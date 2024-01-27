import logging
logger = logging.getLogger("pyseq")

def format_message(data1 = None, data2=None, data3=None):
    if data3 is not None:
        return bytes([data1, data2, data3])
    elif data2 is not None:
        return bytes([data1, data2])
    elif data1 is not None:
        return bytes([data1])
    else:
        return bytes([])

def miscellaneous_function_codes():
    return format_message()

def cable_events():
    return format_message()

def system_common_2bytes(data1, data2):
    return format_message(data1, data2)

def system_common_3bytes(data1, data2, data3):
    return format_message(data1, data2, data3)

def note_off(channel=1, note=60, velocity=0):
    return format_message(0x80 | ((channel-1) & 0x0F), note, velocity)

def note_on(channel=1, note=60, velocity=127):
    return format_message(0x90 | ((channel-1) & 0x0F), note, velocity)

def poly_keypress(channel=1, note=60, pressure=64):
    return format_message(0xA0 | ((channel-1) & 0x0F), note, pressure)

def control_change(channel=1, controller=0, value=0):
    return format_message(0xB0 | ((channel-1) & 0x0F), controller, value)

def program_change(channel=1, program=1):
    return format_message(0xC0 | ((channel-1) & 0x0F), program)

def channel_pressure(channel=1, pressure=64):
    return format_message(0xD0 | ((channel-1) & 0x0F), pressure)

def pitch_bend_change(channel=1, value=8192):
    lsb = (value & 0x7F)
    msb = (value >> 7) & 0x7F
    return format_message(0xE0 | ((channel-1) & 0x0F), lsb, msb)

def single_byte(data):
    return format_message(data)

def sysex_message(data):
    if data[0] != 0xF0 or data[-1] != 0xF7:
        raise ValueError("SysEx data must start with 0xF0 and end with 0xF7")

    if any(byte > 127 for byte in data[1:-1]):
        raise ValueError("All bytes in a SysEx message must be less than 128")

    # Calculate the number of padding bytes needed (0, 1, or 2)
    padding_bytes_needed = (3 - len(data) % 3) % 3

    return data

## old function that I don't think is useful anymore, not maintained
# def decode_message(byte_string):
#     #TODO: I don't know if this works for series of messages from rtmidi. the messages are coming one by one, so it might not be needed to do all the logic for concatenated messages, it could be much easier than this
#     decoded_messages = []
#     i = 0
#     length = len(byte_string)

#     while i < length:
#         # Check for SysEx start byte
#         if byte_string[i] == 0xF0:
#             try:
#                 # Find the end of the SysEx message in the subset of the list
#                 end_index = byte_string[i:].index(0xF7) + i
#             except ValueError:
#                 # If no end byte is found, break the loop
#                 break
#             # Extract the SysEx message
#             sysex_data = byte_string[i:end_index + 1]
#             decoded_messages.append(("sysex_message", sysex_data))
#             # Move the index past the SysEx message
#             i = end_index + 1
#         else:
#             data1 = byte_string[i]
#             if 0x80 <= data1 < 0xC0: # 3 byte messages
#                 if i + 2 < length:
#                     data2, data3 = byte_string[i + 1], byte_string[i + 2]
#                     message = interpret_message(data1, data2, data3)
#                     if message:
#                         decoded_messages.append(message)
#                     # Move the index past this message
#                     i += 3
#                 else:
#                     logger.warn("MIDIMessage decode: partial MIDI message")
#                     break #partial message
#             elif byte_string[i] >= 0xC0: # 2 byte messages
#                 # If there are at least 2 bytes remaining, see if it's a shorter message
#                 data2 = byte_string[i + 1]
#                 if i + 1 < length:
#                     message = interpret_message(data1, data2)
#                     if message:
#                         decoded_messages.append(message)
#                     # Move the index past this message
#                     i += 2
#                 else:
#                     logger.warn("MIDIMessage decode: partial MIDI message")
#                     break

#     # Remaining part of the byte string that was not processed
#     remaining_byte_string = byte_string[i:]

#     return decoded_messages, remaining_byte_string

# def interpret_message(data1, data2, data3=None):
#     # Interpret the message based on the first data byte
#     if data1 >= 0x80 and data1 < 0xF0:
#         channel = data1 & 0x0F
#         if 0x80 <= data1 < 0x90:
#             return ("note_off", channel, data2, data3)
#         elif 0x90 <= data1 < 0xA0:
#             return ("note_on", channel, data2, data3)
#         elif 0xA0 <= data1 < 0xB0:
#             return ("poly_keypress", channel, data2, data3)
#         elif 0xB0 <= data1 < 0xC0:
#             return ("control_change", channel, data2, data3)
#         elif 0xC0 <= data1 < 0xD0:
#             return ("program_change", channel, data2)
#         elif 0xD0 <= data1 < 0xE0:
#             return ("channel_pressure", channel, data2)
#         elif 0xE0 <= data1:
#             value = (data3 << 7) | data2
#             return ("pitch_bend_change", channel, value)
#     elif data1 == 0xF0:
#         # This case is handled in the main loop for SysEx messages
#         pass
#     else:
#         return ("single_byte", data1)

#     return None

def hex(bytes):
    return ' '.join(format(b, '02X') for b in bytes)

def decode(msg):
    # Interpret the message based on the first data byte
    data1, data2, data3, *moredata = tuple(msg) + (None,) * 4
    if data1 is None:
        return ('empty',)
    if data1 == 0xF0:
        return ('sysex', msg)
    if data2 is None:
        return ("single_byte", data1)
    if data1 >= 0x80 and data1 < 0xF0:
        channel = data1 & 0x0F
        if 0x80 <= data1 < 0x90:
            return ("note_off", channel, data2, data3)
        elif 0x90 <= data1 < 0xA0:
            return ("note_on", channel, data2, data3)
        elif 0xA0 <= data1 < 0xB0:
            return ("poly_keypress", channel, data2, data3)
        elif 0xB0 <= data1 < 0xC0:
            return ("control_change", channel, data2, data3)
        elif 0xC0 <= data1 < 0xD0:
            return ("program_change", channel, data2)
        elif 0xD0 <= data1 < 0xE0:
            return ("channel_pressure", channel, data2)
        elif 0xE0 <= data1:
            value = (data3 << 7) | data2
            return ("pitch_bend_change", channel, value)
    logger.warn(f"MIDI message not interpreted: {msg}")
    return None

def encode(msg_type, data1=None, data2=None, data3=None):
    if msg_type == 'empty':
        return bytearray()

    if msg_type == 'sysex':
        return bytearray(data1)

    if msg_type == 'single_byte':
        return bytearray([data1])

    if msg_type in ['note_off', 'note_on', 'poly_keypress', 'control_change', 'program_change', 'channel_pressure', 'pitch_bend_change']:
        if msg_type == 'note_off':
            status_byte = 0x80
        elif msg_type == 'note_on':
            status_byte = 0x90
        elif msg_type == 'poly_keypress':
            status_byte = 0xA0
        elif msg_type == 'control_change':
            status_byte = 0xB0
        elif msg_type == 'program_change':
            status_byte = 0xC0
        elif msg_type == 'channel_pressure':
            status_byte = 0xD0
        elif msg_type == 'pitch_bend_change':
            status_byte = 0xE0
            data2, data3 = data2 & 0x7F, (data2 >> 7) & 0x7F

        status_byte += data1  # data1 is assumed to be the channel

        if msg_type in ['program_change', 'channel_pressure']:
            return bytearray([status_byte, data2])
        else:
            return bytearray([status_byte, data2, data3])

    # Log warning if message type is unknown
    logger.warn(f"Unknown MIDI message type: {msg_type}")
    return None
