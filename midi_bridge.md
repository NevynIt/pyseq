# MIDI Bridge
Hardware interfaces:
 - 3x MIDI ports over USB
 - 1x Serial port over USB
 - 2x Serial ports over GPIO (UART0: TX 0 RX 1 -- UART1 TX 4 RX 5)

Communication interface:
 - messages are received from midi or any serial as 4 bytes, and are sent to a single processing logic, together with the source they came from
 - everything is processed in accordance with the active routing-filtering tables
 - sysex messages addressed to the specific ID on cable 0 on usb midi or any serial are interpreted for configuration
 - ruleset "INIT" is loaded and activated at boot
 - default manuf_ID is 

The sysex commands are:

Hex | Command | Notes
--|--|--
--| **I/O settings** | 
0x10 | Get/Set serial speeds
0x11 | Set heartbeat destinations and frequency | Heartbeat is ALWAYS sent to midi channel 0 at least every 5 seconds to make sure it's possible to know the ID of the device to communicate with it
0x12 | Load I/O settings | manufacturer ID, serial speeds, heartbeat settings
0x13 | Save I/O settings | manufacturer ID, serial speeds, heartbeat settings
0x14 | Set Manufacturer ID
0x15 | Set Channel Names | 3x 8x 7-bit strings
0x16 | Get board unique ID
-- | **RuleSets** | ruleset ID 0-16 are predefined and cannot be overwritten
0x20 | Get ruleset count
0x21 | Get ruleset IDs | 4x 7-bit ID bytes, some IDs might be protected from writing
0x22 | Get ruleset by ID
0x23 | Set ruleset by ID | Max 511 rules, which can refer to max 256 different lookup tables and max 256 sequences
0x24 | Delete ruleset by ID
0x25 | Compile and activate ruleset by ID | This is the only command which actually changes the actual routing behaviour  
-- | **Rules** |
0x30 | Get rule count
0x31 | Get rule IDs | 4x 7-bit ID bytes, user defined, shared by all rule-sets, some might be protected from writing
0x32 | Get rule by ID
0x33 | Set rule by ID
0x34 | Delete rule by ID
-- | **Lookup tables** |
0x40 | Get lookup table count
0x41 | Get lookup table IDs | 4x 7-bit ID bytes, user defined, shared by all rule-sets, some might be protected from writing
0x42 | Get lookup table by ID
0x43 | Set lookup table by ID
-- | **Macros** |
0x40 | Get macro count
0x41 | Get macro IDs | 4x 7-bit ID bytes, user defined, shared by all rule-sets, some might be protected from writing
0x42 | Get macro by ID
0x43 | Set macro by ID

### Get/Set Serial speed sysex request:
Values | meaning | notes
--|--|--
F0 | SysEx start
xx | Manufacturer ID byte 0 - default 00
xx | Manufacturer ID byte 1 - default 36
xx | Manufacturer ID byte 2 - default 36
01 | command: set/get speed
00-02 | Serial interface | 0 = UART0, 1=UART1, 2 = USB
00-7F | UART0 baud rate / 9600 | 0 = unchanged
00-7F | UART1 baud rate / 9600 | 0 = unchanged
00-7F | USB baud rate / 9600 | 0 = unchanged
F7 | SysEx end

### Get/Set Serial speed sysex answer:
Hex | meaning | notes
--|--|--
F0 | SysEx start
xx | Manufacturer ID byte 0 - default 00
xx | Manufacturer ID byte 1 - default 36
xx | Manufacturer ID byte 2 - default 36
10 | answer: current speeds
01-7F | UART0 baud rate / 9600
01-7F | UART1 baud rate / 9600
01-7F | USB baud rate / 9600
F7 | SysEx end

### Base heart beat message:
This message is sent every 5 seconds on cable 0 of the midi interface in sync with the internal clock (as close as possible to when millis() % 5000 == 0) 

Hex | meaning | notes
--|--|--
F0 | SysEx start
xx | Manufacturer ID byte 0 - default 00
xx | Manufacturer ID byte 1 - default 36
xx | Manufacturer ID byte 2 - default 36
00 | heartbeat and internal clock
00-32 | days
00-18 | hours
00-3c | minutes
00-3c | seconds
F7 | SysEx end

## Routing rules
Rules have a a 4x 7-bits ID, a set of things they match, a transformation logic and a destination mask
A rule is composed of:
- 4x ID
- 12x selection mask
- 11x transform
- 8x destination mask
Total: 35 bytes 

### Match
Rules match based on any combination of (12x 7-bit values):
 - bitmask: 000-SSSS 0-CC-HH-MM CCCCCCC CCCCCCC HHHHHHH HHHHHHH MMMMMMM MMMMMMM (8x 7-bit values)
    - S source (4 bit mask)
    - C cable (16 bit mask)
    - H channel (16 bit mask)
    - M message type (16 bit mask)
 - data2 range (min, max) - 2x 7-bit values
 - data3 range (min, max) - 2x 7-bit values

### Transform
Transformation logics are all optional and are applied in the following order:
 - replace message with stored macro (all other transforms are applied to each message in the macro independently)
    - 4x 7-bit value, macro number, 0 = do nothing
 - remapping:
    - for note_on, note_off and poly_keypress messages:
        - remap based on a lookup table
            - 4x 7-bit value, lookup table ID, 0 = do not remap, 1-12 = diatonic scales, 13-127 = other
        - transpose note
            - 1x 7-bit value, DVVVVVV, D=0 up, D=1 down, V = 6-bit transpose value
        - velocity curve remapping
            - 1x 7-bit value (logic TBD), 0 = do not remap
    - for cc and program_change messages:
        - remap based on a lookup table
            - 4x 7-bit value, lookup table ID, 0 = do not remap, 1-12 reserved

### Destination
The destination mask changes ruleset or determines all the ports/cables/channels over which the message is sent:
 - bitmask: 0R-LSSSS 0-LCC-LHH CCCCCCC CCCCCCC HHHHHHH HHHHHHH (6x 7-bit values)
    - R 0=stay with the same ruleset, 1=compile and activate the ruleset defined by the next 4 7-bit bytes (note that activation can be time-consuming)
    - L 0=keep 1=update, Source/cable/channel
    - S source (4 bit mask)
    - C cable (16 bit mask)
    - H channel (16 bit mask)

## Lookup tables
Lookup tables have a 4x 7-bit ID and 128 entries, which define the mapping directly, for a total of 132 bytes

## Macros
Macros have a 4x 7-bit ID, 1x 7-bit length and up to 24x 5x 7-bit entries, for a total of 128 bytes
Each entry is composed of:
 - 1x 7-bit identifying the logic to use to transform the next 3 values (plus the source midi message) into a new message. The logics that come to my mind are:
    - bitmask of changes to apply:
        - port change y/n - new port (2 bit) // data2 (2 bit: 0=no change, 1=add, 2=sub, 3=expcurve) // data3 ((2 bit: 0=no change, 1=add, 2=sub, 3=expcurve))
        - cable change y/n - new cable (4 bit) // message y/n - channel y/n
    - new message/channel (7 bit)
    - data2 modifier (7 bit)
    - data3 modifier (7 bit)