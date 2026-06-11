import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import socket
import json
import threading
from datetime import datetime, UTC

from logger import get_logger
import config

log = get_logger("Cloud Server")

_lock          = threading.Lock()
_history       = []   # all received event batches


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_message(method: str, payload: dict) -> bytes:
    msg = {
        "method":    method,
        "deviceId":  config.DEVICE_CLOUD_SERVER,
        "timestamp": _now(),
        "payload":   payload,
    }
    return json.dumps(msg).encode("utf-8")


def _send_ack(conn: socket.socket, ref_method: str):
    response = _build_message("ACK", {
        "status":     "received",
        "ref_method": ref_method,
    })
    conn.sendall(response)
    log.info(f"ACK sent → ref_method={ref_method}")


def _send_error(conn: socket.socket, ref_method: str, error_code: str, description: str):
    response = _build_message("ERROR", {
        "ref_method":  ref_method,
        "error_code":  error_code,
        "description": description,
    })
    conn.sendall(response)
    log.warning(f"ERROR sent → code={error_code}, description={description}")


def store_events(events: list, period_s: int):
    """
    Stores received events and logs a summary.
    """
    entry = {
        "received_at": _now(),
        "period_s":    period_s,
        "event_count": len(events),
        "events":      events,
    }
    with _lock:
        _history.append(entry)

    log.info(f"Storing {len(events)} events (period={period_s}s)")

    for ev in events:
        method = ev.get("method", "UNKNOWN")
        data   = ev.get("data", {})
        if method == "VEHICLE_COUNT":
            log.debug(f"  └─ VEHICLE_COUNT: count={data.get('count')}, location={data.get('location')}")
        elif method == "SPEED_DATA":
            log.debug(f"  └─ SPEED_DATA: speed={data.get('speed_kmh')} km/h, location={data.get('location')}")
        elif method == "INCIDENT_REPORT":
            log.debug(f"  └─ INCIDENT_REPORT: type={data.get('type')}, severity={data.get('severity')}")
        else:
            log.debug(f"  └─ {method}: {data}")


def handle_client(conn: socket.socket, addr):
    """
    Handles a single TCP connection from the Smart Gateway
    Receives DATA_FORWARD, stores events, sends ACK or ERROR
    """
    log.info(f"Connection received from: {addr}")
    try:
        data = conn.recv(config.TCP_BUFFER_SIZE)
        if not data:
            log.warning(f"Empty message from {addr}")
            return

        try:
            message = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            _send_error(conn, "UNKNOWN", "INVALID_PAYLOAD", "JSON malformado")
            return

        method   = message.get("method")
        payload  = message.get("payload", {})
        deviceId = message.get("deviceId", "unknown")

        log.debug(f"Received → method={method}, from={deviceId}")

        if method != "DATA_FORWARD":
            _send_error(
                conn, method or "UNKNOWN",
                "INVALID_METHOD",
                f"Método não suportado: {method}",
            )
            return

        events   = payload.get("events")
        period_s = payload.get("period_s")

        if events is None or period_s is None:
            _send_error(conn, method, "INVALID_PAYLOAD", "Campos obrigatórios ausentes: events, period_s")
            return

        if not isinstance(events, list):
            _send_error(conn, method, "INVALID_PAYLOAD", "O campo 'events' deve ser uma lista")
            return

        store_events(events, period_s)
        _send_ack(conn, method)

        with _lock:
            total_batches = len(_history)
            total_events  = sum(e["event_count"] for e in _history)
        log.info(f"History: {total_batches} batch(es), {total_events} total event(s)")

    except Exception as e:
        log.error(f"Client handler error ({addr}): {e}")
    finally:
        conn.close()
        log.debug(f"Connection closed: {addr}")


def start_tcp_server():
    """
    TCP server that listens for DATA_FORWARD messages from the Smart Gateway
    Spawns a thread per connection
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config.CLOUD_HOST, config.CLOUD_TCP_PORT))
    sock.listen(5)
    log.info(f"Cloud server TCP listening on {config.CLOUD_HOST}:{config.CLOUD_TCP_PORT}")

    while True:
        try:
            conn, addr = sock.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            client_thread.start()
        except Exception as e:
            log.error(f"TCP server error: {e}")


def main():
    log.info("Cloud Server starting...")
    try:
        start_tcp_server()
    except KeyboardInterrupt:
        log.info("Cloud Server shutting down...")


if __name__ == "__main__":
    main()