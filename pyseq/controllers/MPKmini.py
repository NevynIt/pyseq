import imps
from . import generic

imps.register()

class MPKmini(generic.midi_interface):
    def get_split(self, msg):
        chan = msg[0] & 0x0F
        return chan
