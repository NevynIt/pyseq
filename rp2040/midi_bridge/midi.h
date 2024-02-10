#ifndef MIDI_H
#define MIDI_H

#include "data_types.h"
#include <Adafruit_TinyUSB.h>

#define MIDI_CABLE_NAME_1 "C1"
#define MIDI_CABLE_NAME_2 "C2"
#define MIDI_CABLE_NAME_3 "C3"

extern Adafruit_USBD_MIDI usb_midi;

void midi_setup();
void midi_task();

#endif