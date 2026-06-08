# Responsibilities:
#   - UDP Server: receives VEHICLE_COUNT (inductive loop) and SPEED_DATA (radar)
#   - TCP Server: receives INCIDENT_REPORT (incident sensor), threaded per client
#   - Multicast Sender: sends TRAFFIC_ALERT to actuators
#   - TCP Client: forwards DATA_FORWARD to cloud server
#   - Traffic classification logic (count + avg speed → flow level)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import socket
import json
import threading
import time
from datetime import datetime

from logger import get_logger
import config

log = get_logger("Smart Gateway")

_lock            = threading.Lock()
_speed_readings  = []   # raw km/h values received in current window
_vehicle_count   = 0    # latest count received from inductive loop
_events_buffer   = []   # all events received, flushed on DATA_FORWARD
 
def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _build_message(method: str, payload: dict) -> bytes:
    msg = {
        "method":    method,
        "deviceId":  config.DEVICE_SMART_GATEWAY,
        "timestamp": _now(),
        "payload":   payload,
    }
    return json.dumps(msg).encode("utf-8")

# UDP SERVER ------------------------------------------------------------

def _handle_vehicle_count(payload: dict):
    global _vehicle_count
    count    = payload.get("count", 0)
    location = payload.get("location", "unknown")
    interval = payload.get("interval", config.SENSOR_INTERVAL)
    with _lock:
        _vehicle_count = count
        _events_buffer.append({"method": "VEHICLE_COUNT", "data": payload})
    log.info(f"VEHICLE_COUNT → count={count}, interval={interval}s, location={location}")

 
def _handle_speed_data(payload: dict):
    speed    = payload.get("speed_kmh", 0)
    location = payload.get("location", "unknown")
    with _lock:
        _speed_readings.append(speed)
        _events_buffer.append({"method": "SPEED_DATA", "data": payload})
    log.debug(f"SPEED_DATA    → speed={speed} km/h, location={location}") 

  
def start_udp_server():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config.SG_HOST, config.SG_UDP_PORT))
    log.info(f"UDP server listening on {config.SG_HOST}:{config.SG_UDP_PORT}")
 
    while True:
        try:
            data, addr = sock.recvfrom(config.UDP_BUFFER_SIZE)
            message = json.loads(data.decode("utf-8"))
            method  = message.get("method")
            payload = message.get("payload", {})
 
            if method == "VEHICLE_COUNT":
                _handle_vehicle_count(payload)
            elif method == "SPEED_DATA":
                _handle_speed_data(payload)
            else:
                log.warning(f"UDP: unknown method '{method}' from {addr}")
 
        except json.JSONDecodeError:
            log.error(f"UDP: invalid JSON received from {addr}")
        except Exception as e:
            log.error(f"UDP server error: {e}")
 
 
# TCP SERVER ------------------------------------------------------------

def _send_ack(conn, ref_method: str):
    response = _build_message("ACK", {
        "status":     "received",
        "ref_method": ref_method,
    })
    conn.sendall(response)
    log.info(f"ACK sent → ref_method={ref_method}")


def _send_error(conn, ref_method: str, error_code: str, description: str):
    response = _build_message("ERROR", {
        "ref_method":  ref_method,
        "error_code":  error_code,
        "description": description,
    })
    conn.sendall(response)
    log.warning(f"ERROR sent → code={error_code}, description={description}")


def _handle_incident_report(payload: dict) -> tuple[bool, str, str]:
    """
    Validates and processes an INCIDENT_REPORT payload.
    Returns (ok, error_code, description).
    """
    required = ["type", "severity", "location"]
    for field in required:
        if field not in payload:
            return False, "INVALID_PAYLOAD", f"Campo obrigatório ausente: {field}"
 
    incident_type = payload["type"]
    severity      = payload["severity"]
    location      = payload["location"]
 
    with _lock:
        _events_buffer.append({"method": "INCIDENT_REPORT", "data": payload})
 
    log.warning(f"INCIDENT_REPORT → type={incident_type}, severity={severity}, location={location}")
    return True, "", ""


def handle_tcp_client(conn: socket.socket, addr):
    """
    Handles a single TCP client connection in its own thread.
    Receives INCIDENT_REPORT, sends ACK or ERROR back.
    """
    log.info(f"TCP client connected: {addr}")
    try:
        data = conn.recv(config.TCP_BUFFER_SIZE)
        if not data:
            log.warning(f"TCP: empty message from {addr}")
            return
 
        try:
            message = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            _send_error(conn, "UNKNOWN", "INVALID_PAYLOAD", "JSON malformado")
            return
 
        method   = message.get("method")
        payload  = message.get("payload", {})
        deviceId = message.get("deviceId", "unknown")
 
        log.debug(f"TCP received → method={method}, from={deviceId} {addr}")
 
        if method == "INCIDENT_REPORT":
            ok, error_code, description = _handle_incident_report(payload)
            if ok:
                _send_ack(conn, method)

                send_multicast_alert({
                    "alert_type": "incident",
                    "level":      "high",
                    "location":   payload.get("location", "unknown"),
                    "action":     "ACTIVATE_SIGNAL",
                })
            else:
                _send_error(conn, method, error_code, description)
        else:
            _send_error(conn, method or "UNKNOWN", "INVALID_PAYLOAD",
                        f"Método não suportado via TCP: {method}")
 
    except Exception as e:
        log.error(f"TCP client handler error ({addr}): {e}")
    finally:
        conn.close()
        log.debug(f"TCP connection closed: {addr}")
 
 
def start_tcp_server():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config.SG_HOST, config.SG_TCP_PORT))
    sock.listen(config.TCP_MAX_CLIENTS)
    log.info(f"TCP server listening on {config.SG_HOST}:{config.SG_TCP_PORT} (max {config.TCP_MAX_CLIENTS} clients)")
 
    while True:
        try:
            conn, addr = sock.accept()
            client_thread = threading.Thread(
                target=handle_tcp_client,
                args=(conn, addr),
                daemon=True,
            )
            client_thread.start()
            log.debug(f"TCP thread spawned for {addr} (active threads: {threading.active_count()})")
        except Exception as e:
            log.error(f"TCP server error: {e}")
 

# TRAFFIC CLASSIFICATION
def classify_traffic(vehicle_count: int, avg_speed: float) -> str | None:
    """
    Traffic classification logic based on vehicle count and average speed.
 
    | Situation          | Count                         | Avg speed              | Level    |
    |--------------------|-------------------------------|------------------------|----------|
    | Severe congestion  | >  VEHICLE_COUNT_THRESHOLD    | <  SPEED_LOW_THRESHOLD | "high"   |
    | Slow/intense flow  | >  VEHICLE_COUNT_THRESHOLD    | <  SPEED_MID_THRESHOLD | "medium" |
    | Normal flow        | <= VEHICLE_COUNT_THRESHOLD    | >= SPEED_MID_THRESHOLD | None     |
 
    """
    if vehicle_count > config.VEHICLE_COUNT_THRESHOLD:
        if avg_speed < config.SPEED_LOW_THRESHOLD:
            return "high"
        elif avg_speed < config.SPEED_MID_THRESHOLD:
            return "medium"
    return None
 

def _classification_loop():
    """
    Runs every SENSOR_INTERVAL seconds.
    Reads accumulated speed readings and vehicle count, classifies traffic,
    and triggers a multicast alert if needed.
    """
    while True:
        time.sleep(config.SENSOR_INTERVAL)
 
        with _lock:
            count    = _vehicle_count
            readings = list(_speed_readings)
            _speed_readings.clear()   # reset for next window
 
        if not readings:
            log.info("Classification → no speed data received in this window, skipping")
            continue
 
        avg_speed = sum(readings) / len(readings)
        level     = classify_traffic(count, avg_speed)
 
        log.info(
            f"Classification → count={count}, "
            f"avg_speed={avg_speed:.1f} km/h, "
            f"readings={len(readings)}, "
            f"level={level or 'normal (no alert)'}"
        )
 
        if level:
            send_multicast_alert({
                "alert_type":    "congestion",
                "level":         level,
                "location":      "BR101-km180",
                "action":        "ACTIVATE_SIGNAL",
                "avg_speed_kmh": round(avg_speed, 1),
                "vehicle_count": count,
            })


# MULTICAST 

def send_multicast_alert(payload: dict):
    """
    Sends a TRAFFIC_ALERT message to the multicast group.
    All devices subscribed to MULTICAST_GROUP:MULTICAST_PORT receive it simultaneously.
    """
    message = _build_message("TRAFFIC_ALERT", payload)
 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, config.MULTICAST_TTL)
 
    try:
        sock.sendto(message, (config.MULTICAST_GROUP, config.MULTICAST_PORT))
        log.info(
            f"TRAFFIC_ALERT multicast sent → "
            f"type={payload.get('alert_type')}, "
            f"level={payload.get('level')}, "
            f"location={payload.get('location')}"
        )
    except Exception as e:
        log.error(f"Multicast send error: {e}")
    finally:
        sock.close()

# TCP Client → Cloud

def forward_to_cloud(events: list):
    """
    TCP client that sends a DATA_FORWARD message to the cloud server.
    Called periodically every FORWARD_INTERVAL seconds.
    """
    # TODO: implement
    log.info(f"Forwarding {len(events)} events to cloud server")
    pass


def main():
    log.info("Smart Gateway starting...")

    udp_thread = threading.Thread(target=start_udp_server, daemon=True)
    udp_thread.start()
 
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()
    
    classification_thread = threading.Thread(target=_classification_loop, daemon=True)
    classification_thread.start()

    log.info("All servers running. Waiting for messages...")

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        log.info("Shutting down Smart Gateway...")

if __name__ == "__main__":
    main()