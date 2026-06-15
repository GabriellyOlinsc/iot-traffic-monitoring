# =============================================================================
# run_all.py — Launch all devices in 4 terminal windows
# =============================================================================
# Opens one terminal per layer of the architecture:
#   - Cloud Server
#   - Smart Gateway
#   - Actuators  (Traffic Light + LED Panel)
#   - Sensors    (Inductive Loop + Radar + Incident Sensor)
#
# Usage:
#   python run_all.py
#   python run_all.py --delay 2
#   python run_all.py --split     (one window per script)
# =============================================================================

import subprocess
import sys
import time
import os
import argparse
import tempfile
from logger import get_logger

log = get_logger("Run All")

GROUPS = [
    {
        "name":    "Cloud Server",
        "scripts": ["cloud_server/cloud_server.py"],
        "delay":   2.0,
    },
    {
        "name":    "Smart Gateway",
        "scripts": ["smart_gateway/smart_gateway.py"],
        "delay":   2.0,
    },
    {
        "name":    "Actuators",
        "scripts": ["actuators/traffic_light.py", "actuators/led_panel.py"],
        "delay":   1.0,
    },
    {
        "name":    "Sensors",
        "scripts": ["sensors/inductive_loop.py", "sensors/radar.py", "sensors/incident_sensor.py"],
        "delay":   0.0,
    },
]

_temp_files = []


def _create_launcher(group: dict, base_dir: str) -> str:
    """
    Writes a temporary Python launcher script for the group.
    Returns the path to the temp file.
    """
    scripts = [os.path.join(base_dir, s) for s in group["scripts"]]

    lines = [
        "import subprocess, sys, time",
        f"PYTHON = {sys.executable!r}",
        f"SCRIPTS = {scripts!r}",
        f"NAME = {group['name']!r}",
        "print('=' * 55)",
        "print(f'  [{NAME}]')",
        "print('=' * 55)",
        "procs = [subprocess.Popen([PYTHON, s]) for s in SCRIPTS]",
        "print(f'  {len(procs)} process(es) started. Press Ctrl+C to stop.')",
        "print()",
        "try:",
        "    while all(p.poll() is None for p in procs):",
        "        time.sleep(1)",
        "except KeyboardInterrupt:",
        "    print('\\nStopping...')",
        "    [p.terminate() for p in procs]",
        "    print('Done.')",
    ]

    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        prefix="iot_",
        delete=False,
        dir=base_dir,       # same dir as project — no space issues
    )
    tmp.write("\n".join(lines))
    tmp.close()
    _temp_files.append(tmp.name)
    return tmp.name


def _open_window(title: str, launcher: str, base_dir: str):
    """Opens a new cmd window running the launcher script."""
    subprocess.Popen(
        ["cmd", "/k", sys.executable, launcher],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=base_dir,
    )


def launch_group(group: dict, base_dir: str, split: bool):
    if split:
        for script in group["scripts"]:
            path  = os.path.join(base_dir, script)
            title = f"[{group['name']}] {os.path.basename(script)}"
            subprocess.Popen(
                ["cmd", "/k", sys.executable, path],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=base_dir,
            )
            log.info(f"Opened window → {title}")
    else:
        launcher = _create_launcher(group, base_dir)
        _open_window(group["name"], launcher, base_dir)
        log.info(f"Opened window → [{group['name']}]  ({', '.join(os.path.basename(s) for s in group['scripts'])})")


def main():
    parser = argparse.ArgumentParser(description="Launch all IoT devices in terminal windows")
    parser.add_argument("--delay", type=float, default=None)
    parser.add_argument("--split", action="store_true",
                        help="One window per script instead of one per group")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    log.info("=" * 60)
    log.info("  IoT Traffic Monitoring — Starting all devices")
    log.info("=" * 60)
    if not args.split:
        log.info("  1. Cloud Server")
        log.info("  2. Smart Gateway")
        log.info("  3. Actuators  → Traffic Light + LED Panel")
        log.info("  4. Sensors    → Inductive Loop + Radar + Incident Sensor")
        log.info("=" * 60)

    for group in GROUPS:
        launch_group(group, base_dir, args.split)
        delay = args.delay if args.delay is not None else group["delay"]
        if delay > 0:
            log.info(f"Waiting {delay}s...")
            time.sleep(delay)

    total = sum(len(g["scripts"]) for g in GROUPS)
    log.info(f"All {total} devices started. Close each window to stop.")


if __name__ == "__main__":
    main()