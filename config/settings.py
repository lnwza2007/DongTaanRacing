
# CAN Interface Configuration
CAN_CHANNEL = "can0"
CAN_BITRATE = 1_000_000  # 1 Mbps for MoTeC

# Logger Configuration
SAMPLE_HZ = 20           # Data collection rate (20 Hz)
SAMPLE_INTERVAL = 1.0 / SAMPLE_HZ
STALE_TIMEOUT = 1.0     # Mark data NaN if no update for > 1 second

# Logging Files
LOG_DIR = "./logs"
MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB
FLUSH_EVERY_N = 20

# MQTT Settings
MQTT_USE_HIVEMQ = True
MQTT_BROKER_HIVEMQ = "2898b29c070f4985b025bbc1d2e1d216.s1.eu.hivemq.cloud"
MQTT_PORT_HIVEMQ = 8883
MQTT_USER_HIVEMQ = "dongtaan_vcu"
MQTT_PASS_HIVEMQ = "Frank2007"


MQTT_BROKER_LOCAL = "172.20.10.3"
MQTT_PORT_LOCAL = 1883

MQTT_TOPIC = "balone2/telemetry/motec"
MQTT_PUBLISH_HZ = 20
MQTT_QUEUE_SIZE = 100
