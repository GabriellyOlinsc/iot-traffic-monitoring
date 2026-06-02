# Responsibilities:
#   - TCP Server: receives DATA_FORWARD messages from Smart Gateway
#   - Sends ACK or ERROR response
#   - Stores and displays received traffic history

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Cloud Server")


def handle_client(conn, addr):
    """
    Handles a single TCP connection from the Smart Gateway.
    Receives DATA_FORWARD, stores events, sends ACK or ERROR.
    """
    # TODO: implement
    log.info(f"Connection received from: {addr}")
    pass


def start_tcp_server():
    """
    TCP server that listens for DATA_FORWARD messages from the Smart Gateway.
    Spawns a thread per connection.
    """
    # TODO: implement
    log.info(f"Cloud server TCP listening on {config.CLOUD_HOST}:{config.CLOUD_TCP_PORT}")
    pass


def store_events(events: list, period_s: int):
    """
    Stores received events and logs a summary.
    Could write to a file or in-memory list for demonstration.
    """
    # TODO: implement
    log.info(f"Storing {len(events)} events (period={period_s}s)")
    pass


def main():
    log.info("Cloud Server starting...")
    # TODO: start TCP server
    pass


if __name__ == "__main__":
    main()