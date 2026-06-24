import socket, json
from datetime import datetime, UTC
import config

def send_critical_alert():
    message = {
        "method":    "TRAFFIC_ALERT",
        "deviceId":  "test-injector",
        "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {
            "alert_type":    "congestion",
            "level":         "high",
            "location":      "BR101-km180",
            "action":        "ACTIVATE_SIGNAL",
            "avg_speed_kmh": 18.3,
            "vehicle_count": 28,
        },
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, config.MULTICAST_TTL)
    
    data = json.dumps(message).encode("utf-8")
    sock.sendto(data, (config.MULTICAST_GROUP, config.MULTICAST_PORT))
    sock.close()
    
    print(f"Alerta crítico enviado → group={config.MULTICAST_GROUP}:{config.MULTICAST_PORT}")

if __name__ == "__main__":
    send_critical_alert()