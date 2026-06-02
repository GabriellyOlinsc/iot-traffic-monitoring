# Responsibilities:
#   - Multicast receiver: joins multicast group and listens for TRAFFIC_ALERT
#   - Reacts to alerts by simulating signal timing adjustments

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Traffic Light")


def join_multicast_group():
    """
    Creates a UDP socket and joins the multicast group.
    Returns the socket ready to receive messages.
    """
    # TODO: implement
    log.info(f"Joining multicast group {config.MULTICAST_GROUP}:{config.MULTICAST_PORT}")
    pass


def handle_alert(message: dict):
    """
    Processes a received TRAFFIC_ALERT message and simulates a response.

    Expected payload fields:
        alert_type: "congestion" | "incident"
        level:      "high" | "medium"
        location:   str
        action:     "ACTIVATE_SIGNAL" | ...
    """
    level      = message.get("payload", {}).get("level")
    alert_type = message.get("payload", {}).get("alert_type")
    location   = message.get("payload", {}).get("location")

    # TODO: implement reaction logic based on level
    log.warning(f"TRAFFIC_ALERT received → type={alert_type}, level={level}, location={location}")
    pass


def main():
    log.info("Traffic Light actuator starting...")
    # TODO: join multicast group, loop listening for TRAFFIC_ALERT
    pass


if __name__ == "__main__":
    main()