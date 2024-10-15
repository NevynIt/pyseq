import mido

inp=[p for p in mido.get_input_names() if "FluidSynth" in p]
if len(inp)>0:
    print(inp[0][-1])
else:
    print(0)