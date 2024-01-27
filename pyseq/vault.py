import inspect
import json
from collections import namedtuple
import importlib
import os.path #for isfile
import shutil #for copy
import datetime
import sys

_vault_data = {}
_vault_handlers = {}

def _get_calling_module():
    module = None
    stack = inspect.stack()
    try:
        # The first frame in the stack is this function, the second is the caller inside vault, the third is the actual caller
        caller_frame = stack[2]
        module = inspect.getmodule(caller_frame[0])
    finally:
        # Clean up the stack to prevent reference cycles
        del stack
    return module

def get_my_data(default = {}, module=None):
    try:
        module = module or _get_calling_module()
        return _vault_data[module.__name__]
    except:
        return default

def _default_getter(module):
    return module.vault_data

def _default_setter(data, module):
    module.vault_data = data

def _noop(*args, **kwargs):
    pass
    
_handlers = namedtuple("_handlers", ('getter', 'setter', 'before_reload', 'after_load', 'token'))

def register(getter = None, setter = None, before_reload = None, after_load = None, token = None, module = None):
    module = module or _get_calling_module()
    if not getter and not setter and not hasattr(module, "get_vault_data") and \
        not hasattr(module, "set_vault_data") and hasattr(module, "vault_data"):

        getter = _default_getter
        setter = _default_setter
        token = module
    else:
        getter = getter or module.get_vault_data
        setter = setter or module.set_vault_data
    
    before_reload = before_reload or (hasattr(module, "on_before_reload") and module.on_before_reload) or _noop
    after_load = after_load or (hasattr(module, "on_after_load") and module.on_after_load) or _noop

    module_name = module.__name__
    _vault_handlers[module_name] = _handlers(getter, setter, before_reload, after_load, token)
    
    #I am not sure this is the best behaviour but I think so...
    after_load(token)

def load_file(fname):
    global _vault_data
    with open(fname,"r") as fs:
        _vault_data = json.load(fs)
    for module_name, handlers in _vault_handlers.items():
        if module_name in _vault_data:
            data = _vault_data[module_name]
            handlers.setter(data, handlers.token)

def save_file(fname):
    global _vault_data
    for module_name, handlers in _vault_handlers.items():
        data = handlers.getter(handlers.token)
        _vault_data[module_name] = data
    if os.path.isfile(fname):
        name, ext = os.path.splitext(fname)
        bkpname = name + "-" + datetime.datetime.now().strftime("%y%m%d%H%M%S") + ext
        shutil.copyfile(fname, bkpname)
    with open(fname,"w") as fs:
        json.dump(_vault_data, fs, indent=4, sort_keys=True) #make it pretty

_module_callbacks = {}

def reload(module):
    global _module_callbacks
    if isinstance(module, str):
        module_name = module
        module = sys.modules[module_name]
    else:
        module_name = module.__name__

    try: 
        handlers = _vault_handlers[module_name]
        before_reload = handlers.before_reload
        after_load = handlers.after_load
    except:
        before_reload = _noop
        after_load = _noop

    # Handle callbacks before reloading the module
    for callback, when in _module_callbacks.get(module_name, []):
        if when in ["before", "both"]:
            callback(module, "before")

    reload_data = before_reload()

    # Reload the module
    reloaded_module = importlib.reload(module)

    after_load(reload_data)

    # Handle callbacks after reloading the module
    for callback, when in _module_callbacks.get(module_name, []):
        if when in ["after", "both"]:
            callback(reloaded_module, "after")

def add_reload_cb(module, callback, when="after"):
    module_name = module.__name__
    if module_name not in _module_callbacks:
        _module_callbacks[module_name] = []
    if (callback, when) not in _module_callbacks[module_name]:
        _module_callbacks[module_name].append((callback, when))

def remove_reload_cb(module, callback):
    module_name = module.__name__
    if module_name in _module_callbacks:
        for cb, when in _module_callbacks[module_name]:
            if cb == callback:
                _module_callbacks[module_name].remove((cb, when))
                break