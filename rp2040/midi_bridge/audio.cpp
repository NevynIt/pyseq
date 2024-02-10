#include "midi_bridge.h"

uint16_t audio_in[AUDIO_BUFFER_SIZE];
uint16_t audio_out[AUDIO_BUFFER_SIZE];

void audio_interrupt() {
    //increment the counter
    //sample the two ADCs
    //set the two PWMs
}

void audio_setup() {
  //Start PWM and interrupts for audio I/O
}

void audio_task() {

}