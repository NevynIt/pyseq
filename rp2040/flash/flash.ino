#include <Arduino.h>

#include <pico/stdlib.h>
#include <hardware/flash.h>
#include <hardware/sync.h>

void setup() {
  // Initialize serial communication at a baud rate of 115200:
  Serial.begin(2000000);
}

#define PICO_FLASH_START_ADDRESS 0

void loop() {
  // Wait for the "go!" command
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any whitespace

    if (command == "dump") {
      // Confirm command received
      // Serial.println("Command received, sending data...");

      // Pointer to the beginning of the XIP memory
      const uint8_t* dataPtr = (const uint8_t*)XIP_BASE;

      // Amount of data to send
      const unsigned long dataSize = 2 * 1024 * 1024; // 16MB

      // Send data in chunks to avoid serial buffer overflow
      const unsigned long chunkSize = 512; // Adjust based on your serial buffer size
      unsigned long sent = 0;

      while (sent < dataSize) {
        // Calculate remaining data size
        unsigned long remaining = dataSize - sent;
        unsigned long currentChunkSize = (remaining < chunkSize) ? remaining : chunkSize;

        // Send current chunk
        Serial.write(dataPtr + sent, currentChunkSize);

        // Update sent data size
        sent += currentChunkSize;

        // Optional: delay to ensure data is sent properly; adjust as needed
        delay(5);
      }

      // Serial.println("\nData transmission completed.");
    }
  
    if (command == "info") {
        Serial.write("Flash size: ");
        Serial.println(PICO_FLASH_SIZE_BYTES);
        Serial.write("Flash sector size: ");
        Serial.println(FLASH_SECTOR_SIZE);
        Serial.write("Flash page size: ");
        Serial.println(FLASH_PAGE_SIZE);
    }

    if (command == "erase") {
        // Select a "random" page in the flash over 1 MB. Ensure it's aligned to 4096 bytes.
        uint32_t sector = 256 + 146; //(rand() % (PICO_FLASH_SIZE_BYTES / FLASH_SECTOR_SIZE - 256))
        Serial.write("Sector: ");
        Serial.println(sector);
        uint32_t sector_address = sector * FLASH_SECTOR_SIZE;
        Serial.write("sector_address: ");
        Serial.println(sector_address);

        Serial.println("Before erase");
        // Erase the flash sector before writing
        noInterrupts();
        flash_range_erase(sector_address, FLASH_SECTOR_SIZE);
        interrupts();

        Serial.println("Flash erase complete.");
        }

    if (command == "write") {
        // Select a "random" page in the flash over 1 MB. Ensure it's aligned to 4096 bytes.
        uint32_t sector = 256 + 146; //(rand() % (PICO_FLASH_SIZE_BYTES / FLASH_SECTOR_SIZE - 256))
        Serial.write("Sector: ");
        Serial.println(sector);
        uint32_t sector_address = sector * FLASH_SECTOR_SIZE;
        Serial.write("sector_address: ");
        Serial.println(sector_address);
        uint32_t page = rand() % (FLASH_SECTOR_SIZE/FLASH_PAGE_SIZE);
        Serial.write("page: ");
        Serial.println(page);
        uint32_t page_address = sector_address + page * FLASH_PAGE_SIZE;
        Serial.write("page_address: ");
        Serial.println(page_address);

        // Prepare data to write: the address of the block, repeated 10 times.
        const int dsize = FLASH_PAGE_SIZE/sizeof(uint32_t);
        uint32_t data[dsize];
        for (uint32_t i = 0; i < dsize; i++) {
            if (i<10)
                data[i] = page_address;
            else
                data[i] = i;
        }

        Serial.println("Before writing");
        // // Write the data to the flash
        noInterrupts();
        flash_range_program(page_address, (const uint8_t*)data, sizeof(data));
        interrupts();

        Serial.println("Flash write complete.");
        }

    }
}