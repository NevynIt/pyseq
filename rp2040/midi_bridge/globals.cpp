#include "midi_bridge.h"

Adafruit_USBD_MIDI usb_midi(3);
byte active_rule_list_id;
byte serial_mode[3];
MIDI_msg_t midiMessage;
byte cmd_buffer[3][MAX_CMD_SIZE*2];
uint16_t cmd_buffer_pos[3];
byte Semaphore_0;
byte Semaphore_1;
uint16_t audio_in[AUDIO_BUFFER_SIZE];
uint16_t audio_out[AUDIO_BUFFER_SIZE];
byte BPM;
uint16_t PPQ;
seq_slot_t seq_slots[SEQ_SLOT_NUM];
active_envelope_t active_envelopes[ACTIVE_ENVELOPE_NUM];