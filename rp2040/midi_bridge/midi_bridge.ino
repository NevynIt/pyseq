#include "midi_bridge.h"

byte Semaphore_0;
byte Semaphore_1;

//CORE 0
void setup() {
    midi_setup();
    serial_setup();
    audio_setup();
    config_setup();
}

void loop() {
    midi_task();
    serial_task();
    audio_task();
}

//CORE 1
void setup1() {
    sequencer_setup();
}

void loop1() {
    sequencer_task();
}