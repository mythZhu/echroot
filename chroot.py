#!/usr/bin/env python

import os
import fcntl
import subprocess

from elf import ElfObject
from flock import FileLock

class Chroot(object):

    def __init__(self, chrootdir, execute = "/bin/bash"):
        self._rootdir = chrootdir
        self._execute = execute

    def _determine_arch(self, rootdir, *checks):
        if not checks:
            checks = ["/bin/bash", "/sbin/init"]

        checks  = [ os.path.join(rootdir, chk.lstrip('/')) for chk in checks ]
        elfobjs = [ ElfObject(chk) for chk in checks if os.path.exists(chk) ]

        for obj in elfobjs:
            if not obj.machine: 
                continue
            return obj.machine
        else:
            return None

    def _setup_library(self, libname):
        pass

    def _setup_emulator(self, rootdir, arch):
        pass

    def _setup_workaround(self, hostarch, guestarch):
        # case 1: same architecture
        if hostarch == guestarch: 
            return

        # case 2: compatible architecture
        known_schemes = {('x86-64', 'Intel 80386') : 'ia32-libs',
                         ('ARM64' , 'ARM')         : 'ia32-libs'}
        if (hostarch, guestarch) in known_schemes.keys():
            libname = known_schemes[(hostarch, guestarch)]
            self._setup_library(libname)
            return

        # defult case
        guestarch and self._setup_emulator(self._rootdir, guestarch)

    def _chroot(self):
        # determine architecture 
        # setup workaround according to resolved arch
        hostarch  = self._determine_arch("/")
        guestarch = self._determine_arch(self._rootdir)
        self._setup_workaround(hostarch, guestarch)
        
        # chroot into chrootdir
        # execute specify command
        def oschroot():
            os.chroot(self._rootdir)
            os.chdir('/')

        try:
            print "Launching shell. Exit to continue."
            print "----------------------------------"
            subprocess.call(self._execute, preexec_fn = oschroot, shell=True)

        finally:
            pass

    def chroot(self):
        # try to lock chrootdir
        # many-to-one not allowed
        lockname = '.chroot.lock'
        lockpath = os.path.join(self._rootdir, lockname)
        with FileLock(lockpath) as locked:
            if locked:
                self._chroot()
            else:
                print "Directory '%s' is busy now" % self._rootdir


if __name__ == '__main__':
    chroot = Chroot('/tmp/jail')
    chroot.chroot()
