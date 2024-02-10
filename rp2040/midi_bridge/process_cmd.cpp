#include "midi_bridge.h"

void process_cmd(const port_t port, const int n) {
    byte &mode = serial_mode[port];
    cmd_buffer_t &buffer = cmd_buffer[port];
    uint16_t &buffer_pos = cmd_buffer_pos[port];

    switch (mode)
    {
    case 0x01:
        /* code */
        break;
    
    default:
        //drop the data
        break;
    }
}