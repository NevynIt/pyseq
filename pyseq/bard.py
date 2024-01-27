import imps, imps.pson
import time
from collections import namedtuple
from pyseq.MIDIMessages import decode, encode
import random

import logging
logger = logging.getLogger("pyseq.bard")

imps.register()

event = namedtuple("event", ('time', 'imp', 'data'))

imps.pson.hanlders.append( (event, imps.pson.Formatter.format_tuple) )

compactformatter = imps.pson.Formatter()
compactformatter.htchar = ''
compactformatter.lfchar = ' '
compactformatter.sort_key = False

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

mode_map = {
    -5: ((('C','Bb'), 'Loc'), (('C#','Db'), 'Ion'), (('D#','Eb'), 'Dor'), (('E#','F'), 'Phr'), (('F#','Gb'), 'Lyd'), (('G#','Ab'), 'Mix'), (('A#','Bb'), 'Aeo')),
    -4: ((('C','Bb'), 'Phr'), (('C#','Db'), 'Lyd'), (('D#','Eb'), 'Mix'), (('E#','F'), 'Aeo'), ((('G',),), 'Loc'), (('G#','Ab'), 'Ion'), (('A#','Bb'), 'Dor')),
    -3: ((('C','Bb'), 'Aeo'), (('D',), 'Loc'), (('D#','Eb'), 'Ion'), (('E#','F'), 'Dor'), (('G',), 'Phr'), (('G#','Ab'), 'Lyd'), (('A#','Bb'), 'Mix')),
    -2: ((('C','Bb'), 'Dor'), (('D',), 'Phr'), (('D#','Eb'), 'Lyd'), (('E#','F'), 'Mix'), (('G',), 'Aeo'), (('A',), 'Loc'), (('A#','Bb'), 'Ion')),
    -1: ((('C','Bb'), 'Mix'), (('D',), 'Aeo'), (('E','Fb'), 'Loc'), (('E#','F'), 'Ion'), (('G',), 'Dor'), (('A',), 'Phr'), (('A#','Bb'), 'Lyd')),
     0: ((('C','Bb'), 'Ion'), (('D',), 'Dor'), (('E','Fb'), 'Phr'), (('E#','F'), 'Lyd'), (('G',), 'Mix'), (('A',), 'Aeo'), (('B','Cb'), 'Loc')),
     1: ((('C','Bb'), 'Lyd'), (('D',), 'Mix'), (('E','Fb'), 'Aeo'), (('F#','Gb'), 'Loc'), (('G',), 'Ion'), (('A',), 'Dor'), (('B','Cb'), 'Phr')),
     2: ((('C#','Db'), 'Loc'), (('D',), 'Ion'), (('E','Fb'), 'Dor'), (('F#','Gb'), 'Phr'), (('G',), 'Lyd'), (('A',), 'Mix'), (('B','Cb'), 'Aeo')),
     3: ((('C#','Db'), 'Phr'), (('D',), 'Lyd'), (('E','Fb'), 'Mix'), (('F#','Gb'), 'Aeo'), (('G#','Ab'), 'Loc'), (('A',), 'Ion'), (('B','Cb'), 'Dor')),
     4: ((('C#','Db'), 'Aeo'), (('D#','Eb'), 'Loc'), (('E','Fb'), 'Ion'), (('F#','Gb'), 'Dor'), (('G#','Ab'), 'Phr'), (('A',), 'Lyd'), (('B','Cb'), 'Mix')),
     5: ((('C#','Db'), 'Dor'), (('D#','Eb'), 'Phr'), (('E','Fb'), 'Lyd'), (('F#','Gb'), 'Mix'), (('G#','Ab'), 'Aeo'), (('A#','Bb'), 'Loc'), (('B','Cb'), 'Ion')),
     6: ((('C#','Db'), 'Mix'), (('D#','Eb'), 'Aeo'), (('E#','F'), 'Loc'), (('F#','Gb'), 'Ion'), (('G#','Ab'), 'Dor'), (('A#','Bb'), 'Phr'), (('B','Cb'), 'Lyd'))
}

def tune2str(tune):
    return compactformatter([(e.imp,decode(e.data)) for e in tune])

def add_clamp(value,add,min_value=0,max_value=127):
    return max(min_value, min(value+add, max_value))

class Bard(imps.Imp):
    def set_imp_data(self, data):
        super().set_imp_data(data)
        self.arrangements = self.imp_data.get("arrangements", {})
        self.sources = self.imp_data.get("sources", {})
    
    def send_midi(self, src, msg):
        self.play([event(time.time(),src,msg),])

    def drop(self, tune=None, arr=None):
        return ()

    def noop(self, tune=None, arr=None):
        return tune

    def reroute(self, tune=(), arr={}):
        while True:
            route = arr.get('route', None)
            if route is None:
                return tune
            
            if route in ('bard.reroute','reroute'):
                logger.warn("Cyclic routing")
                return () #drop everything
            
            logger.debug(f'Routing to: {route}')
            arr = self.get_arrangement(route)
            impN, fncN = self.parse_style(arr.get('style','noop'))
            #a possilbe alternative for patterns would be to yield and use iterator objects instead
            # logger.debug(f'Arranging:\nTune:{tune2str(tune)}\nArrangement:\n{imps.pson.dumps(arr)}')
            tune = getattr(imps.imps[impN], fncN)(tune, arr)

    def replace(self, tune=(), arr={}):
        new_tune = []
        for e in tune:
            msg = list(decode(e.data))
            if msg[0] in ['note_off', 'note_on', 'poly_keypress', 'control_change', 'program_change', 'channel_pressure', 'pitch_bend_change']:
                ch = arr.get('channel', None)
                if ch is not None:
                    msg[1] = ch
                if msg[0] in ['note_off', 'note_on']:
                    velexp = arr.get('velexp', None)
                    vel = arr.get('velocity', None)
                    transp = arr.get('transpose', None)
                    scale = arr.get('scale', None)
                    if scale is not None:
                        msg[2] = 12 * (msg[2] // 12) + scale_map[scale][msg[2] % 12]
                    if velexp:
                        if velexp<0:
                            velexp = 1/velexp
                        msg[3] = int(pow(msg[3]/127.0,1/velexp)*127)
                    if vel is not None:
                        msg[3] = vel
                    if transp is not None:
                        msg[2] = add_clamp(msg[2], transp)
            new_tune.append(event(e.time + arr.get('delay', 0),arr.get('output', e.imp),encode(*msg)))
        return new_tune
    
    def randomize(self, tune=(), arr={}):
        if not 'note_map' in arr:
            arr['note_map'] = {}
        new_tune = []
        for e in tune:
            msg = list(decode(e.data))
            if msg[0] == 'note_on':
                note = None
                while not note:
                    d = arr.get('channel', 0)
                    if d is None:
                        newchan = random.randint(0,15)
                    else:
                        newchan =  add_clamp(msg[1],random.randint(-d,d),0,15)
                    d = arr.get('transpose', 0)
                    newnote =  add_clamp(msg[2],random.randint(-d,d))
                    note = (newchan, newnote)
                    if note in arr['note_map'].values():
                        note = None
                arr['note_map'][(msg[1],msg[2])] = note
                msg[1], msg[2] = note
                d = arr.get('velocity', 0)
                msg[3] = add_clamp(msg[3],random.randint(-d,d))
            elif msg[0] == 'note_off':
                note = (msg[1],msg[2])
                msg[1], msg[2] = arr['note_map'][note]
                del arr['note_map'][note]
            new_tune.append(event(e.time,e.imp,encode(*msg)))
        return new_tune

    def chords(self, tune=(), arr={}):
        new_tune = []
        for e in tune:
            msg = list(decode(e.data))
            root = msg[2]
            if msg[0] in ['note_off', 'note_on', 'poly_keypress']:
                for n in arr['notes']:
                    msg[2] = root + n
                    new_tune.append(event(e.time,e.imp,encode(*msg)))
        return new_tune

    def parse_style(self,style):
        spl = style.split('.')
        if len(spl)==1:
            fncN = style
            impN = 'bard'
        elif len(spl)==2:
            impN = spl[0]
            fncN = spl[1]
        else:
            logger.warn(f'Invalid style/arrangement "{style}"')
            fncN = 'drop'
            impN = 'bard'
        return (impN, fncN)

    def get_arrangement(self, arr_name):
        if arr_name in self.arrangements:
            arr = self.arrangements[arr_name]
            if isinstance(arr, str):
                impN, fncN = self.parse_style(arr)
                self.arrangements[arr_name] = {'style': f'{impN}.{fncN}'}
            else:
                impN, fncN = self.parse_style(arr.get('style', 'noop'))
                arr['style'] = impN + '.' + fncN
        else:
            impN, fncN = self.parse_style(arr_name)
            self.arrangements[arr_name] = {'style': impN + '.' + fncN}
        return self.arrangements[arr_name]

    def play(self, tune):
        logger.debug(f'Arranging: {tune2str(tune)}')
        new_tune = []
        for e in tune:
            #a possilbe alternative for patterns would be to yield and use iterator objects instead
            new_tune += self.reroute((e,), {'route': self.sources.get(e.imp,'default')})
        new_tune.sort(key = lambda e: e.time)
        logger.debug(f'Playing: {tune2str(new_tune)}')
        #ignore time for now
        for e in new_tune:
            if '.' in e.imp:
                impN, fncN = e.imp.split('.')
                getattr(imps.imps[impN], fncN)(e.data)
            else:
                imps.imps[e.imp].play((e,))