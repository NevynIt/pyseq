#include "midi_bridge.h"

void load_config() {
  //set some defaults
  BPM = 120;
  PPQ = 240;
  serial_mode[port_usb] = 1;
  active_rule_list_id = 0xFFFF;

}

void setup_midi() {
  usb_midi.setCableName(1, MIDI_CABLE_NAME_1);
  usb_midi.setCableName(2, MIDI_CABLE_NAME_2);
  usb_midi.setCableName(3, MIDI_CABLE_NAME_3);

  usb_midi.begin();
}

void setup_serial() {
  Serial1.setTX(Ser1_TX);
  Serial1.setRX(Ser1_RX);
  Serial2.setTX(Ser2_TX);
  Serial2.setRX(Ser2_RX);

  Serial.begin(SERIAL_SPEED);
  Serial1.begin(SERIAL_SPEED);
  Serial2.begin(SERIAL_SPEED);
}

void audio_interrupt() {
    //increment the counter
    //sample the two ADCs
    //set the two PWMs
}

void setup_audio() {
  //Start PWM and interrupts for audio I/O
}

void activate_ruleset(const byte id) {
}

void setup() {
#if defined(ARDUINO_ARCH_MBED) && defined(ARDUINO_ARCH_RP2040)
  // Manual begin() is required on core without built-in support for TinyUSB
  TinyUSB_Device_Init(0);
#endif
  load_config();

  setup_midi();
  setup_serial();
  setup_audio();
  activate_ruleset(0);
}
