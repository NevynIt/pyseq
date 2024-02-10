#ifndef SERIAL_H
#define SERIAL_H

#include "data_types.h"

#define Ser1_TX 0
#define Ser1_RX 1
#define Ser2_TX 4
#define Ser2_RX 5
#define SERIAL_SPEED (24*9600)

extern byte serial_mode[3];
extern cmd_buffer_t cmd_buffer[3];
extern uint16_t cmd_buffer_pos[3];

void serial_setup();
void serial_task();
void serial_switch(const port_t port);

#endif