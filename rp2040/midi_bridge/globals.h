#ifndef GLOBALS_H
#define GLOBALS_H

#include <Arduino.h>
#include <Adafruit_TinyUSB.h>
#include "midi_bridge_data.h"
#include "flash_data.h"
#include "ioconfig.h"

extern Adafruit_USBD_MIDI usb_midi;
extern byte active_rule_list_id;
extern byte serial_mode[3];
extern MIDI_msg_t midiMessage;
extern byte cmd_buffer[3][MAX_CMD_SIZE*2];
extern uint16_t cmd_buffer_pos[3];
extern byte Semaphore_0;
extern byte Semaphore_1;
extern uint16_t audio_in[AUDIO_BUFFER_SIZE];
extern uint16_t audio_out[AUDIO_BUFFER_SIZE];
extern byte BPM;
extern uint16_t PPQ;
extern seq_slot_t seq_slots[SEQ_SLOT_NUM];
extern active_envelope_t active_envelopes[ACTIVE_ENVELOPE_NUM];

#endif