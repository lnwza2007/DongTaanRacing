#ifndef SD_LOGGER_H
#define SD_LOGGER_H

#include <Arduino.h>

// Initialize SD Card filesystem
bool sd_logger_init();

// Start a new session log file (creates header)
bool sd_logger_start_session();

// Write a row of channel data to the active CSV file
void sd_logger_write_row(uint32_t timestamp_ms);

#endif // SD_LOGGER_H
