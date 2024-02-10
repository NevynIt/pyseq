#ifndef MIDI_BRIDGE_H
#define MIDI_BRIDGE_H

#include "globals.h"

void activate_ruleset(const byte id);
void process_msg(const port_t src, const MIDI_msg_t msg);
void process_cmd(const port_t src, const int n);

#endif