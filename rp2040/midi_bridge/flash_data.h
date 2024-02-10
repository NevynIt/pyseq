#ifndef FLASH_DATA_H
#define FLASH_DATA_H

#include "data_types.h"
#include <hardware/flash.h>

#if PICO_FLASH_SIZE_BYTES == (2 * 1024 * 1024)
    #define FL_CODE_PAGES 4096
    #define FL_CONFIG_PAGES 32
    #define FL_RULESET_PAGES 1
    #define FL_COMPR_PAGES 16
    #define FL_DECOMPR_PAGES 2
    #define FL_LIST_PAGES 2048
    #define FL_LOOKUP_PAGES 1024
    #define FL_ENVELOPE_PAGES 64
    #define FL_SAMPLE_PAGES 1933
#endif

#if PICO_FLASH_SIZE_BYTES == (16 * 1024 * 1024)
    #define FL_CODE_PAGES 4096
    #define FL_CONFIG_PAGES 64
    #define FL_RULESET_PAGES 4
    #define FL_COMPR_PAGES (16*4)
    #define FL_DECOMPR_PAGES (2*4)
    #define FL_LIST_PAGES 8192
    #define FL_LOOKUP_PAGES 2048
    #define FL_ENVELOPE_PAGES 256
    #define FL_SAMPLE_PAGES 52852
#endif

#define FL_TOTAL_PAGES (FL_CODE_PAGES + FL_CONFIG_PAGES + FL_RULESET_PAGES + FL_COMPR_PAGES + FL_DECOMPR_PAGES + FL_LIST_PAGES + FL_ENVELOPE_PAGES + FL_SAMPLE_PAGES)
#define FL_USED_MEMORY (FL_TOTAL_PAGES * FLASH_PAGE_SIZE)

#if FL_USED_MEMORY > PICO_FLASH_SIZE_BYTES
    #define FL_PAGES_OVERFLOW (-(PICO_FLASH_SIZE_BYTES - FL_USED_MEMORY)/FLASH_PAGE_SIZE)
    #pragma message "overflow amount: " FL_PAGES_OVERFLOW
    #error "Pages overflow"
#endif

#if FL_USED_MEMORY == PICO_FLASH_SIZE_BYTES
    #define FL_PAGES_FULL
#endif

#if FL_USED_MEMORY < PICO_FLASH_SIZE_BYTES
    #define FL_PAGES_AVAILABLE ((PICO_FLASH_SIZE_BYTES - FL_USED_MEMORY)/FLASH_PAGE_SIZE)
    #pragma message "pages available: " FL_PAGES_AVAILABLE
    #warning "Memory overflow"
#endif

#define FL_CONFIG_MAX   (FL_CONFIG_PAGES   * FLASH_PAGE_SIZE / sizeof(config_t))
#define FL_RULESET_MAX  (FL_RULESET_PAGES  * FLASH_PAGE_SIZE / sizeof(ruleset_t))
#define FL_COMPR_MAX    (FL_COMPR_PAGES    * FLASH_PAGE_SIZE / sizeof(compr_t))
#define FL_DECOMPR_MAX  (FL_DECOMPR_PAGES  * FLASH_PAGE_SIZE / sizeof(decompr_t))
#define FL_LIST_MAX     (FL_LIST_PAGES     * FLASH_PAGE_SIZE / sizeof(list_t))
#define FL_LOOKUP_MAX   (FL_LOOKUP_PAGES   * FLASH_PAGE_SIZE / sizeof(lookup_t))
#define FL_ENVELOPE_MAX (FL_ENVELOPE_PAGES * FLASH_PAGE_SIZE / sizeof(envelope_t))
#define FL_SAMPLE_MAX   (FL_SAMPLE_PAGES   * FLASH_PAGE_SIZE / sizeof(sample_t))

typedef struct {
    byte code[FL_CODE_PAGES * FLASH_PAGE_SIZE];
    ruleset_t  ruleset[FL_RULESET_MAX];
    compr_t compr[FL_COMPR_MAX];
    decompr_t decompr[FL_DECOMPR_MAX];
    list_t list[FL_LIST_MAX];
    lookup_t lookup[FL_LOOKUP_MAX];
    envelope_t envelope[FL_ENVELOPE_MAX];
    sample_t sample[FL_SAMPLE_MAX];
} fl_data_t;

#define fl_data (*((fl_data_t *)XIP_MAIN_BASE))

#endif