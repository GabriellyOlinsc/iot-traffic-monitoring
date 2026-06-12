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

log = get_logger("Inductive Loop")


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def send_vehicle_count(count: int, location: str):
    message = {
        "method":    "VEHICLE_COUNT",
        "deviceId":  config.DEVICE_INDUCTIVE_LOOP,
        "timestamp": _now(),
        "payload": {
            "count":    count,
            "interval": config.SENSOR_INTERVAL,
            "location": location,
        },
    }

    log.info(f"Sending VEHICLE_COUNT → count={count}, location={location}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            data = json.dumps(message).encode("utf-8")
            sock.sendto(data, (config.SG_HOST, config.SG_UDP_PORT))
            log.debug(f"VEHICLE_COUNT sent to {config.SG_HOST}:{config.SG_UDP_PORT} ({len(data)} bytes)")

    except OSError as e:
        log.error(f"Network error sending VEHICLE_COUNT: {e}")
    except Exception as e:
        log.error(f"Unexpected error sending VEHICLE_COUNT: {e}")


def simulate_vehicle_count() -> int:
    scenario = random.random()

    if scenario < 0.40:
        return random.randint(1, 10)
    elif scenario < 0.80:
        return random.randint(11, 25)
    else:
        return random.randint(26, 45)

def main():
    log.info("Inductive Loop sensor starting...")
    log.info(f"Target: {config.SG_HOST}:{config.SG_UDP_PORT} | Interval: {config.SENSOR_INTERVAL}s")

    location = "BR-101, KM 207 - Kobrasol"

    while True:
        count = simulate_vehicle_count()
        send_vehicle_count(count=count, location=location)
        log.debug(f"Next reading in {config.SENSOR_INTERVAL}s...")
        time.sleep(config.SENSOR_INTERVAL)


if __name__ == "__main__":
    main()