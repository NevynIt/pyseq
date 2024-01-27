import sys
import imps
from . import FSWrap
import rtmidi, rtmidi.midiutil
import pathlib
from pyseq.MIDIMessages import decode

import logging
logger = logging.getLogger("pyseq.fs")

imps.register()

def resfile(fname):
    return str(pathlib.Path(__file__).parent / fname)

class Synth(imps.Imp):
    def __init__(self, id, data=None):
        super().__init__(id, data)
        self.frozen = True
        self.fs = None

    def unfreeze(self):
        super().unfreeze()
        if self.frozen:
            self.sfonts = self.imp_data['sfonts']
            self.fs_port = self.imp_data['fs_port']
            self.out_port = self.imp_data['out_port']
            self.sfids = [None] * len(self.sfonts)
            self.instr = [{} for i in range(len(self.sfonts))]
            try:
                self.midi_out = rtmidi.midiutil.open_midioutput(self.out_port,interactive=False,client_name="pyseq",port_name=self.out_port)[0]
            except:
                self.midi_out = None
            args = []
            fs_port = [p for p in rtmidi.MidiIn().get_ports() if p.startswith(self.fs_port)]
            if len(fs_port)>0:
                fs_port = fs_port[0].split(' ')[-1]
                args.append('-o')
                args.append(f'midi.winmidi.device={fs_port}')
            
            self.fs = FSWrap.FluidSynthWrapper(args)
            for i, sfont in enumerate(self.sfonts):
                self.sfids[i] = self.fs.load(str(sfont))
                if self.sfids[i]:
                    #TODO: names might be duplicates, reverse the dictionary and search differently
                    self.instr[i] = self.fs.inst(self.sfids[i])
            for chan, prog in self.imp_data['presets'].items():
                sel = False
                if isinstance(prog, str):
                    sfid = 0
                    if self.sfids[sfid] and prog in self.instr[sfid]:
                        bank, num = self.instr[sfid][prog]
                        sel = True
                elif isinstance(prog[1], str):
                    sfid = prog[0]
                    if self.sfids[sfid] and prog[1] in self.instr[sfid]:
                        bank, num = self.instr[sfid][prog[1]]
                        sel = True
                else:
                    sfid, bank, num = prog
                    sel = True
                if sel:
                    self.program_select(preset=num,bank=bank,chan=chan,sfid=sfid)
            self.frozen = False
    
    def freeze(self):
        super().freeze()
        if not self.frozen:
            self.fs.close()
            self.fs = None
            self.midi_out.close_port()
            self.midi_out = None
            self.frozen = True
    
    def program_select(self, preset = 0, bank = 0, chan=0, sfid = 0):
        if sfid >= len(self.sfids) or self.sfids[sfid] is None:
            return
        self.fs.select(chan,self.sfids[sfid],bank,preset)

    def send_midi(self, msg):
        if self.midi_out:
            self.midi_out.send_message(msg)
    
    def get_inst_names(self):
        ret = {}
        for i, id in enumerate(self.sfids):
            if id:
                ret[self.sfonts[i]] = self.instr[i]
        return ret