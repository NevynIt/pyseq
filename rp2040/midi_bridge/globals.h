#ifndef GLOBALS_H
#define GLOBALS_H

#include <Arduino.h>
#include <Adafruit_TinyUSB.h>
#include "data_types.h"
#include "flash_data.h"
#include "sram_data.h"
#include "ioconfig.h"

extern Adafruit_USBD_MIDI usb_midi;
extern MIDI_msg_t midiMessage;
extern byte serial_mode[3];
extern byte cmd_buffer[3][MAX_CMD_SIZE*2];
extern uint16_t cmd_buffer_pos[3];

extern uint16_t audio_in[AUDIO_BUFFER_SIZE];
extern uint16_t audio_out[AUDIO_BUFFER_SIZE];

extern byte BPM;
extern uint16_t PPQ;
extern seq_slot_t seq_slots[SEQ_SLOT_NUM];
extern active_envelope_t active_envelopes[ACTIVE_ENVELOPE_NUM];

// NOTE: fl_data is defined as a macro
extern sr_data_t sr_data;
extern byte Semaphore_0;
extern byte Semaphore_1;
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

inline const compr_t &get_compr(uint16_t id) {
    if (id < SR_COMPR_MAX)
        return sr_data.compr[id];
    else {
        id -= SR_COMPR_MAX;
        if (id < FL_COMPR_MAX)
            return fl_data.compr[id];
        else
            return *((const compr_t *)&invalid_data);
    }
}

inline const decompr_t &get_decompr(uint16_t id) {
    if (id < SR_DECOMPR_MAX)
        return sr_data.decompr[id];
    else {
        id -= SR_DECOMPR_MAX;
        if (id < FL_DECOMPR_MAX)
            return fl_data.decompr[id];
        else
            return *((const decompr_t *)&invalid_data);
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