# Usage:
#   from logger import get_logger
#   log = get_logger("RADAR")
#   log.info("Sending SPEED_DATA: 72 km/h")
#   log.warning("No response from SG")
#   log.error("Connection refused")

import logging
import sys

# ANSI color codes
_COLORS = {
    "SMART GATEWAY":    "\033[96m",   # Cyan
    "CLOUD SERVER":     "\033[94m",   # Blue
    "INDUCTIVE LOOP":   "\033[92m",   # Green
    "RADAR":            "\033[93m",   # Yellow
    "INCIDENT SENSOR":  "\033[91m",   # Red
    "LED PANEL":        "\033[95m",   # Magenta
    "TRAFFIC LIGHT":    "\033[33m",   # Orange-ish
    "RUN ALL":          "\033[97m",   # White
}

_LEVEL_COLORS = {
    "DEBUG":    "\033[37m",    # Light gray
    "INFO":     "\033[0m",     # Reset (default)
    "WARNING":  "\033[33m",    # Yellow
    "ERROR":    "\033[31m",    # Red
    "CRITICAL": "\033[41m",    # Red background
}

_RESET = "\033[0m"

# Longest device name is "INCIDENT SENSOR" (15 chars) + 2 brackets = 17
# We pad to 17 so every prefix occupies the same visual width
_PREFIX_WIDTH = 17


class _ColoredFormatter(logging.Formatter):
    def __init__(self, device_name: str):
        super().__init__()
        self.device_name  = device_name
        self.device_color = _COLORS.get(device_name.upper(), "\033[0m")

    def format(self, record: logging.LogRecord) -> str:
        level_color = _LEVEL_COLORS.get(record.levelname, "\033[0m")

        timestamp = self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S")

        # Fixed-width prefix: [DEVICE NAME]   ← padded to _PREFIX_WIDTH
        label  = f"[{self.device_name.upper()}]"
        prefix = f"{self.device_color}{label:<{_PREFIX_WIDTH}}{_RESET}"

        level_tag = f"{level_color}{record.levelname:<8}{_RESET}"
        message   = f"{level_color}{record.getMessage()}{_RESET}"
        return f"{timestamp}  {prefix} {level_tag} {message}"


def get_logger(device_name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    Returns a logger prefixed and colored by device name.

    Args:
        device_name: Human-readable name shown in every log line.
                     Should match one of the keys in _COLORS for best results.
        level:       Logging level (default: DEBUG).
    """
    logger = logging.getLogger(device_name)

    # Avoid duplicate handlers if get_logger is called more than once
    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(_ColoredFormatter(device_name))

    logger.addHandler(handler)
    logger.propagate = False

    return logger

# Quick demo — preview log
if __name__ == "__main__":
    devices = [
        "Smart Gateway",
        "Cloud Server",
        "Inductive Loop",
        "Radar",
        "Incident Sensor",
        "LED Panel",
        "Traffic Light",
        "Run All",
    ]

    print("\n--- Logger color preview ---\n")
    for name in devices:
        log = get_logger(name)
        log.debug(f"DEBUG message from {name}")
        log.info(f"INFO message from {name}")
        log.warning(f"WARNING message from {name}")
        log.error(f"ERROR message from {name}")
        print()


def format_msg(method: str, payload: dict) -> str:
    """
    Formats a log message in the standard protocol style:
        METHOD → {"key": value, ...}

    Usage:
        from logger import get_logger, format_msg

        log.debug(format_msg("SPEED_DATA", {"speed_kmh": 26.5, "location": "BR-101"}))
        # → SPEED_DATA → {"speed_kmh": 26.5, "location": "BR-101"}

        log.info(format_msg("VEHICLE_COUNT", {"count": 12, "interval": 30}))
        # → VEHICLE_COUNT → {"count": 12, "interval": 30}

        log.warning(format_msg("TRAFFIC_ALERT", {"level": "high", "alert_type": "incident"}))
        # → TRAFFIC_ALERT → {"level": "high", "alert_type": "incident"}
    """
    import json
    payload_str = json.dumps(payload, ensure_ascii=False)
    return f"{method} → {payload_str}"