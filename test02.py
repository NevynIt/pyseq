import traceback
import mido
import threading
import asyncio
import logging
import time
import random

logging.basicConfig(level=logging.DEBUG, filename=__file__+'.log', filemode='w')

def tt():
    return str(time.time() % 100)[:7]

class live_tune():
    def __init__(self, timeout=0.2):
        self.timeout = timeout
        self.q = asyncio.Queue()
        self.ended = False
        self.time = time.time()
    
    async def put(self, msg):
        now = time.time()
        msg.time = now-self.time
        logging.debug(f"{tt()} put {msg}")
        await self.q.put(msg)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.ended:
            raise StopAsyncIteration

        try:
            item = await asyncio.wait_for(self.q.get(),self.timeout)
        except asyncio.TimeoutError:
            self.ended = True
            raise StopAsyncIteration
        
        if item is None:
            self.ended = True
            raise StopAsyncIteration

        return item

class arranger():
    def __init__(self):
        self.out = mido.open_output(mido.get_output_names()[3])
        self.loop = None
        self.tune = None
        self.play_queue = []
        self.new_data = asyncio.Event()

        self.thread = threading.Thread(target=self.loop_thread_main, daemon=True)
        self.thread.start()

    def loop_thread_main(self):
        self.loop = asyncio.new_event_loop()
        self.player_task = self.create_task(self.play_task_main(), 'player')
        self.loop.run_forever()

    async def task_wrapper(self, coro, name):
        task = asyncio.create_task(coro)
        task.set_name(name)
        try:
            await task
        except Exception as e:
            error_traceback = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            logging.error(f"Task {task.get_name()} raised an exception: {e}\n{error_traceback}")

            if task.get_name().startswith('arranger'):
                self.tune = None

    def create_task(self, coro, name):
        asyncio.run_coroutine_threadsafe(self.task_wrapper(coro, name), self.loop)

    async def play_task_main(self):
        while True:
            if len(self.play_queue) == 0:
                logging.debug(f"{tt()} waiting")
                await self.new_data.wait()

            self.new_data.clear()

            self.play_queue.sort(key=lambda m: m.time)

            while len(self.play_queue)>0 and not self.new_data.is_set():
                now = time.time()
                delay = self.play_queue[0].time - now
                delay = (int(delay*10000) + 1)/10000
                if delay <= 0.005:
                    msg = self.play_queue.pop(0)
                    logging.debug(f"{tt()} play {msg}")
                    self.out.send(msg)
                    continue
                
                # logging.debug(f"{tt()} wait {delay}")
                try:
                    await asyncio.wait_for(self.new_data.wait(), delay)
                    logging.debug(f"{tt()} new_data")
                    break
                except asyncio.TimeoutError:
                    pass

    def push(self, msg):
        self.play_queue.append(msg)
        self.new_data.set()

    async def arrange(self, tune, chain):
        src = tune
        for f in chain:
            src = f(src)
        
        t0 = time.time()
        async for msg in src:
            msg.time = t0 + msg.time
            logging.debug(f"{tt()} enqueue {msg}")
            self.push(msg)
        
        logging.info('end of tune')
        self.tune = None

    def post(self, msg):
        if self.loop:
            if not self.tune or self.tune.ended:
                logging.info("new tune")
                self.tune = live_tune()
                self.create_task(self.arrange(self.tune, (f1,f2,f3)), f'arranger-{random.randint(10,99)}')
    
            self.create_task(self.tune.put(msg), f'put-{random.randint(10,99)}')

scale_map = {
    -5: ( 0, 1, 1, 3, 3, 5, 6, 6, 8, 8, 10, 10),
    -4: ( 0, 1, 1, 3, 3, 5, 5, 7, 8, 8, 10, 10),
    -3: ( 0, 0, 2, 3, 3, 5, 5, 7, 8, 8, 10, 10),
    -2: ( 0, 0, 2, 3, 3, 5, 5, 7, 7, 9, 10, 10),
    -1: ( 0, 0, 2, 1, 4, 5, 5, 7, 7, 9, 10, 10),
    0: ( 0, 0, 2, 2, 4, 5, 5, 7, 7, 9, 9, 11),
    1: ( 0, 0, 2, 2, 4, 6, 6, 7, 7, 9, 9, 11),
    2: ( 1, 1, 2, 2, 4, 6, 6, 7, 7, 9, 9, 11),
    3: ( 1, 1, 2, 2, 4, 6, 6, 8, 8, 9, 9, 11),
    4: ( 1, 1, 3, 3, 4, 6, 6, 8, 8, 9, 9, 11),
    5: ( 1, 1, 3, 3, 4, 6, 6, 8, 8, 10, 10, 11),
    6: ( 1, 1, 3, 3, 5, 6, 6, 8, 8, 10, 10, 11)
}

async def f3(src, scale=5):
    #transpose
    async for msg in src:
        if msg.type in ('note_on','note_off'):
            note = msg.note
            note = 12 * (note // 12) + scale_map[scale][note % 12]
            msg = msg.copy(note=note)
        # logging.debug(f"{tt()}f1 {msg}")
        yield msg

async def f2(src, params=None):
    #random velocity
    async for msg in src:
        # if msg.type in ('note_on','note_off'):
        #     msg = msg.copy(velocity=random.randint(60,127))
        # logging.debug(f"{tt()}f2 {msg}")
        yield msg

arp = ((0,0), (4,0.2), (7,0.4),(12,0.6), (7,0.8), (4,1))

async def f1(src, params=None):
    #harmonize
    async for msg in src:
        if msg.type == 'note_on':
            triad = [msg.copy(note=msg.note+dn, time=msg.time+dt+random.randint(0,1)/100) for dn,dt in arp]
            for m in triad:
                # logging.debug(f"{tt()}f3 {m}")
                yield m
                yield mido.Message('note_off', note=m.note, time=m.time+0.5)

# def midi_input_thread():
#     apc = mido.open_input(mido.get_input_names()[0])
#     for msg in apc:
#         arr.post(msg)

arr = arranger()
# midithread = threading.Thread(target=midi_input_thread, daemon=True)
# midithread.start()

import msvcrt

# Keyboard to MIDI mapping
keyboard_to_midi = {
    b'a': 60, b'w': 61, b's': 62, b'e': 63, b'd': 64, b'f': 65, b't': 66,
    b'g': 67, b'y': 68, b'h': 69, b'u': 70, b'j': 71, b'k': 72, b'o': 73,
    b'l': 74, b'p': 75, b';': 76, b'\'': 77
}

# MIDI note number to note name mapping
midi_note_to_name = {
    60: "C4", 61: "C#4", 62: "D4", 63: "D#4", 64: "E4", 65: "F4", 66: "F#4",
    67: "G4", 68: "G#4", 69: "A4", 70: "A#4", 71: "B4", 72: "C5", 73: "C#5",
    74: "D5", 75: "D#5", 76: "E5", 77: "F5"
}

try:
    print("Press keys to play MIDI notes (press 'q' to exit)...")
    while True:
        if msvcrt.kbhit():  # Check if a key is pressed
            char = msvcrt.getch()  # Read the pressed key
            if char == b'q':  # Exit if 'q' is pressed
                break
            note = keyboard_to_midi.get(char)
            if note:
                m = mido.Message('note_on', note=note, velocity=100)
                print(midi_note_to_name[note], end=', ', flush=True)
                arr.post(m)
except KeyboardInterrupt:
    pass
finally:
    # outport.close()
    print("Exited.")