import logging
logging.basicConfig(level=logging.DEBUG, filename=__file__+'.log', filemode='w')
logging.info(f"------------- Starting '{__file__}'")
# logging.getLogger("pyseq.FSWrap").setLevel(logging.INFO)
# logging.getLogger("pyseq.bard").setLevel(logging.INFO)
logging.getLogger("imps").setLevel(logging.INFO)


import imps, imps.pson
import pyseq
import rtmidi, rtmidi.midiutil

imps.unfreeze()

def fsinteract(cmd):
    res = imps.imps.fs.fs.send_command(cmd)
    for l in res:
        print(l)

print("Starting interpreter")
import code
localvars = {
    "imps" : imps.imps,
    "fs": fsinteract,
    'respawn': imps.respawn
}
code.interact(local=localvars)

imps.freeze()

logging.info(f"------------- Stopping '{__file__}'")