# Responsibilities:
#   - UDP Client: sends VEHICLE_COUNT to Smart Gateway every SENSOR_INTERVAL seconds

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Inductive Loop")


def send_vehicle_count(count: int, location: str):
    """
    Sends a VEHICLE_COUNT message via UDP to the Smart Gateway.

    Message format:
    {
        "method": "VEHICLE_COUNT",
        "deviceId": "laco-001",
        "timestamp": "<ISO 8601>",
        "payload": {
            "count": <int>,
            "interval": 30,
            "location": "<string>"
        }
    }
    """
    # TODO: implement
    log.info(f"Sending VEHICLE_COUNT → count={count}, location={location}")
    pass


def simulate_vehicle_count() -> int:
    """
    Simulates a vehicle count reading for testing purposes.
    Returns a random integer representing vehicles in the last interval.
    """
    # TODO: implement (hint: use random.randint)
    pass


def main():
    log.info("Inductive Loop sensor starting...")
    log.info(f"Target: {config.SG_HOST}:{config.SG_UDP_PORT} | Interval: {config.SENSOR_INTERVAL}s")
    # TODO: loop — simulate count, send VEHICLE_COUNT, wait SENSOR_INTERVAL
    pass


if __name__ == "__main__":
    main()