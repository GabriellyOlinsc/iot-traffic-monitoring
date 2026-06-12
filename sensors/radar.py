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

log = get_logger("Radar")


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def send_speed_data(speed_kmh: float, location: str):

    message = {
        "method":    "SPEED_DATA",
        "deviceId":  config.DEVICE_RADAR,
        "timestamp": _now(),
        "payload": {
            "speed_kmh": round(speed_kmh, 1),
            "location":  location,
        },
    }

    log.info(f"Sending SPEED_DATA → speed={speed_kmh:.1f} km/h, location={location}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            data = json.dumps(message).encode("utf-8")
            sock.sendto(data, (config.SG_HOST, config.SG_UDP_PORT))
            log.debug(f"SPEED_DATA sent to {config.SG_HOST}:{config.SG_UDP_PORT} ({len(data)} bytes)")

    except OSError as e:
        log.error(f"Network error sending SPEED_DATA: {e}")
    except Exception as e:
        log.error(f"Unexpected error sending SPEED_DATA: {e}")


def simulate_speed() -> float:
    scenario = random.random()

    if scenario < 0.15:             # severe congestion
        base = random.uniform(5.0, 29.0)
    elif scenario < 0.40:           # slow / dense traffic
        base = random.uniform(30.0, 59.0)
    elif scenario < 0.85:           # normal urban flow
        base = random.uniform(60.0, 90.0)
    else:                           # free-flow / highway
        base = random.uniform(91.0, 120.0)

    jitter = random.gauss(0, 3.0)
    speed = max(1.0, base + jitter)

    return speed


def main():
    log.info("Radar sensor starting...")
    log.info(f"Target: {config.SG_HOST}:{config.SG_UDP_PORT} | Interval: {config.RADAR_INTERVAL}s")

    location = "BR-101, KM 207 - Kobrasol"

    while True:
        speed = simulate_speed()
        send_speed_data(speed_kmh=speed, location=location)
        log.debug(f"Next reading in {config.RADAR_INTERVAL}s...")
        time.sleep(config.RADAR_INTERVAL)


if __name__ == "__main__":
    main()