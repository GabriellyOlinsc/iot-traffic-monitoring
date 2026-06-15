# IoT Traffic Monitoring

Aplicação distribuída de monitoramento de fluxo de veículos em vias, desenvolvida com Python e API de Sockets.

---

## Estrutura do projeto

```
projeto/
├── config.py                        # Configurações compartilhadas (portas, IPs, limiares)
├── logger.py                        # Logger colorido por dispositivo
├── run_all.py                       # Sobe todos os dispositivos de uma vez
├── smart_gateway/
│   └── smart_gateway.py             # UDP Server, TCP Server, Multicast Sender, TCP Client, classificação
├── sensors/
│   ├── inductive_loop.py            # UDP Client
│   ├── radar.py                     # UDP Client
│   └── incident_sensor.py           # TCP Client
├── actuators/
│   ├── traffic_light.py             # Multicast Receiver
│   └── led_panel.py                 # Multicast Receiver 
└── cloud_server/
    └── cloud_server.py              # TCP Server
```

---

## Requisitos

- Python 3.10 ou superior
- Sem dependências externas — apenas biblioteca padrão do Python

---

## Como rodar

```bash
python run_all.py
```

Abre 4 janelas de terminal, uma por camada da arquitetura.
Para parar: feche cada janela individualmente com `Ctrl+C`.

### Comandos Alternativos:

```bash
python run_all.py --delay 2   //Delay para inicialização de dispositivos
```

---

### Opção 2 — Um terminal por dispositivo (recomendado para desenvolvimento)

Abra 7 terminais e rode **nessa ordem**:

**Terminal 1 — Servidor na nuvem**

```bash
python cloud_server/cloud_server.py
```

**Terminal 2 — Smart Gateway**

```bash
python smart_gateway/smart_gateway.py
```

**Terminal 3 — Semáforo inteligente**

```bash
python actuators/traffic_light.py
```

**Terminal 4 — Painel LED**

```bash
python actuators/led_panel.py
```

**Terminal 5 — Laço indutivo**

```bash
python sensors/inductive_loop.py
```

**Terminal 6 — Radar**

```bash
python sensors/radar.py
```

**Terminal 7 — Sensor de incidente**

```bash
python sensors/incident_sensor.py
```

> A ordem importa. O Cloud Server e o Smart Gateway precisam estar de pé antes dos sensores e atuadores.

---

## Sockets utilizados

| Dispositivo      | Socket             | Protocolo | Função                                             |
| ---------------- | ------------------ | --------- | -------------------------------------------------- |
| Laço Indutivo    | UDP Client         | UDP       | Envia `VEHICLE_COUNT`                              |
| Radar            | UDP Client         | UDP       | Envia `SPEED_DATA`                                 |
| Sensor Incidente | TCP Client         | TCP       | Envia `INCIDENT_REPORT`                            |
| Smart Gateway    | UDP Server         | UDP       | Recebe dados dos sensores UDP                      |
| Smart Gateway    | TCP Server         | TCP       | Recebe `INCIDENT_REPORT`, multi-cliente (threaded) |
| Smart Gateway    | Multicast Sender   | Multicast | Envia `TRAFFIC_ALERT`                              |
| Smart Gateway    | TCP Client         | TCP       | Envia `DATA_FORWARD` à nuvem                       |
| Semáforo         | Multicast Receiver | Multicast | Recebe `TRAFFIC_ALERT`                             |
| Painel LED       | Multicast Receiver | Multicast | Recebe `TRAFFIC_ALERT`                             |
| Servidor Nuvem   | TCP Server         | TCP       | Recebe `DATA_FORWARD`                              |

---

## Configuração

Todas as configurações estão centralizadas em `config.py`:

```python
# Portas
SG_UDP_PORT   = 5005   # Smart Gateway — recebe UDP
SG_TCP_PORT   = 5006   # Smart Gateway — recebe TCP
CLOUD_TCP_PORT = 6000  # Servidor na nuvem

# Multicast
MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT  = 5007

# Limiares de classificação de tráfego
VEHICLE_COUNT_THRESHOLD = 20    # veículos
SPEED_LOW_THRESHOLD     = 30    # km/h — abaixo: congestionamento severo
SPEED_MID_THRESHOLD     = 60    # km/h — abaixo: fluxo lento

# Intervalos de simulação
SENSOR_INTERVAL   = 30   # segundos entre VEHICLE_COUNT
RADAR_INTERVAL    = 2    # segundos entre SPEED_DATA
FORWARD_INTERVAL  = 60   # segundos entre DATA_FORWARD
INCIDENT_INTERVAL = 45   # segundos entre INCIDENT_REPORT
```

---

## Logs

Cada dispositivo tem uma cor fixa no terminal.

Níveis de log:

| Nível   | Cor      | Quando usar                            |
| ------- | -------- | -------------------------------------- |
| DEBUG   | Cinza    | Detalhes internos                      |
| INFO    | Padrão   | Eventos normais de operação            |
| WARNING | Amarelo  | Alertas recebidos / situações anômalas |
| ERROR   | Vermelho | Falhas de conexão ou processamento     |

---

## Classificação de tráfego

A lógica de classificação é aplicada pelo Smart Gateway a cada intervalo:

| Situação         | Contagem      | Velocidade média | Nível      |
| ---------------- | ------------- | ---------------- | ---------- |
| Acidente         | —             | —                | `high`     |
| Congestionamento | > 20 veículos | < 30 km/h        | `high`     |
| Fluxo lento      | > 20 veículos | 30–60 km/h       | `medium`   |
| Fluxo normal     | ≤ 20 veículos | ≥ 60 km/h        | sem alerta |
