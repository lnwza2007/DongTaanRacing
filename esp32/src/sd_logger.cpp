#include "sd_logger.h"
#include "config.h"
#include "channels.h"
#include "can_handler.h"
#include <SPI.h>
#include <SD.h>

static File logFile;
static char activeFileName[32] = "";
static bool sdActive = false;
static uint32_t writeCount = 0;

bool sd_logger_init() {
    Serial.printf("[SD] Initializing SD Card (CS Pin: %d)...\n", SD_CS_PIN);
    
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("[SD] Mounting failed! Logger running without local SD logging.");
        sdActive = false;
        return false;
    }
    
    uint8_t cardType = SD.cardType();
    if (cardType == CARD_NONE) {
        Serial.println("[SD] No card found.");
        sdActive = false;
        return false;
    }

    Serial.println("[SD] Card initialized successfully.");
    sdActive = true;
    return true;
}

bool sd_logger_start_session() {
    if (!sdActive) return false;

    // Find the next available log index (e.g. /log_001.csv)
    int fileIndex = 1;
    while (fileIndex < 1000) {
        snprintf(activeFileName, sizeof(activeFileName), "/log_%03d.csv", fileIndex);
        if (!SD.exists(activeFileName)) {
            break;
        }
        fileIndex++;
    }

    Serial.printf("[SD] Creating file: %s\n", activeFileName);
    logFile = SD.open(activeFileName, FILE_WRITE);
    if (!logFile) {
        Serial.println("[SD] Failed to open file for writing.");
        return false;
    }

    // Write Header Row
    logFile.print("timestamp_ms");
    for (size_t i = 0; i < NUM_CHANNELS; i++) {
        logFile.printf(",%s", CHANNELS[i].name);
    }
    logFile.println();
    logFile.flush();

    return true;
}

void sd_logger_write_row(uint32_t timestamp_ms) {
    if (!sdActive || !logFile) return;

    // Write time offset
    logFile.printf("%u", timestamp_ms);

    // Write channel data
    for (size_t i = 0; i < NUM_CHANNELS; i++) {
        float val = can_handler_get_value(i);
        if (isnan(val)) {
            logFile.print(",NaN");
        } else {
            logFile.printf(",%.4f", val);
        }
    }
    logFile.println();

    // Flush every 20 rows to avoid loss on power cut
    writeCount++;
    if (writeCount % 20 == 0) {
        logFile.flush();
    }
}
