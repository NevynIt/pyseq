#ifndef MIDI_BRIDGE_DATA_H
#define MIDI_BRIDGE_DATA_H

typedef uint32_t ID_t;

typedef byte MIDI_msg_t[4];

typedef struct {
  ID_t magic;
  byte manuf_ID[3];
  byte speeds[3];
  char c0name[8];
  char c1name[8];
  char c2name[8];
  byte pins[4];
} IOSettings_t;

typedef struct {
  ID_t ID;
  byte src_mask[8]; //- see markdown documentation
  byte d2min, d2max, d3min, d3max;

  ID_t macro;
  ID_t lookup;
  byte transpose;
  byte velocity;

  byte dst_mask[6]; //- see markdown documentation
} rule_t;

typedef struct {
  byte src_port;
  uint16_t src_cable;
  uint16_t src_channel;
  uint16_t src_message;
  byte d2min, d2max, d3min, d3max;

  byte macro;
  byte lookup;
  byte transpose;
  byte velocity;

  byte dst; //RLLLSSSS - see markdown documentation
  uint16_t dst_cable;
  uint16_t dst_channel;
} compiled_rule_t;

typedef struct {
  ID_t ID;
  byte map[128];
} lookup_t;

typedef struct {
  byte map[128];
} compiled_lookup_t;

typedef struct { //5 bytes
  byte port_data_mask;
  byte cable_message_channel_mask;
  byte message_channel;
  byte data2;
  byte data3;
} macro_step_t;

typedef struct { //128 bytes
  ID_t ID;
  byte len;
  macro_step_t steps[24];
} macro_t;

typedef struct {
  byte len;
  macro_step_t steps[24];
} compiled_macro_t;

typedef struct {
  ID_t ID;
  ID_t rules[511];
} ruleset_t;

typedef struct {
  uint16_t nrules;
  compiled_rule_t rules[511];
  compiled_lookup_t lookups[256];
  compiled_macro_t macros[256];
} compiled_ruleset_t;

typedef enum{
  port_usb  = 0, 
  port_ser1 = 1,
  port_ser2 = 2,
  port_midi = 3
} port_t;

const uint16_t max_rulesets = 128;
const uint16_t max_rules = 4096;
const uint16_t max_lookup = 512;
const uint16_t max_macro = 512;

const uint32_t addr_IOSettings = 0;
const uint32_t addr_rulesets = 1024; //arbitrary to leave space for more settings
const uint32_t addr_rules = addr_rulesets + sizeof(ruleset_t) * max_rulesets;
const uint32_t addr_lookup = addr_rules + sizeof(rule_t) * max_rules;
const uint32_t addr_macro = addr_lookup + sizeof(lookup_t) * max_lookup;
const uint32_t addr_end = addr_macro + sizeof(macro_t) * max_macro;

const ID_t magic_number = 0x31D1B41D; //MIDIBRID

const ID_t INIT_ruleset = 0x49434954; //'INIT'

#endif
