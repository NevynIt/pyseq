#ifndef SEQUENCER_H
#define SEQUENCER_H

#include "data_types.h"

#define SEQ_SLOT_MAX 256
#define ACTIVE_ENVELOPE_MAX 256

extern byte BPM;
extern uint16_t PPQ;
extern seq_slot_t seq_slots[SEQ_SLOT_MAX];
extern active_envelope_t active_envelopes[SEQ_SLOT_MAX];

void sequencer_setup();
void sequencer_task();

#endif