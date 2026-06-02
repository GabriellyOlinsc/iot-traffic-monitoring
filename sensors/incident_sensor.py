# Responsibilities:
#   - TCP Client: sends INCIDENT_REPORT to Smart Gateway
#   - Waits for ACK or ERROR response after each message
# =============================================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Incident Sensor")


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
    # TODO: implement (connect, send, wait for ACK/ERROR, close)
    log.info(f"Sending INCIDENT_REPORT → type={incident_type}, severity={severity}, location={location}")
    pass


def simulate_incident() -> dict:
    """
    Simulates an incident detection for testing purposes.
    Returns a dict with type, severity and location.
    """
    # TODO: implement
    pass


def main():
    log.info("Incident Sensor starting...")
    log.info(f"Target: {config.SG_HOST}:{config.SG_TCP_PORT} | Interval: {config.INCIDENT_INTERVAL}s")
    # TODO: loop — simulate incident, send INCIDENT_REPORT, wait INCIDENT_INTERVAL
    pass


if __name__ == "__main__":
    main()