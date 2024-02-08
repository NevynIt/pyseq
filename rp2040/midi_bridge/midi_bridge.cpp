#include "midi_bridge.h"

Adafruit_USBD_MIDI usb_midi(3);
compiled_ruleset_t active_ruleset;
IOSettings_t IOSettings;

void load_IOSettings() {
  EEPROM.get(addr_IOSettings, IOSettings);
  if (IOSettings.magic != magic_number) {
        //Magic number mismatch, set some defaults
        IOSettings.magic = magic_number;
        IOSettings.manuf_ID[0] = 0x00;
        IOSettings.manuf_ID[1] = 0x36;
        IOSettings.manuf_ID[2] = 0x63;
        IOSettings.speeds[0] = 230400/9600;
        IOSettings.speeds[1] = 230400/9600;
        IOSettings.speeds[2] = 230400/9600;
        memcpy((byte *)&IOSettings.c0name, "Cable 1", 8);
        memcpy((byte *)&IOSettings.c1name, "Cable 2", 8);
        memcpy((byte *)&IOSettings.c2name, "Cable 3", 8);
        IOSettings.pins[0] = 0;
        IOSettings.pins[1] = 1;
        IOSettings.pins[2] = 4;
        IOSettings.pins[3] = 5;
        EEPROM.put(addr_IOSettings, IOSettings);
      }
}

uint32_t find_id_in_eeprom(const ID_t find_id, const uint32_t start_addr, const uint32_t size, const uint32_t max) {
  //find the object in the EEPROM
  uint32_t addr = start_addr;
  uint16_t n = 0;
  ID_t id;
  EEPROM.get(addr, id);
  while (n<max && id != find_id) {
    addr += size;
    n++;
    EEPROM.get(addr, id);
  }
  if (n<max)
    return addr;
  else
    return 0;
}

inline uint32_t find_ruleset(const ID_t find_id) {
  return find_id_in_eeprom(find_id, addr_rulesets, sizeof(ruleset_t), max_rulesets);
}

inline uint32_t find_rule(const ID_t find_id) {
  return find_id_in_eeprom(find_id, addr_rules, sizeof(rule_t), max_rules);
}

inline uint32_t find_lookup(const ID_t find_id) {
  return find_id_in_eeprom(find_id, addr_lookup, sizeof(lookup_t), max_lookup);
}

inline uint32_t find_macro(const ID_t find_id) {
  return find_id_in_eeprom(find_id, addr_macro, sizeof(macro_t), max_macro);
}

typedef ID_t compiled_ids_t[256];

void compile_rule(const rule_t rule, compiled_ids_t &lookups, compiled_ids_t &macros) {
  // ID_t ID;
  // byte src_mask[8]; //- see markdown documentation
  // byte d2min, d2max, d3min, d3max;

  // ID_t macro;
  // ID_t lookup;
  // byte transpose;
  // byte velocity;

  // byte dst_mask[6]; //- see markdown documentation
  int i;

  //add the rule to the active_ruleset, referencing or copying lookups and macros as required
  compiled_rule_t *comp = &(active_ruleset.rules[active_ruleset.nrules]);
  comp->src_port    =  rule.src_mask[0] & 0b0001111;
  comp->src_cable   = (rule.src_mask[1] & 0b0110000) << 10 + rule.src_mask[2] << 7 + rule.src_mask[3];
  comp->src_channel = (rule.src_mask[1] & 0b0001100) << 12 + rule.src_mask[4] << 7 + rule.src_mask[5];
  comp->src_message = (rule.src_mask[1] & 0b0000011) << 14 + rule.src_mask[6] << 7 + rule.src_mask[7];
  comp->d2min = rule.d2min;
  comp->d2max = rule.d2max;
  comp->d3min = rule.d3min;
  comp->d3max = rule.d3max;
  //see if we have already copied the macro
  for (i=0; i<256; i++)
    if (macros[i] == rule.macro || macros[i] == 0)
      break;
  if (i<256)
  {
    if (macros[i] == 0) {
      uint32_t addr = find_macro(rule.macro);
      if (addr != 0) {
        macro_t macro;
        EEPROM.get(addr, macro);
        memcpy((void *)&active_ruleset.macros[i], ((void *)&macro) + sizeof(ID_t), sizeof(compiled_macro_t));
        macros[i] = rule.macro;
      }
    }
    if (macros[i] != 0)
      comp->macro = (byte)i;
  }

  //see if we have already copied the lookup
  for (i=0; i<256; i++)
    if (lookups[i] == rule.lookup || lookups[i] == 0)
      break;
  if (i<256)
  {
    if (lookups[i] == 0) {
      uint32_t addr = find_lookup(rule.lookup);
      if (addr != 0) {
        lookup_t lookup;
        EEPROM.get(addr, lookup);
        memcpy((void *)&active_ruleset.lookups[i], ((void *)&lookup) + sizeof(ID_t), sizeof(compiled_lookup_t));
        lookups[i] = rule.lookup;
      }
    }
    if (lookups[i] != 0)
      comp->lookup = (byte)i;
  }
  comp->transpose = rule.transpose;
  comp->velocity = rule.velocity;

  comp->dst = (rule.dst_mask[0] & 0b0110000) << 2 + (rule.dst_mask[1] & 0b0100000) + (rule.dst_mask[1] & 0b0000100) << 3 + (rule.dst_mask[0] & 0b0001111);
  comp->dst_cable = (rule.dst_mask[1] & 0b0011000) << 11 + (rule.dst_mask[2]) << 7 + (rule.dst_mask[3]);
  comp->dst_channel = (rule.dst_mask[1] & 0b0000011) << 14 + (rule.dst_mask[4]) << 7 + (rule.dst_mask[5]);

  active_ruleset.nrules++;

  // byte src_port;
  // uint16_t src_cable;
  // uint16_t src_channel;
  // uint16_t src_message;
  // byte d2min, d2max, d3min, d3max;

  // byte macro;
  // byte lookup;
  // byte transpose;
  // byte velocity;

  // byte dst; //RLLLSSSS - see markdown documentation
  // uint16_t dst_cable;
  // uint16_t dst_channel;
}

void activate_ruleset(const ID_t id) {
  uint32_t addr = find_ruleset(id);
  if (addr != 0) {
    memset((void *)&active_ruleset, 0, sizeof(compiled_ruleset_t));
    ruleset_t ruleset;
    EEPROM.get(addr, ruleset);

    compiled_ids_t lookups, macros;

    for (int i=0; i<511; i++) {
      ID_t id = ruleset.rules[i];
      if (id == 0)
        continue;
      addr = find_rule(id);
      if (addr != 0) {
        rule_t rule;
        EEPROM.get(addr, rule);
        compile_rule(rule, lookups, macros);
      }
    }
  }
}

void process_msg(const port_t src, const MIDI_msg_t msg) {

}

