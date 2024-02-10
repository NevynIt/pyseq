#ifndef FLASH_DATA_H
#define FLASH_DATA_H

#include <hardware/flash.h>
#include "midi_bridge_data.h"

#define FL_CODE_PAGES 4096
#define FL_CONFIG_PAGES 32
#define FL_RULESET_PAGES 1
#define FL_COMPR_PAGES 16
#define FL_DECOMPR_PAGES 2
#define FL_LIST_PAGES 2048
#define FL_LOOKUP_PAGES 1024
#define FL_ENVELOPE_PAGES 64
#define FL_AUDIO_PAGES 910

#define FL_CONFIG_ADDR (XIP_BASE + FL_CODE_PAGES * FLASH_PAGE_SIZE)
#define FL_RULESET_ADDR (FL_CONFIG_ADDR + FL_CONFIG_PAGES * FLASH_PAGE_SIZE)
#define FL_COMPR_ADDR (FL_RULESET_ADDR + FL_RULESET_PAGES * FLASH_PAGE_SIZE)
#define FL_DECOMPR_ADDR (FL_COMPR_ADDR + FL_COMPR_PAGES * FLASH_PAGE_SIZE)
#define FL_LIST_ADDR (FL_DECOMPR_ADDR + FL_DECOMPR_PAGES * FLASH_PAGE_SIZE)
#define FL_LOOKUP_ADDR (FL_LIST_ADDR + FL_LIST_PAGES * FLASH_PAGE_SIZE)
#define FL_ENVELOPE_ADDR (FL_LOOKUP_ADDR + FL_LOOKUP_PAGES * FLASH_PAGE_SIZE)
#define FL_AUDIO_ADDR (FL_ENVELOPE_ADDR + FL_ENVELOPE_PAGES * FLASH_PAGE_SIZE)

#define fl_config_num (FL_CONFIG_PAGES * FLASH_PAGE_SIZE / sizeof(config_t))
#define fl_ruleset_num (FL_RULESET_PAGES * FLASH_PAGE_SIZE / sizeof(ruleset_t))
#define fl_list_num (FL_LIST_PAGES * FLASH_PAGE_SIZE / sizeof(list_t))
#define fl_lookup_num (FL_LOOKUP_PAGES * FLASH_PAGE_SIZE / sizeof(lookup_t))
#define fl_envelope_num (FL_ENVELOPE_ADDR * FLASH_PAGE_SIZE / sizeof(envelope_t))

#define fl_config ((const config_t *)FL_CONFIG_ADDR)
#define fl_ruleset ((const ruleset_t *)FL_RULESET_ADDR)
#define fl_list ((const list_t *)FL_LIST_ADDR)
#define fl_lookup ((const lookup_t *)FL_LOOKUP_ADDR)
#define fl_envelope ((const envelope_t *)FL_RULESET_ADDR)

#endif