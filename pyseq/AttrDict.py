class AttrDict:
    def __init__(self):
        super().__setattr__("_AttrDictDataInternal", {})

    def __contains__(self, key):
        return key in self._AttrDictDataInternal

    def __iter__(self):
        return iter(self._AttrDictDataInternal)

    def __setattr__(self, key, value):
        if key == '_AttrDictDataInternal':
            raise "Cannot replace internal _AttrDictDataInternal"
        else:
            self._AttrDictDataInternal[key] = value

    def __getattr__(self, key):
        return self._AttrDictDataInternal[key]

    def __delattr__(self, key):
        del self._AttrDictDataInternal[key]

    def __getitem__(self, key):
        if isinstance(key,int):
            key = str(key)
        return self._AttrDictDataInternal[key]

    def __setitem__(self, key, value):
        self._AttrDictDataInternal[key] = value

    def __delitem__(self, key):
        del self._AttrDictDataInternal[key]
    
    def __str__(self):
        return str(self._AttrDictDataInternal)
    
    def __repr__(self):
        return repr(self._AttrDictDataInternal)
