#include "midi_bridge.h"

void config_setup() {
  //set some defaults
  BPM = 120;
  PPQ = 240;
  serial_mode[port_usb] = 1;
  //load the configuration from flash
  active_rule_list_id = get_ruleset(0);
}
