#ifndef MIDI_BRIDGE_H
#define MIDI_BRIDGE_H

#include <Arduino.h>
#include <Adafruit_TinyUSB.h>
#include <ArduinoUniqueID.h>
#include <EEPROM.h>

#include "midi_bridge_data.h"

extern Adafruit_USBD_MIDI usb_midi;
extern IOSettings_t IOSettings;

void activate_ruleset(const ID_t id);
void process_msg(const port_t src, const MIDI_msg_t msg);
void load_IOSettings();

#endif