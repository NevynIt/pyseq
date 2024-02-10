#include "midi_bridge.h"

void process_cmd(const port_t port) {
    byte &mode = serial_mode[port];
    cmd_buffer_t &buffer = cmd_buffer[port];

    if (buffer[0] == 0xFF)
        return; //ignore mode change commands

    //buffer[0-1] is the lenght of the command in bytes, including the length itself, in case we need it
    switch (mode)
    {
    case 0x01:
        
        break;
    
    default:
        //ignore any command
        break;
    }
}