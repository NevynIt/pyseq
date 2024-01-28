import mido

outp=[p for p in mido.get_output_names() if "FluidSynth" in p]
if len(outp)>0:
    print(outp[0][-1])
else:
    print(0)