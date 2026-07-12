#ifndef MQTT_HANDLER_H
#define MQTT_HANDLER_H

#include <Arduino.h>

// Connect WiFi & initialize MQTT Secure Client
void mqtt_handler_init();

// Keep WiFi and MQTT connection alive
void mqtt_handler_loop();

// Publish telemetry snapshot over MQTT
void mqtt_handler_publish(const char* payload);

// Returns true if WiFi & MQTT are connected
bool mqtt_handler_is_connected();

#endif // MQTT_HANDLER_H
