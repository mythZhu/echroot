#!/usr/bin/env python

import os
import fcntl

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
        self._lockfp = fpath
        self._lockfd = -1
        self._lockid = str(os.getpid())

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, t, v, tb):
        self.release()

    def locked(self):
        return self._lockid == _get_ident(self._lockfp)

    def acquire(self):
        if self.locked(): 
            return
        self._lockfd = open(self._lockfp, 'a+')
        fcntl.flock(self._lockfd, fcntl.LOCK_EX)
        self._lockfd.truncate(0)
        self._lockfd.write(self._lockid)
        self._lockfd.flush()

    def release(self):
        self.locked() and os.remove(self._lockfp)
