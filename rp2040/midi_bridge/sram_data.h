#ifndef SRAM_DATA_H
#define SRAM_DATA_H

#include "data_types.h"
#define SRAM_PAGE_SIZE 256

#define SR_CODE_PAGES 0
#define SR_CONFIG_PAGES 1
#define SR_RULESET_PAGES 1
#define SR_COMPR_PAGES 16
#define SR_DECOMPR_PAGES 2
#define SR_LIST_PAGES 400
#define SR_LOOKUP_PAGES 32
#define SR_ENVELOPE_PAGES 2
#define SR_SAMPLE_PAGES 300

#define SR_TOTAL_PAGES (SR_CODE_PAGES + SR_CONFIG_PAGES + SR_RULESET_PAGES + SR_COMPR_PAGES + SR_DECOMPR_PAGES + SR_LIST_PAGES + SR_ENVELOPE_PAGES + SR_SAMPLE_PAGES)
#define SR_USED_MEMORY (SR_TOTAL_PAGES * SRAM_PAGE_SIZE)

#define SR_CONFIG_MAX   (SR_CONFIG_PAGES   * SRAM_PAGE_SIZE / sizeof(config_t))
#define SR_RULESET_MAX  (SR_RULESET_PAGES  * SRAM_PAGE_SIZE / sizeof(ruleset_t))
#define SR_COMPR_MAX    (SR_COMPR_PAGES    * SRAM_PAGE_SIZE / sizeof(compr_t))
#define SR_DECOMPR_MAX  (SR_DECOMPR_PAGES  * SRAM_PAGE_SIZE / sizeof(decompr_t))
#define SR_LIST_MAX     (SR_LIST_PAGES     * SRAM_PAGE_SIZE / sizeof(list_t))
#define SR_LOOKUP_MAX   (SR_LOOKUP_PAGES   * SRAM_PAGE_SIZE / sizeof(lookup_t))
#define SR_ENVELOPE_MAX (SR_ENVELOPE_PAGES * SRAM_PAGE_SIZE / sizeof(envelope_t))
#define SR_SAMPLE_MAX   (SR_SAMPLE_PAGES   * SRAM_PAGE_SIZE / sizeof(sample_t))

typedef struct {
    // byte code[SR_CODE_PAGES * SRAM_PAGE_SIZE];
    ruleset_t  ruleset[SR_RULESET_MAX];
    compr_t compr[SR_COMPR_MAX];
    decompr_t decompr[SR_DECOMPR_MAX];
    list_t list[SR_LIST_MAX];
    lookup_t lookup[SR_LOOKUP_MAX];
    envelope_t envelope[SR_ENVELOPE_MAX];
    sample_t sample[SR_SAMPLE_MAX];
} sr_data_t;

#endif