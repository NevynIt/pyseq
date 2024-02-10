#include "midi_bridge.h"

Adafruit_USBD_MIDI usb_midi(3);

typedef byte MIDI_msg_t[4];
MIDI_msg_t midiMessage;

void midi_task() {
  if (usb_midi.available())
    if (usb_midi.readPacket(midiMessage))
      process_msg(port_midi, midiMessage);
}

void midi_setup() {
  #if defined(ARDUINO_ARCH_MBED) && defined(ARDUINO_ARCH_RP2040)
    // Manual begin() is required on core without built-in support for TinyUSB
    TinyUSB_Device_Init(0);
  #endif

  usb_midi.setCableName(1, MIDI_CABLE_NAME_1);
  usb_midi.setCableName(2, MIDI_CABLE_NAME_2);
  usb_midi.setCableName(3, MIDI_CABLE_NAME_3);

  usb_midi.begin();
}

void midi_send(const MIDI_msg_t &msg) {
    usb_midi.writePacket(msg);
}