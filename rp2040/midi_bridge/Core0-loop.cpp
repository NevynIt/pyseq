#include "midi_bridge.h"

unsigned long last_idle[3];
void loop() {

  const unsigned long timeout = 500;
  //logic to drop partial messages that have been waiting more than timeout ms

  int sa;
  unsigned long t0;

  sa = Serial.available();
  t0 = millis();
  if (sa  == 0)
    last_idle[port_usb] = t0;
  else if (sa  < 4 && t0 - last_idle[port_usb] > timeout)
    Serial.readBytes((byte *)&midiMessage,sa);

  sa = Serial1.available();
  if (sa  == 0)
    last_idle[port_ser1] = t0;
  else if (sa  < 4 && t0 - last_idle[port_ser1] > timeout)
    Serial1.readBytes((byte *)&midiMessage,sa);

  sa = Serial2.available();
  if (sa  == 0)
    last_idle[port_ser2] = t0;
  else if (sa  < 4 && t0 - last_idle[port_ser2] > timeout)
    Serial2.readBytes((byte *)&midiMessage,sa);

  //logic to read and process messages

  // Check if there is a MIDI message available from the USB MIDI interface
  if (usb_midi.available()) {
    if (usb_midi.readPacket(midiMessage)) {
      process_msg(port_midi, midiMessage);
    }
  }

  port_t port;

  port = port_ser1;
  if (serial_mode[port] == 0)
    if (Serial1.available() >= 4) {
      Serial1.readBytes((byte *)&midiMessage,4);
      if (*((uint64_t *)&midiMessage) == 0xFFFFFFFF)
        serial_mode[port] = 1;
      else
        process_msg(port, midiMessage);
    }
  else if (serial_mode[port] == 1)
    if (Serial1.available() > 0) {
      int n = min(MAX_CMD_SIZE, Serial1.available());
      Serial1.readBytes(&cmd_buffer[port][cmd_buffer_pos[port]],n);
      process_cmd(port, n);
    }

  port = port_ser2;
  if (serial_mode[port] == 0)
    if (Serial2.available() >= 4) {
      Serial2.readBytes((byte *)&midiMessage,4);
      if (*((uint64_t *)&midiMessage) == 0xFFFFFFFF)
        serial_mode[port] = 1;
      else
        process_msg(port, midiMessage);
    }
  else if (serial_mode[port] == 1)
    if (Serial2.available() > 0) {
      int n = min(MAX_CMD_SIZE, Serial2.available());
      Serial2.readBytes(&cmd_buffer[port][cmd_buffer_pos[port]],n);
      process_cmd(port, n);
    }

  port = port_usb;
  if (serial_mode[port] == 0)
    if (Serial.available() >= 4) {
      Serial.readBytes((byte *)&midiMessage,4);
      if (*((uint64_t *)&midiMessage) == 0xFFFFFFFF)
        serial_mode[port] = 1;
      else
        process_msg(port, midiMessage);
    }
  else if (serial_mode[port] == 1)
    if (Serial.available() > 0) {
      int n = min(MAX_CMD_SIZE, Serial.available());
      Serial.readBytes(&cmd_buffer[port][cmd_buffer_pos[port]],n);
      process_cmd(port, n);
    }
}
