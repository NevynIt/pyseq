import importlib

module_callbacks = {}

def reload(module):
    module_name = module.__name__

    reload_data = None

    # Handle callbacks before reloading the module
    for callback, when in module_callbacks.get(module_name, []):
        if when in ["before", "both"]:
            callback(module, "before")

    if hasattr(module, "on_before_reload"):
        reload_data = module.on_before_reload()

    # Reload the module
    reloaded_module = importlib.reload(module)

    if hasattr(module, "on_after_reload"):
        module.on_after_reload(reload_data)

    # Handle callbacks after reloading the module
    for callback, when in module_callbacks.get(module_name, []):
        if when in ["after", "both"]:
            callback(reloaded_module, "after")

def add(module, callback, when="after"):
    module_name = module.__name__
    if module_name not in module_callbacks:
        module_callbacks[module_name] = []
    if (callback, when) not in module_callbacks[module_name]:
        module_callbacks[module_name].append((callback, when))

def remove(module, callback):
    module_name = module.__name__
    if module_name in module_callbacks:
        for cb, when in module_callbacks[module_name]:
            if cb == callback:
                module_callbacks[module_name].remove((cb, when))
                break