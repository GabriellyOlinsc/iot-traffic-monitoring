# Smart Gateway
SG_HOST = "127.0.0.1"
SG_UDP_PORT = 5005       # Receives VEHICLE_COUNT and SPEED_DATA
SG_TCP_PORT = 5006       # Receives INCIDENT_REPORT

# Cloud Server
CLOUD_HOST = "127.0.0.1"
CLOUD_TCP_PORT = 6000    # Receives DATA_FORWARD

# Multicast
MULTICAST_GROUP = "224.1.1.1"
MULTICAST_PORT  = 5007
MULTICAST_TTL   = 2

# Device IDs
DEVICE_INDUCTIVE_LOOP   = "laco-001"
DEVICE_RADAR            = "radar-001"
DEVICE_INCIDENT_SENSOR  = "sensor-inc-001"
DEVICE_SMART_GATEWAY    = "sg-001"
DEVICE_LED_PANEL        = "led-panel-001"
DEVICE_TRAFFIC_LIGHT    = "traffic-light-001"
DEVICE_CLOUD_SERVER     = "cloud-server-001"

# Simulation intervals 
SENSOR_INTERVAL         = 30     # How often inductive loop sends VEHICLE_COUNT
RADAR_INTERVAL          = 2      # How often radar sends a SPEED_DATA reading
FORWARD_INTERVAL        = 60     # How often SG forwards data to cloud
INCIDENT_INTERVAL       = 45     # How often incident sensor sends a report (simulation)

# Thresholds
VEHICLE_COUNT_THRESHOLD = 20     # Max vehicles for "normal" flow
SPEED_LOW_THRESHOLD     = 30     # km/h — below this = severe congestion
SPEED_MID_THRESHOLD     = 60     # km/h — below this = slow/intense flow

# TCP server 
TCP_MAX_CLIENTS         = 10     # Max queued connections on SG TCP server
TCP_BUFFER_SIZE         = 4096   # Bytes
UDP_BUFFER_SIZE         = 4096