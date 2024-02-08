#include "midi_bridge.h"

void setup() {
#if defined(ARDUINO_ARCH_MBED) && defined(ARDUINO_ARCH_RP2040)
  // Manual begin() is required on core without built-in support for TinyUSB
  TinyUSB_Device_Init(0);
#endif
  load_IOSettings();

  usb_midi.setCableName(1, (char *)&IOSettings.c0name);
  usb_midi.setCableName(2, (char *)&IOSettings.c1name);
  usb_midi.setCableName(3, (char *)&IOSettings.c2name);

  usb_midi.begin();

  Serial1.setTX(IOSettings.pins[0]);
  Serial1.setRX(IOSettings.pins[1]);
  Serial2.setTX(IOSettings.pins[2]);
  Serial2.setRX(IOSettings.pins[3]);

  Serial.begin(IOSettings.speeds[0] * 9600);
  Serial1.begin(IOSettings.speeds[1] * 9600);
  Serial2.begin(IOSettings.speeds[2] * 9600);

  activate_ruleset(INIT_ruleset);
}

unsigned long last_idle[3];
void loop() {
  MIDI_msg_t midiMessage;

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

  // Check if there is data available from the UART0 interface
  if (Serial1.available() >= 4) {
    Serial1.readBytes((byte *)&midiMessage,4);
    process_msg(port_ser1, midiMessage);
  }

  // Check if there is data available from the UART1 interface
  if (Serial2.available() >= 4) {
    Serial2.readBytes((byte *)&midiMessage,4);
    process_msg(port_ser2, midiMessage);
  }

  // Check if there is data available from the USB interface
  if (Serial.available() >= 4) {
    Serial.readBytes((byte *)&midiMessage,4);
    process_msg(port_usb, midiMessage);
  }
}
