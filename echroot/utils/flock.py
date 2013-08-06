#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import errno

class FileLockError(Exception): 
    """ Base exception class for FileLock class"""
    pass

class PidFileLock(object):
    """ PidFileLock implemented via a Unix PID file.

        A lock's PID file contains a singe line, indicating 
        the process ID (PID) of the owner. This lock is best
        used in a context manager fashion through the 'with'
        statement.
    """
 
    def __init__(self, fpath, timeout=None):
        """ Prepare the file lock.

            Specify @fpath as the file or directory to lock.
            If @fpath is a common file, lock file will be
            located in the parent directory of @fpath. If
            @fpath is a directory, lock file will be located
            in the @fpath. If @timeout is `None`, block when 
            acquire. 
        """
        fbase = ".%s.lock" % os.path.basename(fpath)
        fdir = not os.path.isdir(fpath) and os.path.dirname(fpath) or fpath

        self._lockfp = os.path.join(fdir, fbase)
        self._lockid = os.getpid()
        self._timeout = timeout

    def locked(self):
        """ Test if @self is the lock's owner.

            Return `True` if the current process ID matches
            the PID recorded in the target lock's file.
        """
        try:
            lockfs = open(self._lockfp, 'r')
            lockid = int(lockfs.readline().strip())
            lockfs.close()
        except:
            lockid = -1

        return self._lockid == lockid

    def acquire(self):
        """ Acquire the lock.

            Try to create PID file for this lock. If the lock
            is in use, wait util it is available unless the 
            timeout has been set.
        """
        if self.locked(): 
            return

        start_time = time.time()

        while True:
            try:
                oflags = (os.O_CREAT | os. O_EXCL | os.O_WRONLY)
                lockfd = os.open(self._lockfp, oflags)
            except OSError, err:
                if err.errno != errno.EEXIST:
                    raise
                if self._timeout is not None and \
                   time.time() - start_time >= self._timeout:
                    raise FileLockError("Failed to acquire '%s'." % self._lockfp)
                else:
                    time.sleep(1)
            else:
                os.write(lockfd, "%d\n" % self._lockid)
                os.close(lockfd)
                return

    def release(self):
        """ Release the lock.
            Remove the lock's PID file to release the lock.
        """
        self.locked() and os.unlink(self._lockfp)

    def __enter__(self):
        """ Activated when enter into the `with` block.
            The lock is acquired automatically.
        """
        self.acquire()
        return self

    def __exit__(self, t, v, tb):
        """ Activated when exit from the `with` block.
            The lock is released automatically.
        """
        self.release()

    def __del__(self):
        """ This destructor tries to perform correctly. 
            Please make sure that it can be called as 
            expected.
        """
        try:
            self.release()
        except:
            pass

FileLock = PidFileLock
