#ifndef CONFIG_H
#define CONFIG_H

// WiFi Settings
#define WIFI_SSID "DongtaanWifi"
#define WIFI_PASSWORD "Dongtaan"


// MQTT Settings (HiveMQ Cloud TLS)
#define MQTT_BROKER "2898b29c070f4985b025bbc1d2e1d216.s1.eu.hivemq.cloud"
#define MQTT_PORT 8883
#define MQTT_USER "dongtaan_vcu"
#define MQTT_PASS "Frank2007"
#define MQTT_TOPIC "balone2/telemetry/motec"


// ESP32 TWAI (CAN Controller) Pins
#define CAN_TX_PIN 5
#define CAN_RX_PIN 4

// SD Card SPI Pin
#define SD_CS_PIN 15

// Rates
#define SAMPLE_HZ 20
#define SAMPLE_INTERVAL_MS (1000 / SAMPLE_HZ)

#endif // CONFIG_H
