#include "mqtt_handler.h"
#include "config.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

static WiFiClientSecure secureClient;
static PubSubClient mqttClient(secureClient);
static unsigned long lastConnectAttempt = 0;

void mqtt_handler_init() {
    Serial.printf("[WiFi] Connecting to SSID: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    // Disable certificate validation for lightweight TLS connection
    secureClient.setInsecure();

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    // Increase buffer size to handle larger JSON telemetry frames
    mqttClient.setBufferSize(1024);
}

static bool reconnect_mqtt() {
    if (mqttClient.connect("esp32_motec_logger", MQTT_USER, MQTT_PASS)) {
        Serial.println("[MQTT] Connected to HiveMQ Cloud.");
        return true;
    }
    Serial.printf("[MQTT] Connection failed, rc=%d\n", mqttClient.state());
    return false;
}

void mqtt_handler_loop() {
    // Check WiFi Connection
    if (WiFi.status() != WL_CONNECTED) {
        if (millis() % 5000 < 50) {
            Serial.println("[WiFi] Reconnecting...");
        }
        return;
    }

    // Check MQTT Connection
    if (!mqttClient.connected()) {
        unsigned long now = millis();
        if (now - lastConnectAttempt > 5000) {
            lastConnectAttempt = now;
            Serial.println("[MQTT] Attempting connection...");
            if (reconnect_mqtt()) {
                lastConnectAttempt = 0;
            }
        }
    } else {
        mqttClient.loop();
    }
}

void mqtt_handler_publish(const char* payload) {
    if (mqttClient.connected()) {
        mqttClient.publish(MQTT_TOPIC, payload);
    }
}

bool mqtt_handler_is_connected() {
    return WiFi.status() == WL_CONNECTED && mqttClient.connected();
}
