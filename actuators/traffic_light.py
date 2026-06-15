# Responsibilities:
#   - Multicast receiver: joins multicast group and listens for TRAFFIC_ALERT
#   - Reacts to alerts by simulating signal timing adjustments

import sys
import os
import socket
import struct
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger
import config

log = get_logger("Traffic Light")


def join_multicast_group():
    """
    Creates a UDP socket and joins the multicast group.
    Returns the socket ready to receive messages.
    """
    log.info(f"Joining multicast group {config.MULTICAST_GROUP}:{config.MULTICAST_PORT}")
    
    # 1. Cria o socket UDP genérico
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # 2. Permite que o processo se ligue à porta mesmo que ela já esteja em uso por outro atuador (ex: o painel LED)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 3. Vincula o socket à porta multicast configurada pelas meninas
    sock.bind(('', config.MULTICAST_PORT))
    
    # 4. Cria a requisição IGMP estruturada para entrar no grupo IP específico
    mreq = struct.pack("4sl", socket.inet_aton(config.MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    return sock


def handle_alert(message: dict):
    """
    Processes a received TRAFFIC_ALERT message and simulates a response.

    Expected payload fields:
        alert_type: "congestion" | "incident"
        level:      "high" | "medium"
        location:   str
        action:     "ACTIVATE_SIGNAL" | ...
    """
    payload = message.get("payload", {})
    level      = payload.get("level")
    alert_type = payload.get("alert_type")
    location   = payload.get("location")
    action     = payload.get("action")

    log.warning(f"TRAFFIC_ALERT received → type={alert_type}, level={level}, location={location}")
    
    # Implementação da lógica de reação baseada no nível (item 2.1 e 4.6 do PDF)
    if level == "high":
        log.info(f"Ação solicitada: {action}. Mudando semáforo para SINAL AMARELO INTERMITENTE / ATENÇÃO MÁXIMA devido a {alert_type}.")
    elif level == "medium":
        log.info(f"Ajustando temporizador! Reduzindo tempo de sinal verde na via afetada para desafogar o tráfego.")
    else:
        log.info(f"Nível {level} estável. Mantendo o ciclo padrão de operação do semáforo.")


def main():
    log.info("Traffic Light actuator starting...")
    
    # Invoca a função que cria o socket e entra no grupo multicast
    sock = join_multicast_group()
    
    log.info("Loop de escuta multicast iniciado com sucesso.")
    
    # Loop contínuo escutando mensagens do grupo
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode('utf-8'))
            
            # Valida se o método da mensagem recebida é de fato um alerta de tráfego
            if message.get("method") == "TRAFFIC_ALERT":
                handle_alert(message)
                
        except json.JSONDecodeError:
            log.error("Erro ao decodificar a mensagem JSON recebida no grupo Multicast.")
        except Exception as e:
            log.error(f"Erro inesperado no loop principal: {e}")


if __name__ == "__main__":
    main()