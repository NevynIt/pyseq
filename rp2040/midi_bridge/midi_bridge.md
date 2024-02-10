# MIDI Bridge
(configurable) denotes parameters that can be changed at compile time

### **Hardware interfaces:**
 - 1x Serial port over USB (with 16x cables)
 - 2x Serial ports over GPIO (with 16x cables each)
    - (configurable) pins are by default: UART0 TX 0 RX 1 -- UART1 TX 4 RX 5
 - 1x MIDI port over USB (with 3x cables, the system crashes if I try to add more)
    - as only 3 'cables' can be configured on the midi port apparently, the other cables are used for other functions:
        - anything sent out to 13 comes back from 14, and vice versa, which can be used to create crazy rules (and deadlock the system)
        - anything sent out to 15 comes back from 16, and vice versa, which can be used to create crazy rules (and deadlock the system)
 - (future) stereo audio output over two GPIO PINs using PWM, controlled by a digital synth, controlled by messages over MIDI cable 12
 - (future) stereo audio input over a GPIO ADC PIN using PWM, controlled by a sampler, controlled by messages over MIDI cable 11
 - (future) RGB led strip, connected via SPI, controlled by a visualizer, controlled by messages over MIDI cable 10
 - (future) LCD TFT screen (possibly with buttons or touch), controlled by a visualizer, controlled by messages over MIDI cable 9

### **Functionalities:**
modules can be configured in/out at compile time to balance memory and cpu usage
 - filtering and routing (base - Must)
 - transforming the messages (module - Should)
 - sequencing (module - Should)
 - looping envelopes (module - Could)
 - sound synthesis (future module, using PIO and PWM)
 - sound sampling (future module, using PIO and external memory connected via SPI)
 - rgb leds strip control (future module, using SPI and maybe PIO)
 - display/buttons control (future module, using SPI)

### **Communication interface:**
 - messages are received from midi or any serial as 4 bytes (usb_midi), and are sent to a single processing logic, together with the source they came from
 - everything is processed in accordance with the active routing-filtering tables
 - ruleset 0 is loaded and activated at boot
 - sending a 0xFF aa bb cc to a serial interface changes its behaviour to allow for other interfaces than MIDI, which can be used for:
    - debugging!
    - up/down-loading the ruleset configurations (and all other objects)
        - rules are prepared as human friendly text files, compiled on a pc and then sent over serial this way
    - activate a different ruleset
    - get/set the runtime values as the system runs 

### **Multicore logic:**
 - Core 0
    - listens to messages over the 4 inputs
    - manages configuration messages (stops core 1 when storing data or activating a different ruleset)
    - executes the matching logic, the command actions and populates sequencer slots
        - this includes managing the 'status variables'
    - executes the interrupt that manages stereo audio I/O
 - Core 1
    - cycles through sequencer slots
    - keeps track of what has to be played next for each sequencer slot
    - transforms the notes and sends them out
        - looping envelope values are calculated as part of the transformation when needes
    - if looping, keeps track of the noteon/noteoff messages it sends, to be able to send noteoffs when the loop is stopped
    - (future) fills the looping buffers for audio output of the synth, which is sent as PWM by an interrupt in core0
 - PWM
    - generates an interrupt at FREQ Hz so that core0 can sample two ADCs to form a stereo pair. (default 22100 Hz)
    - the samples go continuously to a fixed length circular array (default 2x FREQ bytes)
    - at the same time, two channel levels of another PWM are set to play the contents of another fixed length circular array (same size)
    - the samples are scaled with a compession enhancer (A-law style) whose lookup table is stored in flash

### **Memory allocation**
assuming 2MB flash on the rp2040, each page is 256 bytes
Page start|Page size|Page end|Content
-|-|-|-
0|4096|4096|Program code
4096|32|4128|configuration data
4128|1|4129|128 rulesets
4129|2048|6177|65535 lists (8 per page)
6177|1024|7201|1024 lookup tables
7201|64|7265|1024 looping envelopes (16 per page)
7265|910|8170|230k of Audio samples
8177|2|8178|8 to 16 bit de-compessor lookup table
8178|16|8192|16 to 8 bit compessor lookup table

object types - on the flash:
 - id is 16 bit
    - 0xFFFF is *the* invalid ID
    - 0x0000 is used as NULL, end of lists
 - ruleset (rule list id)
    - if the list if is 0xFFFF, the entry is unused
    - all rules that match are fired. if multiple subsequent rules match the same list id, the match is checked only once
 - rule (match list id, action, data) - total 3x 16bit
    - if match list id == 0x0000 the previous rule was the last
    - if action == 0xFFFF, then the action is a command, and data represents the 16-bit parameter. Commands can be:
        - set status variables used in message matching
        - select a different ruleset
        - change configuration parameters
        - arm/stop sequencer looping/play
        - start/stop looping envelopes (parameters id, running id)
        - (future) arm/start/stop sampling
        - (future) start/stop sound output
    - param is interpreted by the function that implements the specific command
    - if action != 0xFFFF, then it is a sequence list id
        - data thenepresents a transformation list id (to be performed to each message just before sending)
        - note: sequence 0x0000 is not really executed, it just creates a sequence with just the source message as is
 - match (match type, param) - total 2x 16-bit
    - if match type == 0x0000 the previous was the last
    - match type is composed, bitwise:
        - A. (port, cable, channel, message, data1, data2), or B. (status variable) - 1-bit
        - case A:
            - selector: one of (port, cable, channel, message, data1, data2) - 3-bit
            - comparison: one of (equal, different, inside-range, outside-range, mask) - 3-bit
        - case B:
            - categories: port/cable/channel/message/data1 specific - 5-bit mask (0b00000 = absolute status variable)
            - comparison: one of (equal, different, inside-range, outside-range, mask) - 3-bit
            - identifier: 8-bit (0x00 = no variable)
    - param can be:
        - 1x value
        - 2x min/max range
 - sequence (transformation list id, delta ticks)
    - if transformation list id == 0x0000 the sequence is over
    - if transformation list id == 0xFFFF the sequence loops from the start
 - transformation is 4x bytes, bitwise:
    - if the target/operator/options bytes is 0x0000 the previous was the last
    - target: one of (port, cable, channel, message, data1, data2, status variable, ...) - 4-bit
    - operator: one of (replace/lookup, arythmetic add/subtract/multiply/divide, curves gamma/exp/S, register operations store/load) - 4-bits
    - options: over/under-flow behaviour (clip, wrap, loop), param source (literal, looping envelopes, random, lookup, registers, runtime data, ...) 8-bits
    - params: 2x bytes interpreted bt the operator logic, identifying 2x values, or 1x id of something
 - lookup table (256 8-bit entries)
    - (configurable) up to 2^16 lookup tables are stored on flash (ids are 16-bits), default 2^10 (2^7 is also good if memory is low)
    - if the first byte is 0xFF, the entry is unused
 - looping envelope (attack, decay, hold, release times, min, sustain, max levels, attack, decay, release lookup functions, loop mode, ...) - 16x 8-bits 
    - (configurable) up to 2^16 looping envelope settings can be stored - default 2^10
    - times go exponentially from 1ms (0) to 60s (255) - the formula to get the number of ms is: f(x) = 1.0441^x 
 - list (continuation list id (16-bits), data[Nx 8-bit entries])
    - if the first bytes are 0xFFFF, then the entry is unused
    - (configurable) up to 2^8 data bytes in a list is - 30 8-bit bytes by default
    - (configurable) up to 2^14 lists are stored on flash - all of them by default
 - configuration data is stored in groups of X bytes (divisor of 256, for instance 64)
    - the first byte is:
      - 0xFF when the entry is unused
      - 0x0F when the entry is active and current
      - 0x00 when the entry is obsolete and should not be used
    - this allows to save the configuration data without clearing the flash memory unless all entries in the page are obsolete
    - contents of the configuration page TBD, but should include at least:
      - serial connection speeds

objects in memory:
 - all objects in flash are memory mapped, so are directly accessible as read-only 
 - two semaphores s0 and s1, used to pause core1 from core0
    - s0 and s1 are 0x00 in normal operation
    - core0 raises s0 to ask core1 to stop
    - core1 raises s1 when it actually stops and waits
    - core0 waits for s1 to rise before performing any dangerous operation (like activating a different ruleset)
    - core0 lowers s0 when it's ok to go again
    - core1 waits for s0 to go low before lowering s1 and resuming normal operation
 - global settings:
    - BPM (beats/quarternotes per minute)
    - PPQ (ticks per quarter note)
        - note: changing the tempo will affect the phase of all oscillators and envelopes
 - sequencer slots:
    - there are (configurable) up to 2^16 slots, which means that many independent sequences which can run in parallel - default 256
    - each slot contains:
        - 2x 8-bit semaphores, s0 owned by core0, s1 owned by core1
            - if s0 == 0x00 and s1 == 0x00, the entry is available, and core0 can write on it
            - if s0 > 0x00, the entry is ready to be played
            - if s1 > 0x00, the sequencer is using it (it stores how many times the sequence has been looping)
            - if s0 is 0x00 when s1 > 0x00, core0 is asking to stop the sequence asap
            - when core1 has stopped using the sequence slot, it lowers both s0 and s1 to 0x00
        - 4x 7-bit triggering message (used as the start of the transformation chains)
        - 16-bit starting sequence list id
        - 16-bit transformation list id
        - 16-bit current list id
        - 8-bit next index in the current list
        - 32-bit millis time when the next message must be sent
        - (configurable) list of active notes (each is 4x 8bits: port/cable/channel/note) - default to 96 notes
            - port == 0xFF means unused
 - active looping envelopes (looping env id, phase attacking/decaying/holding/releasing, t0 of the current phase in millis)
    - (configurable) up to 2^8 active looping envelopes - default all of them
    - looping env id == 0xFF means unused entry
 - (future) circular audio buffers (2x stereo 8-bit, configurable length)