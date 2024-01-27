import subprocess
import pathlib
import re
import threading, queue
import logging
import imps

imps.register()

logger = logging.getLogger("pyseq.FSWrap")

class FluidSynthWrapper:
    def __init__(self, args=[]):
        # Build the command string
        global vault_data
        FSPath = vault_data.get('FSPath', '')

        command = str(pathlib.Path(FSPath) / "fluidsynth")
        
        logger.debug([command] + args)
        # Start the FluidSynth process
        self.process = subprocess.Popen([command] + args, 
                                        stdin=subprocess.PIPE, 
                                        stdout=subprocess.PIPE,
                                        universal_newlines = True,
                                        cwd = FSPath,
                                        startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.DETACHED_PROCESS))

        # Set up a queue to hold the output
        self.queue = queue.Queue()

        # Start a thread to read the output of the process
        self.reader_thread = threading.Thread(target=self._reader)
        self.reader_thread.daemon = True
        self.reader_thread.start()

        res = self.get_response()

    def _reader(self):
        # Read lines from the process's stdout and put them in the queue
        # for line in iter(self.process.stdout.readline, ''):
        #     self.queue.put(line)
        buf = ''
        while True:
            c = self.process.stdout.read(1)
            if c=='':
                break

            if c == '\n':
                self.queue.put(buf)
                buf = ''
            elif buf == '' and c == '>':
                self.process.stdout.read(1)
                self.queue.put("> ")
            else:
                buf += c

    def get_response(self):
        # Collect the response
        response = []
        while True:
            try:
                line = self.queue.get(timeout=0.1)
                if line == '> ':
                    break
                logger.debug(line)
                response.append(line.strip())
            except queue.Empty:
                break  # No more lines in the queue

        return response

    def send_command(self, command):
        # Send a command to the FluidSynth console
        logger.debug('> ' + command)
        print(f"{command}", file=self.process.stdin, flush=True)
        return self.get_response()

    def close(self):
        # Close the FluidSynth process
        self.send_command('quit')
        self.process.terminate()
    
    def load(self, fname):
        res = self.send_command(f"load '{fname}'")
        if len(res) == 1:
            m = re.match('loaded SoundFont has ID (\d+)', res[0])
            if m:
                return m.groups()[0]
        logger.warning(f"Unable to load {fname}")
        return None

    def inst(self, sfont):
        res = self.send_command(f"inst {sfont}")
        inst_dict = {}
        for l in res:
            m = re.match('(\d\d\d)-(\d\d\d) (.*)',l)
            if m:
                bank,num,name = m.groups()
                inst_dict[name] = (int(bank),int(num))
        return inst_dict

    def select(self,chan,sfont,bank,prog):
        self.send_command(f"select {chan} {sfont} {bank} {prog}")

    def noteon(self,chan=0,key=60,vel=60):
        self.send_command(f"noteon {chan} {key} {vel}")

    def noteoff(self,chan=0,key=60,vel=60):
        self.send_command(f"noteon {chan} {key}")