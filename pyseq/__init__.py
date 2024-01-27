import imps
import logging
logger = logging.getLogger("pyseq")
logging.getLogger('rtmidi.midiutil').setLevel(logging.ERROR)
import rtmidi

logger.info(f"in_ports: {rtmidi.MidiIn().get_ports()}")
logger.info(f"out_ports: {rtmidi.MidiOut().get_ports()}")

imps.register()