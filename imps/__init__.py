import importlib
import threading
import inspect
import json
from collections import namedtuple
import os.path
import shutil
import datetime
import sys
import importlib.resources
import logging
import pathlib
from . import pson
import ast

logger = logging.getLogger("imps")

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

def get_default_module_data(module):
    if isinstance(module, str):
        module_name = module
        module = sys.modules[module_name]
    else:
        module_name = module.__name__
    
    if hasattr(module, "get_default_data"):
        return module.get_default_data()
    
    logger.debug(f"no default for {module_name}")
    return {}

def get_my_data(default = None):
    module = _get_calling_module()
    module_name = module.__name__
    if module_name in _global_vault_data:
        return _global_vault_data[module_name]
    if default:
        return default

    return get_default_module_data(module)

def _default_getter(module):
    return module.vault_data

def _default_setter(data, module):
    module.vault_data = data

def _noop(*args, **kwargs):
    pass
    
_handlers = namedtuple("_handlers", ('getter', 'setter'))

def register(getter = None, setter = None):
    module = _get_calling_module()
    module_name = module.__name__
    logger.info(f"Registering '{module_name}'")

    if hasattr(module, "get_vault_data"):
        getter = getter or module.get_vault_data
    else:
        getter = getter or (lambda: _default_getter(module))

    if hasattr(module, "set_vault_data"):
        setter = setter or module.set_vault_data
    else:
        setter = setter or (lambda d: _default_setter(d, module))
    
    if module_name in _module_data_handlers:
        first_time = False
    else:
        first_time = True
    
    _module_data_handlers[module_name] = _handlers(getter, setter)

    #if first_time, it should load "imps.pson" from the module folder and integrate it
    #in the existing _global_vault_data, however without overwriting what was already
    #put there by modules imported before
    load_module_file("imps.pson", True, False, module)
    return first_time

def _deep_update(original, updates):
    if not isinstance(original, dict) or not isinstance(updates, dict):
        return updates

    for key, value in updates.items():
        if value is None:
            original.pop(key, None)
        elif key in original and isinstance(original[key], dict) and isinstance(value, dict):
            _deep_update(original[key], value)
        else:
            original[key] = value

    return original

def _shallow_update(original, updates):
    if not isinstance(original, dict) or not isinstance(updates, dict):
        return original

    for key, value in updates.items():
        if key not in original:
            original[key]= value
    
    if "imps" in updates and "imps" in original:
        _shallow_update(original["imps"], updates["imps"])

def load_module_file(fname, shallow=False, force=True, module=None):
    module = module or _get_calling_module()
    if isinstance(module, str):
        module = sys.modules[module]
    data_file = importlib.resources.files(module.__package__).joinpath(fname)
    load_file(str(data_file), shallow, force)

def save_module_file(fname, subtree='', merge=False, module=None):
    module = module or _get_calling_module()
    if isinstance(module, str):
        module = sys.modules[module]
    data_file = importlib.resources.files(module.__package__).joinpath(fname)
    save_file(str(data_file), subtree, merge)

def _load(fname):
    if fname.lower().endswith('.json'):
        with open(fname,"r") as fs:
            return json.load(fs)
    elif fname.lower().endswith('.pson'):
        with open(fname,"r") as fs:
            return ast.literal_eval(fs.read())
    else:
        raise RuntimeError(f"Unsupported file '{fname}'")

def _save(tosave, fname):
    if fname.lower().endswith('.json'):
        with open(fname,"w") as fs:
            json.dump(tosave, fs, indent=4, sort_keys=True)
    elif fname.lower().endswith('.pson'):
        with open(fname,"w") as fs:
            dumps = pson.Formatter()
            fs.write(dumps(tosave))
    else:
        raise RuntimeError(f"Unsupported file '{fname}'")

def load_file(fname, shallow=False, force=True):
    global _global_vault_data
    if not os.path.isfile(fname) and not force:
        return
    
    if shallow:
        logger.info(f"Shallow loading '{fname}'")
    else:
        logger.info(f"Loading '{fname}'")

    newdata = _load(fname)

    if shallow:
        _shallow_update(_global_vault_data, newdata)
    else:
        _deep_update(_global_vault_data, newdata)

    for module_name, handlers in _module_data_handlers.copy().items():
        if module_name in _global_vault_data:
            data = _global_vault_data[module_name]
            handlers.setter(data)

def save_file(fname, subtree='', merge=False, update=True):
    global _global_vault_data
    if subtree:
        logger.info(f"saving subtree '{subtree}' in '{fname}'")
    else:
        logger.info(f"saving '{fname}'")

    if update:
        for module_name, handlers in _module_data_handlers.items():
            if module_name.startswith(subtree):
                data = handlers.getter()
                _global_vault_data[module_name] = data
    
    tosave = dict([(k,v) for k,v in _global_vault_data.items() if k.startswith(subtree)])

    if merge and os.path.isfile(fname):
        existing_data = _load(fname)
        tosave = _deep_update(existing_data, tosave)

    if os.path.isfile(fname):
        name, ext = os.path.splitext(fname)
        bkpname = name + "-" + datetime.datetime.now().strftime("%y%m%d%H%M%S") + ext
        shutil.copyfile(fname, bkpname)

    _save(tosave, fname)

def reload(module):
    global _reload_callbacks
    if isinstance(module, str):
        module_name = module
        module = sys.modules[module_name]
    else:
        module_name = module.__name__

    logger.info(f"reloading module '{module_name}'")
    # Handle callbacks before reloading the module
    for callback, when in _reload_callbacks.get(module_name, []):
        if when in ["before", "both"]:
            callback(module, "before")


    if hasattr(module, "on_before_reload"):
        module.on_before_reload()

    # Reload the module
    reloaded_module = importlib.reload(module)

    # Handle callbacks after reloading the module
    for callback, when in _reload_callbacks.get(module_name, []):
        if when in ["after", "both"]:
            callback(reloaded_module, "after")

def add_reload_cb(module, callback, when="after"):
    module_name = module.__name__
    if module_name not in _reload_callbacks:
        _reload_callbacks[module_name] = []
    if (callback, when) not in _reload_callbacks[module_name]:
        _reload_callbacks[module_name].append((callback, when))

def remove_reload_cb(module, callback):
    module_name = module.__name__
    if module_name in _reload_callbacks:
        for cb, when in _reload_callbacks[module_name]:
            if cb == callback:
                _reload_callbacks[module_name].remove((cb, when))
                break
            
class _imps_impl:
    def __init__(self):
        super().__setattr__("_Imps_Dict_Internal", {})
    
    def __contains__(self, key):
        return key in self._Imps_Dict_Internal

    def __iter__(self):
        return iter(self._Imps_Dict_Internal)
    
    def __getattr__(self, key):
        return self._Imps_Dict_Internal[key]

    def __getitem__(self, key):
        if isinstance(key,int):
            key = str(key)
        return self._Imps_Dict_Internal[key]

    def __str__(self):
        return str(self._Imps_Dict_Internal)
    
    def __repr__(self):
        return repr(self._Imps_Dict_Internal)

class Imp:
    def __init__(self, id, data = None):
        self.id = id
        self.set_imp_data(data or self.get_default_data())

    def get_imp_data(self):
        return self.imp_data

    def set_imp_data(self,data):
        self.imp_data = data

    def get_default_data(self):
        return get_default_imp_data(self.__class__.__module__, self.__class__.__name__)

    #TODO: should return a success/fail, and imps should not retry after success
    def freeze(self):
        # logger.debug(f"freezing {self.id}")
        pass
    
    #TODO: should return a success/fail, and imps should not retry after success
    def unfreeze(self):
        # logger.debug(f"unfreezing {self.id}")
        pass

def get_default_imp_data(module, clname):
    if isinstance(module, str):
        module_name = module
        module = sys.modules[module_name]
    else:
        module_name = module.__name__

    imp_name = module_name + '.' + clname
    if imp_name in _global_vault_data:
        return _global_vault_data[imp_name]

    logger.debug(f"no default for {imp_name}")
    return {}
            
def spawn():
    global imps, imps_lock, vault_data, respawn_set, _spawning, _frozen
    if _spawning:
        return
    with imps_lock:
        _spawning = True
        imps_dict = imps._Imps_Dict_Internal
        #store a copy of the vault data we'll use in this cycle
        vdata = vault_data["imps"].copy()
        #identify which modules to reload
        reload_queue = set()
        while respawn_set:
            id = respawn_set.pop()
            if id in imps_dict:
                reload_queue.add(imps_dict[id].__class__.__module__)

        #check if we have the right ones or they need to respawn
        remove = set()
        for id in imps_dict:
            imp = imps_dict[id]
            mod = imp.__class__.__module__
            cl = imp.__class__
            if id not in vdata or mod in reload_queue or \
                    mod != vdata[id]["module"] or \
                    cl.__name__ != vdata[id]["class"]:
                logger.info(f"freezing and removing '{id}'")
                imp.freeze()
                vdata[id]["data"] = imp.get_imp_data()
                remove.add(id)

        #reload the modules
        while reload_queue:
            module = reload_queue.pop()
            reload(module)

        #create/replace the missing ones
        for id in vdata:
            if not id in imps_dict or id in remove:
                module_name = vdata[id]["module"]
                clname = vdata[id]["class"]
                logger.info(f"spawning '{id}': '{module_name}.{clname}'")
                try:
                    module = importlib.import_module(module_name)
                    factory = getattr(module, clname)
                except Exception:
                    factory = None
                    logger.exception("(Imps) import failed")
                    
                if not factory:
                    continue
                
                def_data = get_default_imp_data(module,clname)

                try:
                    data = vdata[id]["data"]
                except:
                    data = {}

                data.update(dict([(k,v) for k,v in def_data.items() if k not in data]))

                try:
                    imp = factory(id,data)
                except:
                    imp = None
                    logger.exception("(Imps) creation failed")
                if imp:
                    imps_dict[id] = imp
                    if id in remove:
                        remove.remove(id)
        while remove:
            id = remove.pop()
            del imps_dict[id]

        #unfreeze all imps (or ping unfrozen ones)
        if not _frozen:
            for key, imp in imps_dict.items():
                try:
                    imp.unfreeze()
                except:
                    logger.exception(f"Unfreezing {key} raised an exception")
        
        _spawning = False

class _worker_thread_impl(threading.Thread):
    def __init__(self):
        super().__init__(name="imps.spawn", daemon=True)
        self.stop_event = threading.Event()
    
    def run(self):
        while not self.stop_event.wait(vault_data["period"]):
            spawn()

def respawn(key):
    if isinstance(key,int):
        key = str(key)
    respawn_set.add(key)
    spawn()

def get_vault_data():
    global vault_data
    for id in imps:
        vault_data["imps"][id]["data"] = imps[id].imp_data
    return vault_data

def set_vault_data(data):
    global vault_data
    vault_data = data
    spawn()

def unfreeze():
    global _worker_thread, _frozen, imps_lock, imps
    logger.info("Unfreezing all")
    _frozen = False
    with imps_lock:
        for key, imp in imps._Imps_Dict_Internal.items():
            try:
                imp.unfreeze()
            except:
                logger.exception(f"Unfreezing {key} raised an exception")
    _worker_thread.start()

def freeze():
    global _worker_thread, _frozen, imps_lock, imps
    logger.info("Freezing all")
    _frozen = True
    _worker_thread.stop_event.set()
    _worker_thread = _worker_thread_impl()
    with imps_lock:
        for imp in imps._Imps_Dict_Internal.values():
            imp.freeze()

#make sure these are never replaced for new ones, even on reload
_global_vault_data = globals().get("_global_vault_data", {})
_module_data_handlers = globals().get("_module_data_handlers", {})
_reload_callbacks = globals().get("_reload_callbacks", {})
_spawning = globals().get("_spawning", False)
_frozen = globals().get("_frozen", True)
imps = globals().get("imps", _imps_impl())
imps_lock = globals().get("imps_lock", threading.RLock())
respawn_set = globals().get("respawn_set", set())

vault_data = get_my_data()
if register():
    #the first time the module is loaded:
    #load imps.pson from the folder where __main__ is, if available
    data_file = pathlib.Path(sys.modules["__main__"].__file__).parent.joinpath("imps.pson")
    if data_file.is_file():
        load_file(str(data_file))

_worker_thread = globals().get("_worker_thread", _worker_thread_impl())

spawn()