#ifndef DATA_H
#define DATA_H

#include "data_types.h"
#include "flash_data.h"
#include "sram_data.h"

// NOTE: fl_data is defined as a macro
extern sr_data_t sr_data;
extern uint16_t active_rule_list_id;

const uint64_t invalid_data = 0xFFFFFFFF;

inline const ruleset_t &get_ruleset(uint16_t id) {
    if (id < SR_RULESET_MAX)
        return sr_data.ruleset[id];
    else {
        id -= SR_RULESET_MAX;
        if (id < FL_RULESET_MAX)
            return fl_data.ruleset[id - SR_RULESET_MAX];
        else
            return *((const ruleset_t *)&invalid_data);
    }
}

inline const comp_t &get_comp(uint16_t id) {
    if (id < SR_COMP_MAX)
        return sr_data.comp[id];
    else {
        id -= SR_COMP_MAX;
        if (id < FL_COMP_MAX)
            return fl_data.comp[id];
        else
            return *((const comp_t *)&invalid_data);
    }
}

inline const decomp_t &get_decomp(uint16_t id) {
    if (id < SR_DECOMP_MAX)
        return sr_data.decomp[id];
    else {
        id -= SR_DECOMP_MAX;
        if (id < FL_DECOMP_MAX)
            return fl_data.decomp[id];
        else
            return *((const decomp_t *)&invalid_data);
    }
}

inline const list_t &get_list(uint16_t id) {
    if (id < SR_LIST_MAX)
        return sr_data.list[id];
    else {
        id -= SR_LIST_MAX;
        if (id < FL_LIST_MAX)
            return fl_data.list[id];
        else
            return *((const list_t *)&invalid_data);
    }
}

inline const lookup_t &get_lookup(uint16_t id) {
    if (id < SR_LOOKUP_MAX)
        return sr_data.lookup[id];
    else {
        id -= SR_LOOKUP_MAX;
        if (id < FL_LOOKUP_MAX)
            return fl_data.lookup[id];
        else
            return *((const lookup_t *)&invalid_data);
    }
}

inline const envelope_t &get_envelope(uint16_t id) {
    if (id < SR_ENVELOPE_MAX)
        return sr_data.envelope[id];
    else {
        id -= SR_ENVELOPE_MAX;
        if (id < FL_ENVELOPE_MAX)
            return fl_data.envelope[id];
        else
            return *((const envelope_t *)&invalid_data);
    }
}

inline const sample_t &get_sample(uint32_t id) {
    if (id < SR_SAMPLE_MAX)
        return sr_data.sample[id];
    else {
        id -= SR_SAMPLE_MAX;
        if (id < FL_SAMPLE_MAX)
            return fl_data.sample[id];
        else
            return *((const sample_t *)&invalid_data);
    }
}

template <class T>
class list_iter {
    protected:
        uint16_t list_id;
        byte index;
    public:
        list_iter(uint16_t id) {
            list_id = id;
            index = 0;
        }
    
        const T& get() const {
            if (list_id >= 0xFFFE)
                return *((const T*) &invalid_data);
            return ((T*)(&get_list(list_id).data))[index];
        }

        void next() {
            index++;
            if (index*sizeof(T) >= FL_LIST_ELEMENTS) {
                list_id = get_list(list_id).continuation
                index=0;
            }
        }

        bool eof() const {
            return (list_id >= 0xFFFE);
        }
};

#endif