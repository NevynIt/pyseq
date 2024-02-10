#ifndef AUDIO_H
#define AUDIO_H

#include "data_types.h"

#define AUDIO_SAMPLE_RATE 24000
#define AUDIO_SAMPLE_MILLIS 1000
#define AUDIO_BUFFER_SIZE (AUDIO_SAMPLE_RATE * AUDIO_SAMPLE_MILLIS / 1000)

extern uint16_t audio_in[AUDIO_BUFFER_SIZE];
extern uint16_t audio_out[AUDIO_BUFFER_SIZE];

void audio_setup();
void audio_task();

#endif