import msvcrt
import mido

outp=[p for p in mido.get_output_names() if "FluidSynth" in p][0]

# MIDI setup
outport = mido.open_output(outp)

# Initial transposition level (0 means no transposition)
transposition = 0

# Keyboard to MIDI mapping
keyboard_to_midi = {
    b'a': 60, b'w': 61, b's': 62, b'e': 63, b'd': 64, b'f': 65, b't': 66,
    b'g': 67, b'y': 68, b'h': 69, b'u': 70, b'j': 71, b'k': 72, b'o': 73,
    b'l': 74, b'p': 75, b';': 76, b'\'': 77
}

# Note names
note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def midi_note_to_name(midi_note):
    note_name = note_names[midi_note % 12]
    octave = (midi_note // 12) - 1
    return f"{note_name}{octave}"

print("Press keys to play MIDI notes (press 'q' to exit, 'z' to transpose down, 'x' to transpose up)...", end=' ', flush=True)

try:
    while True:
        if msvcrt.kbhit():  # Check if a key is pressed
            char = msvcrt.getch()  # Read the pressed key

            if char == b'q':  # Exit if 'q' is pressed
                break
            elif char == b'z':  # Transpose down one octave
                transposition -= 12
                print("\nTransposed down", end=': ', flush=True)
                continue
            elif char == b'x':  # Transpose up one octave
                transposition += 12
                print("\nTransposed up", end=': ', flush=True)
                continue

            midi_note = keyboard_to_midi.get(char)
            if midi_note is not None:
                midi_note += transposition
                if 0 <= midi_note < 128:  # Ensure note is within MIDI range
                    outport.send(mido.Message('note_on', note=midi_note, velocity=100))
                    print(midi_note_to_name(midi_note), end=', ', flush=True)
except KeyboardInterrupt:
    pass
finally:
    outport.close()
    print("\nExited.")
