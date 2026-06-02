# Responsibilities:
#   - UDP Client: sends one SPEED_DATA per vehicle to Smart Gateway
#                 every RADAR_INTERVAL seconds (simulating vehicles passing)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Radar")


def send_speed_data(speed_kmh: float, location: str):
    """
    Sends a SPEED_DATA message via UDP to the Smart Gateway.

    Message format:
    {
        "method": "SPEED_DATA",
        "deviceId": "radar-001",
        "timestamp": "<ISO 8601>",
        "payload": {
            "speed_kmh": <float>,
            "location": "<string>"
        }
    }
    """
    # TODO: implement
    log.info(f"Sending SPEED_DATA → speed={speed_kmh} km/h, location={location}")
    pass


def simulate_speed() -> float:
    """
    Simulates a vehicle speed reading for testing purposes.
    Returns a random float representing speed in km/h.
    """
    # TODO: implement (hint: use random.uniform)
    pass


def main():
    log.info("Radar sensor starting...")
    log.info(f"Target: {config.SG_HOST}:{config.SG_UDP_PORT} | Interval: {config.RADAR_INTERVAL}s")
    # TODO: loop — simulate speed, send SPEED_DATA, wait RADAR_INTERVAL
    pass


if __name__ == "__main__":
    main()