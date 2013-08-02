#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import subprocess

from elf import ElfObject, is_elf
from dup import Dupping, DuppingError
from bind import Binding, BindingError
from path import norm_path, cano_path
from qemu import setup_qemu_emulator, unset_qemu_emulator
from flock import FileLock

def what_arch(rootdir, checks):
    for chk in checks:
        path = norm_path(chk, rootdir)
        arch = is_elf(path) and ElfObject(path).machine
        if arch: return arch
    else: 
        return None

class ChrootError(Exception):
    pass

class Chroot(object):

    FILECHKS = ( "/bin/sh",
                 "/sbin/init", )

    DIRBINDS = ( "/proc/:/proc/",
                 "/proc/sys/fs/binfmt_misc/:/proc/sys/fs/binfmt_misc/",
                 "/sys/:/sys/",
                 "/dev/:/dev/",
                 "/dev/pts/:/dev/pts/",
                 "/dev/shm/:/dev/shm/",
                 "/var/lib/dbus/:/var/lib/dbus/",
                 "/var/run/dbus/:/var/run/dbus/",
                 "/var/lock/:/var/lock/", )

    FILEDUPS = ( "/etc/resolv.conf:/etc/resolv.conf",
                 "/etc/mtab:/etc/mtab", )

    def __init__(self, rootdir, execute="/bin/sh"):
        self._rootdir = rootdir
        self._execute = execute

        self._bindings = []
        self._duppings = []
        self._interpre = None

    def _setup_bindings(self, dirbinds=DIRBINDS):
        for dirbind in dirbinds:
            try:
                splits = dirbind.split(':')
                olddir = splits[0].strip()
                newdir = cano_path(splits[1].strip(), self._rootdir)
                binding = Binding(olddir, newdir, *splits[2:])
            except BindingError:
                continue

            binding.bind()
            binding.binded() and self._bindings.append(binding)

    def _setup_duppings(self, filedups=FILEDUPS):
        for filedup in filedups:
            try:
                splits  = filedup.split(':')
                srcfile = splits[0].strip()
                dstfile = norm_path(splits[1].strip(), self._rootdir)
                dupping = Dupping(srcfile, dstfile)
            except DuppingError:
                continue

            dupping.dup()
            dupping.dupped() and self._duppings.append(dupping)

    def _setup_interpre(self):
        if not self.arch:
            raise ChrootError("Arch of '%s' is unknown." % self._rootdir)

        if self.arch == what_arch('/', self.FILECHKS):
            self._interpre = "native"
        else:
            self._interpre = setup_qemu_emulator(self._rootdir, self.arch)

        if not self._interpre:
            raise ChrootError("No interpreter for %s ELF." % self.arch)

    def _unset_bindings(self):
        for binding in reversed(self._bindings):
            binding.unbind()

    def _unset_duppings(self):
        for dupping in self._duppings:
            dupping.undup()

    def _unset_interpre(self):
        if not self._interpre:
            return

        unset_qemu_emulator(self._rootdir, self._interpre)

    def _kill_processes(self):
        for proc in self.processes:
            try:
                os.kill(proc, 9)
            except:
                pass

    def _setup(self):
        self._setup_bindings()
        self._setup_duppings()
        self._setup_interpre()

    def _unset(self):
        self._kill_processes()
        self._unset_interpre()
        self._unset_duppings()
        self._unset_bindings()

    def _chroot(self):
        def oschroot():
            os.chroot(self._rootdir)
            os.chdir('/')

        try:
            print "Launching shell. Exit to continue."
            print "----------------------------------"

            subprocess.call(self._execute, preexec_fn = oschroot, shell=True)

        except Exception, e:
            print "%s - %s" % (self._execute, e)

    def chroot(self):
        # try to lock chrootdir
        # many-to-one not allowed
        with FileLock(self._rootdir) as flock:
            try:
                self._setup()
                self._chroot()

            except ChrootError, err:
                print err

            finally:
                self._unset()

    @property
    def arch(self):
        if not hasattr(self, "_arch"):
            self._arch = what_arch(self._rootdir, self.FILECHKS)

        return self._arch

    @property
    def bindings(self):
        return self._bindings

    @property
    def duppings(self):
        return self._duppings

    @property
    def processes(self):
        procs = []

        for path in glob.glob("/proc/[0-9]*/root"):
            if os.path.samefile(self._rootdir, path):
                proc = int(path.split('/')[2])
                procs.append(proc)

        return procs

if __name__ == '__main__':
    chroot = Chroot('/tmp/jail')
    chroot.chroot()
