#include "can_handler.h"
#include "config.h"
#include "channels.h"
#include <driver/twai.h>

static float channel_values[NUM_CHANNELS];
static uint32_t channel_timestamps[NUM_CHANNELS];
static SemaphoreHandle_t state_mutex = NULL;

bool can_handler_init() {
    state_mutex = xSemaphoreCreateMutex();
    
    // Initialize channel values to NAN (Not a Number) to represent stale/empty state
    for (size_t i = 0; i < NUM_CHANNELS; i++) {
        channel_values[i] = NAN;
        channel_timestamps[i] = 0;
    }

    // Configure TWAI driver: 1 Mbps bitrate, standard pins, normal mode
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        (gpio_num_t)CAN_TX_PIN, 
        (gpio_num_t)CAN_RX_PIN, 
        TWAI_MODE_NORMAL
    );
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_1MBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    // Install and start TWAI driver
    if (twai_driver_install(&g_config, &t_config, &f_config) != ESP_OK) {
        Serial.println("[CAN] Failed to install TWAI driver!");
        return false;
    }
    if (twai_start() != ESP_OK) {
        Serial.println("[CAN] Failed to start TWAI driver!");
        return false;
    }

    Serial.println("[CAN] TWAI driver initialized at 1 Mbps.");
    return true;
}

static int64_t unpack_bytes(const uint8_t* data, uint8_t offset, uint8_t length, bool is_signed) {
    uint64_t raw_val = 0;
    for (uint8_t i = 0; i < length; i++) {
        raw_val |= ((uint64_t)data[offset + i]) << (8 * i);
    }
    
    if (is_signed) {
        if (length == 1) return (int8_t)raw_val;
        if (length == 2) return (int16_t)raw_val;
        if (length == 4) return (int32_t)raw_val;
    }
    return raw_val;
}

void can_handler_read() {
    twai_message_t message;
    
    // Read all queued messages (non-blocking, timeout = 0)
    while (twai_receive(&message, 0) == ESP_OK) {
        // Skip extended frames (MoTeC standard broadcast uses standard 11-bit IDs)
        if (message.extd) continue;

        uint32_t msg_id = message.identifier;
        uint32_t now = millis();

        if (xSemaphoreTake(state_mutex, pdMS_TO_TICKS(5)) == pdTRUE) {
            // Find channels that map to this CAN ID
            for (size_t i = 0; i < NUM_CHANNELS; i++) {
                if (CHANNELS[i].can_id == msg_id) {
                    const auto& ch = CHANNELS[i];
                    
                    // Boundary check
                    if (ch.byte_offset + ch.byte_length <= message.data_length_code) {
                        int64_t raw_val = unpack_bytes(message.data, ch.byte_offset, ch.byte_length, ch.is_signed);
                        float physical_val = (raw_val * ch.multiplier) + ch.offset;
                        
                        channel_values[i] = physical_val;
                        channel_timestamps[i] = now;
                    }
                }
            }
            xSemaphoreGive(state_mutex);
        }
    }
}

float can_handler_get_value(size_t index) {
    if (index >= NUM_CHANNELS) return NAN;
    
    float val = NAN;
    if (xSemaphoreTake(state_mutex, pdMS_TO_TICKS(5)) == pdTRUE) {
        // Check for stale data (timeout after 1000 ms)
        if (millis() - channel_timestamps[index] > 1000) {
            channel_values[index] = NAN;
        }
        val = channel_values[index];
        xSemaphoreGive(state_mutex);
    }
    return val;
}

uint32_t can_handler_get_last_update(size_t index) {
    if (index >= NUM_CHANNELS) return 0;
    
    uint32_t ts = 0;
    if (xSemaphoreTake(state_mutex, pdMS_TO_TICKS(5)) == pdTRUE) {
        ts = channel_timestamps[index];
        xSemaphoreGive(state_mutex);
    }
    return ts;
}

void can_handler_print_debug() {
    Serial.println("================================================");
    Serial.println(" ESP32 MoTeC CAN Telemetry Monitor");
    Serial.println("================================================");
    
    for (size_t i = 0; i < NUM_CHANNELS; i++) {
        float val = can_handler_get_value(i);
        Serial.printf("%-15s: ", CHANNELS[i].name);
        if (isnan(val)) {
            Serial.println("NaN");
        } else {
            Serial.printf("%.2f %s\n", val, CHANNELS[i].unit);
        }
    }
}
