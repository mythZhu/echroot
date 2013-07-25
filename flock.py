#!/usr/bin/env python

import os
import fcntl

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
        try:
            lockfd = open(self._lockfp)
            lockid = fd.readline().strip()
            fd.close()
        except:
            lockid = -1

        return self._lockid == lockid

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
