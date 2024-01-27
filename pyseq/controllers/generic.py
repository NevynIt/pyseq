import rtmidi
import imps
import logging
import threading
import time

logger = logging.getLogger("pyseq")

vault_data = imps.get_my_data()
imps.register()

class midi_interface(imps.Imp):
    def __init__(self, id, data=None):
        super().__init__(id, data)
        self.midi_in = None
        self.in_port = None
        self.midi_out = None
        self.out_port = None
    
    def unfreeze(self):
        super().unfreeze()
        in_port = self.imp_data.get('in_port', None)
        if not self.midi_in and self.in_port != in_port:
            if self.midi_in:
                self.midi_in.close_port()
                logger.info(f"{self.id} input closed")
            try:
                self.midi_in, pname = rtmidi.midiutil.open_midiinput(in_port,interactive=False,client_name="pyseq",port_name=in_port)
                self.in_port = in_port
                logger.info(f"{self.id} input opened '{pname}'")
            except:
                self.midi_in = None
            if self.midi_in:
                if self.imp_data.get('polling', True) == True:
                    self.polling = True
                    self.polling_stop_event = threading.Event()
                    self.polling_interval = self.imp_data.get('polling_interval', 0.1)
                    self.polling_thread = threading.Thread(target=self._polling_loop)
                    self.polling_thread.start()
                else:
                    self.polling = False
                    self.midi_in.set_callback(self.midi_callcack)
                    self.midi_in.set_error_callback(self.midi_error_callback)
        out_port = self.imp_data.get('out_port', None)
        if not self.midi_out and self.out_port != out_port:
            if self.midi_out:
                self.midi_out.close_port()
                logger.info(f"{self.id} output closed")
            try:
                self.midi_out, pname = rtmidi.midiutil.open_midioutput(out_port,interactive=False,client_name="pyseq",port_name=out_port)
                self.out_port = out_port
                logger.info(f"{self.id} output opened '{pname}'")
            except:
                self.midi_out = None

    def freeze(self):
        super().freeze()
        if self.midi_in:
            if self.polling:
                self.polling_stop_event.set()
            self.midi_in.close_port()
            logger.info(f"{self.id} input closed")
            self.midi_in = None

        if self.midi_out:
            self.midi_out.close_port()
            logger.info(f"{self.id} output closed")
            self.midi_out = None

    def send_midi(self, msg):
        if self.midi_out:
            self.midi_out.send_message(msg)

    def get_split(self, msg):
        return 0

    def _get_message(self):
        try:
            return self.midi_in.get_message()
        except:
            logger.exception('Error in _get_message')

    def _polling_loop(self):
        """The polling loop for reading MIDI messages when polling is enabled."""
        while not self.polling_stop_event.is_set():
            msg = self._get_message()
            while msg:
                self.midi_callcack( msg )
                msg = self._get_message()
            time.sleep(self.polling_interval)

    def midi_callcack(self, msg, data=None):
        try:
            split = self.get_split(msg[0])
            if split == 0:
                src = self.id
            else:
                src = f'{self.id}.{split}'
            imps.imps.bard.send_midi(src, msg[0])
        except:
            logger.exception(f"Exception in {self.id}.midi_callcack")

    def midi_error_callback(self, error, message, data=None):
        logger.warning(f"Midi error from {self.id}: {error}-{message}")