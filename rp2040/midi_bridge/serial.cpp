#include "midi_bridge.h"

byte serial_mode[3];
byte cmd_buffer[3][MAX_CMD_SIZE*2];
uint16_t cmd_buffer_pos[3];

const unsigned long idle_timeout = 500;
unsigned long last_idle[3];
unsigned long reactivate_time[3];

void serial_switch(const port_t port) {
  byte &mode = serial_mode[port];
  cmd_buffer_t &buffer = cmd_buffer[port];
  uint16_t &buffer_pos = cmd_buffer_pos[port];

  mode = buffer[1];
  if (mode != 0) {
    buffer_pos = 0;
    process_cmd(port, 4);
  }
}

void serial_read(Stream &src, const port_t port) {
  byte &mode = serial_mode[port];
  cmd_buffer_t &buffer = cmd_buffer[port];
  uint16_t &buffer_pos = cmd_buffer_pos[port];

  int sa = src.available();
  unsigned long t0 = millis();
 
  if (reactivate_time[port] != 0)
    if (reactivate_time[port] > t0) {
      while (sa > 0) {
        int n = min(MAX_CMD_SIZE, sa);
        src.readBytes((byte *)buffer,n);
        sa -= n;
      }
      return;
    }
    else {
      reactivate_time[port] = 0;
    }

  if (sa  == 0)
    last_idle[port] = t0;
  else if (sa  < 4 && t0 - last_idle[port] > idle_timeout)
    src.readBytes((byte *)buffer, sa);

  if (mode == 0)
    if (sa >= 4) {
      src.readBytes((byte *)buffer,4);
      
      if (buffer[0] == 0xFF)
        serial_switch(port);
      else
        process_msg(port, *((const MIDI_msg_t *)buffer));
    }
  else if (sa > 0) {
      int n = min(MAX_CMD_SIZE, sa);
      src.readBytes(&(buffer[buffer_pos]),n);
      buffer_pos += n;

      if (buffer[0] == 0xFF)
        serial_switch(port);
      else while (1) {
        const uint16_t &cmd_len = *(const uint16_t *)buffer;
        if (cmd_len == 0)
          break;

        if (cmd_len > MAX_CMD_SIZE) { //obviously an error in the communication, reset and ignore any input for a fixed time
          buffer_pos = 0;
          reactivate_time[port] = t0 + idle_timeout + 10;
          return;
        }
        
        if (buffer_pos >= cmd_len) {
          process_cmd(port);
          if (buffer_pos > cmd_len) {
            //copy the bytes to the beginning
            memccpy((void *) buffer, (void *)&buffer[cmd_len], buffer_pos - cmd_len);
          }
          buffer_pos -= cmd_len;
          //make sure that leftover bytes from previous read are reinitialised to zero;
          buffer[buffer_pos] = 0;
          buffer[buffer_pos+1] = 0;
        }
        else
          break; //need more data
      }
        
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