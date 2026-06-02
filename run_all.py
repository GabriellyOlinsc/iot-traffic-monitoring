
# Starts every device as a subprocess with colored, prefixed output.
# Each device can also be run independently in its own terminal.
#
# Usage:
#   python run_all.py
#   python run_all.py --delay 2   (seconds between each device startup)
# =============================================================================

import subprocess
import sys
import time
import os
import argparse
from logger import get_logger

log = get_logger("Run All")

# --- Device definitions ---
# Order matters: servers must start before clients
DEVICES = [
    {
        "name":   "Cloud Server",
        "script": "cloud_server/cloud_server.py",
        "delay":  1.5,   # seconds to wait after starting before next device
    },
    {
        "name":   "Smart Gateway",
        "script": "smart_gateway/smart_gateway.py",
        "delay":  1.5,
    },
    {
        "name":   "Traffic Light",
        "script": "actuators/traffic_light.py",
        "delay":  0.5,
    },
    {
        "name":   "LED Panel",
        "script": "actuators/led_panel.py",
        "delay":  0.5,
    },
    {
        "name":   "Inductive Loop",
        "script": "sensors/inductive_loop.py",
        "delay":  0.5,
    },
    {
        "name":   "Radar",
        "script": "sensors/radar.py",
        "delay":  0.5,
    },
    {
        "name":   "Incident Sensor",
        "script": "sensors/incident_sensor.py",
        "delay":  0.0,
    },
]


def launch_device(device: dict, base_dir: str) -> subprocess.Popen:
    """Launches a device script as a subprocess."""
    script_path = os.path.join(base_dir, device["script"])
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    log.info(f"Started '{device['name']}' (PID {process.pid})")
    return process


def main():
    parser = argparse.ArgumentParser(description="Launch all IoT devices")
    parser.add_argument("--delay", type=float, default=None,
                        help="Override startup delay between devices (seconds)")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    processes = []

    log.info("=" * 60)
    log.info("  IoT Traffic Monitoring — Starting all devices")
    log.info("=" * 60)

    try:
        for device in DEVICES:
            proc = launch_device(device, base_dir)
            processes.append((device["name"], proc))

            delay = args.delay if args.delay is not None else device["delay"]
            if delay > 0:
                time.sleep(delay)

        log.info(f"All {len(processes)} devices started.")

        # Wait for all processes (runs until interrupted)
        for name, proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        log.warning("Shutdown signal received — stopping all devices...")
        for name, proc in processes:
            proc.terminate()
            log.info(f"Stopped '{name}' (PID {proc.pid})")
        log.info("All devices stopped.")


if __name__ == "__main__":
    main()