#include "midi_bridge.h"

byte serial_mode[3];
byte cmd_buffer[3][MAX_CMD_SIZE*2];
uint16_t cmd_buffer_pos[3];

const unsigned long timeout = 500;
unsigned long last_idle[3];

void serial_flush(Stream &src, port_t port) {
  int sa = src.available();
  unsigned long t0 = millis();

  if (sa  == 0)
    last_idle[port] = t0;
  else if (sa  < 4 && t0 - last_idle[port] > timeout)
    src.readBytes((byte *)&midiMessage, sa);
}

void serial_read(Stream &src, port_t port) {
  serial_flush(src, port);

  if (serial_mode[port] == 0)
    if (src.available() >= 4) {
      src.readBytes((byte *)&midiMessage,4);
      if (*((uint64_t *)&midiMessage) == 0xFFFFFFFF)
        serial_mode[port] = 1;
      else
        process_msg(port, midiMessage);
    }
  else if (serial_mode[port] == 1)
    if (src.available() > 0) {
      int n = min(MAX_CMD_SIZE, Serial1.available());
      src.readBytes(&cmd_buffer[port][cmd_buffer_pos[port]],n);
      process_cmd(port, n);
    }
}

void serial_setup() {
  Serial1.setTX(Ser1_TX);
  Serial1.setRX(Ser1_RX);
  Serial2.setTX(Ser2_TX);
  Serial2.setRX(Ser2_RX);

  Serial.begin(SERIAL_SPEED);
  Serial1.begin(SERIAL_SPEED);
  Serial2.begin(SERIAL_SPEED);
}

void serial_task() {
  serial_read(Serial, port_usb);
  serial_read(Serial1, port_ser1);
  serial_read(Serial2, port_ser2);
}