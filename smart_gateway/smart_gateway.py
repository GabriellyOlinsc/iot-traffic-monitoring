# Responsibilities:
#   - UDP Server: receives VEHICLE_COUNT (inductive loop) and SPEED_DATA (radar)
#   - TCP Server: receives INCIDENT_REPORT (incident sensor), threaded per client
#   - Multicast Sender: sends TRAFFIC_ALERT to actuators
#   - TCP Client: forwards DATA_FORWARD to cloud server
#   - Traffic classification logic (count + avg speed → flow level)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Smart Gateway")


def start_udp_server():
    """
    UDP server that receives VEHICLE_COUNT and SPEED_DATA messages.
    Runs in a dedicated thread.
    """
    # TODO: implement
    log.info(f"UDP server listening on {config.SG_HOST}:{config.SG_UDP_PORT}")
    pass


def handle_tcp_client(conn, addr):
    """
    Handles a single TCP client connection in its own thread.
    Receives INCIDENT_REPORT, sends ACK or ERROR back.
    """
    # TODO: implement
    log.info(f"TCP client connected: {addr}")
    pass


def start_tcp_server():
    """
    TCP server that accepts multiple clients, spawning a thread per connection.
    Runs in a dedicated thread.
    """
    # TODO: implement
    log.info(f"TCP server listening on {config.SG_HOST}:{config.SG_TCP_PORT}")
    pass


def send_multicast_alert(payload: dict):
    """
    Sends a TRAFFIC_ALERT message to the multicast group.
    Called when classification detects congestion or an incident is received.
    """
    # TODO: implement
    log.info(f"Sending TRAFFIC_ALERT via multicast → level={payload.get('level')}")
    pass


def forward_to_cloud(events: list):
    """
    TCP client that sends a DATA_FORWARD message to the cloud server.
    Called periodically every FORWARD_INTERVAL seconds.
    """
    # TODO: implement
    log.info(f"Forwarding {len(events)} events to cloud server")
    pass


def classify_traffic(vehicle_count: int, avg_speed: float) -> str | None:
    """
    Applies traffic classification logic based on vehicle count and average speed.

    Returns:
        "high"   → severe congestion or incident
        "medium" → slow/intense flow
        None     → normal flow (no alert)
    """
    # TODO: implement classification table from config thresholds
    pass


def main():
    log.info("Smart Gateway starting...")
    # TODO: start UDP server thread
    # TODO: start TCP server thread
    # TODO: start periodic DATA_FORWARD loop
    pass


if __name__ == "__main__":
    main()