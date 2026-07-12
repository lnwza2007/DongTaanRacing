#ifndef CHANNELS_H
#define CHANNELS_H

#include <Arduino.h>

struct ChannelDef {
    const char* name;
    uint32_t can_id;
    uint8_t byte_offset;
    uint8_t byte_length;
    bool is_signed;
    float multiplier;
    float offset;
    const char* unit;
};

// Definitions aligned with PROTOCOL.md (Little Endian / Intel Byte Order)
const ChannelDef CHANNELS[] = {
    // 0x640: Primary Engine Data
    {"engine_rpm", 0x640, 0, 2, false, 1.0f, 0.0f, "rpm"},
    {"throttle_pos", 0x640, 2, 2, true, 0.1f, 0.0f, "%"},
    {"manifold_pres", 0x640, 4, 2, true, 0.1f, 0.0f, "kPa"},
    {"coolant_temp", 0x640, 6, 2, true, 0.1f, 0.0f, "C"},

    // 0x648: Secondary Engine Sensors
    {"oil_pres", 0x648, 0, 2, true, 0.1f, 0.0f, "kPa"},
    {"oil_temp", 0x648, 2, 2, true, 0.1f, 0.0f, "C"},
    {"intake_temp", 0x648, 4, 2, true, 0.1f, 0.0f, "C"},
    {"fuel_pres", 0x648, 6, 2, true, 0.1f, 0.0f, "kPa"},

    // 0x650: Fuel & Lambda Status
    {"lambda_1", 0x650, 0, 2, false, 0.001f, 0.0f, "La"},
    {"lambda_2", 0x650, 2, 2, false, 0.001f, 0.0f, "La"},
    {"fuel_temp", 0x650, 4, 2, true, 0.1f, 0.0f, "C"},
    {"exhaust_temp", 0x650, 6, 2, true, 0.1f, 0.0f, "C"},

    // 0x660: Gearbox & Battery
    {"gear_pos", 0x660, 0, 2, true, 1.0f, 0.0f, ""},
    {"battery_volt", 0x660, 2, 2, false, 0.01f, 0.0f, "V"},
    {"vehicle_speed", 0x660, 4, 2, false, 0.1f, 0.0f, "km/h"},
    {"ign_advance", 0x660, 6, 2, true, 0.1f, 0.0f, "deg"},

    // 0x700: C125 Lap Timing & Buttons
    {"lap_number", 0x700, 0, 2, false, 1.0f, 0.0f, ""},
    {"lap_time_ms", 0x700, 2, 4, false, 1.0f, 0.0f, "ms"},
    {"dash_button_1", 0x700, 6, 1, false, 1.0f, 0.0f, ""},
    {"dash_button_2", 0x700, 7, 1, false, 1.0f, 0.0f, ""}
};

const size_t NUM_CHANNELS = sizeof(CHANNELS) / sizeof(CHANNELS[0]);

#endif // CHANNELS_H
