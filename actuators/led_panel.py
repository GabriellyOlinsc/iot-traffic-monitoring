# Responsibilities:
#   - Multicast receiver: joins multicast group and listens for TRAFFIC_ALERT
#   - Reacts to alerts by simulating message display on the panel

import sys
import os
import socket
import struct
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logger import get_logger, format_msg
import config

log = get_logger("LED Panel")


def join_multicast_group():
    """
    Creates a UDP socket and joins the multicast group.
    Returns the socket ready to receive messages.
    """
    log.info(f"Joining multicast group {config.MULTICAST_GROUP}:{config.MULTICAST_PORT}")
    
    # Cria o socket UDP genérico para comunicação por datagramas
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Ativa o REUSEADDR para permitir que o painel e o semáforo escutem a mesma porta simultaneamente
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Vincula o socket à porta multicast definida no arquivo config pelas meninas
    sock.bind(('', config.MULTICAST_PORT))
    
    # 4. Estrutura a requisição IGMP para se registrar no grupo IP Multicast
    mreq = struct.pack("4sl", socket.inet_aton(config.MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    return sock


def handle_alert(message: dict):
    """
    Processes a received TRAFFIC_ALERT message and simulates panel display.

    Expected payload fields:
        alert_type: "congestion" | "incident"
        level:      "high" | "medium"
        location:   str
        action:     str
    """
    payload = message.get("payload", {})
    level      = payload.get("level")
    alert_type = payload.get("alert_type")
    location   = payload.get("location")
    avg_speed  = payload.get("avg_speed_kmh", "N/A")

    log.warning(f"TRAFFIC_ALERT received → type={alert_type}, level={level}, location={location}")
    
    # Implementação da lógica visual de exibição de texto baseada no nível do alerta
    print("\n" + "="*55)
    print(f" [PAINEL LED] EXIBIÇÃO EM: {location.upper()} ")
    print("="*55)
    
    if level == "high":
        print(f"  ALERTA CRÍTICO: {alert_type.upper()} DETECTADO! ")
        print(f"  VELOCIDADE MÉDIA: {avg_speed} km/h ")
        print("  --> [ MENSAGEM: TRÂNSITO PARADO. REDUZA A VELOCIDADE! ] ")
    elif level == "medium":
        print(f"  ATENÇÃO: FLUXO LENTO POR {alert_type.upper()} ")
        print(f"  VELOCIDADE MÉDIA: {avg_speed} km/h ")
        print("  --> [ MENSAGEM: TRÁFEGO INTENSO À FRENTE. CUIDADO. ] ")
    else:
        print("  CONDIÇÕES NORMAIS NA VIA ")
        print("  --> [ MENSAGEM: BOA VIAGEM! DADOS DE FLUXO ESTÁVEIS. ] ")
        
    print("="*55 + "\n")


def main():
    log.info("LED Panel actuator starting...")
    
    # Inicializa o socket e se inscreve no grupo multicast
    sock = join_multicast_group()
    
    log.info("Loop de escuta multicast iniciado com sucesso.")
    
    # Loop de recebimento contínuo de pacotes
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode('utf-8'))
            
            if message.get("method") == "TRAFFIC_ALERT":
                handle_alert(message)
                
        except json.JSONDecodeError:
            log.error("Erro ao decodificar pacote JSON recebido no grupo Multicast.")
        except Exception as e:
            log.error(f"Erro inesperado no loop do Painel LED: {e}")


if __name__ == "__main__":
    main()