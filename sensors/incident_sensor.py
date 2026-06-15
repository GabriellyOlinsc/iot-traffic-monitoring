import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import socket
import json
import time
import random
from datetime import datetime, UTC

from logger import get_logger
import config

log = get_logger("Incident Sensor")


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def send_incident_report(incident_type: str, severity: str, location: str):
    """
    Sends an INCIDENT_REPORT message via TCP to the Smart Gateway.
    Waits for an ACK or ERROR response.

    Message format:
    {
        "method": "INCIDENT_REPORT",
        "deviceId": "sensor-inc-001",
        "timestamp": "<ISO 8601>",
        "payload": {
            "type": "<string>",       e.g. "accident", "breakdown"
            "severity": "<string>",   e.g. "high", "medium", "low"
            "location": "<string>"
        }
    }
    """
    message = {
        "method":    "INCIDENT_REPORT",
        "deviceId":  config.DEVICE_INCIDENT_SENSOR,
        "timestamp": _now(),
        "payload": {
            "type":     incident_type,
            "severity": severity,
            "location": location,
        },
    }

    log.info(f"Sending INCIDENT_REPORT → type={incident_type}, severity={severity}, location={location}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((config.SG_HOST, config.SG_TCP_PORT))
        sock.sendall(json.dumps(message).encode("utf-8"))
        
        response_data = sock.recv(config.TCP_BUFFER_SIZE)
        response = json.loads(response_data.decode("utf-8"))
        method  = response.get("method")
        payload = response.get("payload", {})

        if method == "ACK":
            log.info(f"ACK received → status={payload.get('status')}, ref={payload.get('ref_method')}")
        elif method == "ERROR":
            log.error(f"ERROR received → code={payload.get('error_code')}")

    except ConnectionRefusedError:
        log.error(f"Connection refused — Smart Gateway not available")
    except Exception as e:
        log.error(f"Error sending INCIDENT_REPORT: {e}")
    finally:
        sock.close()

def simulate_incident() -> dict:
    """
    Simulates an incident detection for testing purposes.
    Returns a dict with type, severity and location.
    """
    incident_types = ["accident", "breakdown", "obstacle", "flooding", "roadwork"]
    severities     = ["high", "medium", "low"]
    locations      = [
        "Av. Beira-Mar Norte, KM 3",
        "SC-401, KM 12",
        "BR-101, KM 207 - Kobrasol",
        "BR-101, KM 210 - Distrito Industrial",
    ]

    return {
        "type":     random.choice(incident_types),
        "severity": random.choice(severities),
        "location": random.choice(locations),
    }


def main():
    log.info("Incident Sensor starting...")
    log.info(f"Target: {config.SG_HOST}:{config.SG_TCP_PORT} | Interval: {config.INCIDENT_INTERVAL}s")

    while True:
        incident = simulate_incident()
        send_incident_report(
            incident_type=incident["type"],
            severity=incident["severity"],
            location=incident["location"],
        )
        time.sleep(config.INCIDENT_INTERVAL)


if __name__ == "__main__":
    main()