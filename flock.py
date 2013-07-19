#!/usr/bin/env python

import os

def _get_ident(fpath):
    if os.path.exists(fpath):
        fd = open(fpath)
        ident = fd.readline().strip()
        fd.close()
        return ident
    else:
        return None


class FileLock(object):
 
    def __init__(self, fpath):
        self._lock = fpath
        self._this = str(os.getpid())

    def __enter__(self):
        return self.acquire()

    def __exit__(self, t, v, tb):
        self.release()

    def acquire(self):
        owner = _get_ident(self._lock)

        if owner == None:
            fd = open(self._lock, 'w')
            fd.write(self._this)
            fd.close()
            return True

        return owner == self._this

    def release(self):
        if self._this == _get_ident(self._lock):
            os.remove(self._lock)
