class Formatter(object):
    def __init__(self):
        global hanlders
        self.types = {}
        self.htchar = '    '
        self.lfchar = '\n'
        self.indent = 0
        self.sort_keys = True
        self.sort_fnc = None
        for h in hanlders:
            self.set_formatter(h[0],h[1])

    def set_formatter(self, obj, callback):
        self.types[obj] = callback

    def __call__(self, value, **args):
        for key in args:
            setattr(self, key, args[key])
        formater = self.types[type(value) if type(value) in self.types else Exception]
        return formater(self, value, self.indent)

    def format_Exception(self,value,indent):
        raise ValueError(f"Cannot format {value} as python literal")

    def format_object(self, value, indent):
        return repr(value)

    def format_dict(self, value, indent):
        keys = value.keys()
        if self.sort_keys:
            keys = sorted(keys, key = self.sort_fnc)
        items = [
            self.lfchar + self.htchar * (indent + 1) + repr(key) + ': ' +
            (self.types[type(value[key]) if type(value[key]) in self.types else Exception])(self, value[key], indent + 1)
            for key in keys
        ]
        return '{%s}' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_list(self, value, indent):
        items = [
            (self.types[type(item) if type(item) in self.types else Exception])(self, item, indent + 1)
            for item in value
        ]
        l = sum([len(i) for i in items])+(len(items)-1)*2
        if l<50:
            return '[%s]' % (', '.join(items))
        else:
            items = [self.lfchar + self.htchar * (indent + 1) + i for i in items]
            return '[%s]' % (','.join(items) + self.lfchar + self.htchar * indent)

    def format_tuple(self, value, indent):
        items = [
            (self.types[type(item) if type(item) in self.types else Exception])(self, item, indent + 1)
            for item in value
        ]
        l = sum([len(i) for i in items])+(len(items)-1)*2
        if l<50:
            return '(%s)' % (', '.join(items))
        else:
            items = [self.lfchar + self.htchar * (indent + 1) + i for i in items]
            return '(%s)' % (','.join(items) + self.lfchar + self.htchar * indent)
    
    def format_set(self,value,indent):
        items = [
            (self.types[type(item) if type(item) in self.types else Exception])(self, item, indent + 1)
            for item in value
        ]
        l = sum([len(i) for i in items])+(len(items)-1)*2
        if l<50:
            return '{%s}' % (', '.join(items))
        else:
            items = [self.lfchar + self.htchar * (indent + 1) + i for i in items]
            return '{%s}' % (','.join(items) + self.lfchar + self.htchar * indent)

hanlders=[
    (type(None), Formatter.format_object),
    (str, Formatter.format_object),
    (bool, Formatter.format_object),
    (bytes, Formatter.format_object),
    (int, Formatter.format_object),
    (float, Formatter.format_object),
    (Exception, Formatter.format_Exception),
    (dict, Formatter.format_dict),
    (list, Formatter.format_list),
    (tuple, Formatter.format_tuple)    
]

import ast

def loads(s):
    return ast.literal_eval(s)

def load(fname):
    with open(fname,"r") as fs:
        return loads(fs.read())

def dumps(tosave, **args):
    return Formatter()(tosave, **args)

def dump(tosave, fname, **args):
    with open(fname,"w") as fs:
        fs.write(dumps(tosave, **args))

def clone(src):
    s = dumps(src, htchar='', lfchar='', sort_keys=False)
    dst = loads(s)
    return dst