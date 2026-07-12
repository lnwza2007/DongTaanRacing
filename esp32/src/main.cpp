#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"
#include "channels.h"
#include "can_handler.h"
#include "mqtt_handler.h"
#include "sd_logger.h"

static unsigned long lastSampleTime = 0;
static unsigned long lastDebugTime = 0;
static uint32_t messageCount = 0;

void setup() {
    // Start serial console
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n=============================================");
    Serial.println(" ESP32 MoTeC CAN Telemetry Logger Starting");
    Serial.println("=============================================");

    // Initialize subsystems
    mqtt_handler_init();
    can_handler_init();
    
    if (sd_logger_init()) {
        sd_logger_start_session();
    }

    lastSampleTime = millis();
    lastDebugTime = millis();
}

void loop() {
    // 1. Read and decode all incoming CAN frames (Non-blocking TWAI reception)
    can_handler_read();

    // 2. Maintain WiFi and MQTT connection states
    mqtt_handler_loop();

    unsigned long now = millis();

    // 3. Fixed Rate Sampling Loop (20 Hz)
    if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
        lastSampleTime += SAMPLE_INTERVAL_MS;

        // Log locally to SD Card
        sd_logger_write_row(now);

        // Package data to JSON for MQTT
        if (mqtt_handler_is_connected()) {
            StaticJsonDocument<512> doc;
            doc["timestamp_ms"] = now;
            doc["session_id"] = "esp32_active";
            
            JsonObject dataObj = doc.createNestedObject("data");
            
            // Build dynamic data payload of active (non-NaN) channels
            for (size_t i = 0; i < NUM_CHANNELS; i++) {
                float val = can_handler_get_value(i);
                if (!isnan(val)) {
                    // Truncate to 4 decimals for bandwidth efficiency
                    dataObj[CHANNELS[i].name] = roundf(val * 10000.0f) / 10000.0f;
                }
            }

            // Publish JSON payload
            String payload;
            serializeJson(doc, payload);
            mqtt_handler_publish(payload.c_str());
        }
    }

    // 4. Debug Console Loop (1 Hz)
    if (now - lastDebugTime >= 1000) {
        lastDebugTime = now;
        
        // Output live stats on Serial
        can_handler_print_debug();
        Serial.printf("WiFi/MQTT Connected: %s | Active SD Logging: %d\n", 
                      mqtt_handler_is_connected() ? "Yes" : "No", 
                      SD.cardSize() > 0);
        Serial.println("================================================\n");
    }
}
