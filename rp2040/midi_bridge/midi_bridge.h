#ifndef MIDI_BRIDGE_H
#define MIDI_BRIDGE_H

#include "data.h"
#include "audio.h"
#include "serial.h"
#include "midi.h"
#include "config.h"
#include "sequencer.h"

void process_msg(const port_t src, const MIDI_msg_t &msg);
void process_cmd(const port_t src);

#endif