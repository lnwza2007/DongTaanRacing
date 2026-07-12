#ifndef CAN_HANDLER_H
#define CAN_HANDLER_H

#include <Arduino.h>

// Initialize TWAI (CAN) driver
bool can_handler_init();

// Read all available CAN packets and update state
void can_handler_read();

// Get the current state of a channel by index (Thread-safe)
float can_handler_get_value(size_t index);

// Get the last update timestamp of a channel
uint32_t can_handler_get_last_update(size_t index);

// Print debug state to Serial
void can_handler_print_debug();

#endif // CAN_HANDLER_H
