#!/usr/bin/python2


'''
Case-insensitive dictionary.
'''


class CIDict(dict):

    def __init__(self):
        self.__keys = {}
        super(CIDict, self).__init__({})

    def __getitem__(self, key):
        return super(CIDict, self).__getitem__(key.lower())

    def __setitem__(self, key, val):
        lower_key = key.lower()
        self.__keys[lower_key] = key
        super(CIDict, self).__setitem__(lower_key, val)

    def __delitem__(self, key):
        lower_key = key.lower()
        del self.__keys[lower_key]
        super(CIDict, self).__delitem__(lower_key)

    def has_key(self, key):
        return super(CIDict, self).__contains__(key.lower())

    __contains__ = has_key

    def get(self, key, default):
        return super(CIDict, self).get(key.lower(), default)

    def keys(self):
        return self.__keys.values()

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    @classmethod
    def fromkeys(cls, keys, default=None):
        cidict = CIDict()
        for k in keys:
            cidict[k] = default
        return cidict

# vim:ts=4 sts=4 sw=4 et
