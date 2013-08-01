#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import subprocess

from path import cano_path
from elf import ElfObject, is_elf
from dup import Dupping, DuppingError
from bind import Binding, BindingError
from flock import FileLock

def what_arch(rootdir, checks):
    for chk in checks:
        path = cano_path(chk)
        arch = is_elf(path) and ElfObject(path).machine
        if arch: return arch
    else: 
        return None

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
                 "/etc/mtab:/etc/mtab")

    def __init__(self, rootdir, execute="/bin/bash"):
        self._rootdir = rootdir
        self._execute = execute

        self._bindings = []
        self._duppings = []

        self._emulator = ''

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
            print binding

    def _setup_duppings(self, filedups=FILEDUPS):
        for filedup in filedups:
            try:
                splits  = filedup.split(':')
                srcfile = splits[0].strip()
                dstfile = cano_path(splits[1].strip(), self._rootdir)
                dupping = Dupping(srcfile, dstfile)
            except DuppingError:
                continue

            dupping.dup()
            dupping.dupped() and self._duppings.append(dupping)
            print dupping

    def _setup_emulator(self, checks=FILECHKS):
        pass

    def _unset_bindings(self):
        for binding in reversed(self._bindings):
            binding.unbind()
            not binding.binded() and self._bindings.remove(binding)
            print binding

    def _unset_duppings(self):
        for dupping in self._duppings:
            dupping.undup()
            not dupping.dupped() and self._duppings.remove(dupping)
            print dupping

    def _unset_emulator(self):
        if os.path.exists(self._emulator):
            os.unlink(self._emulator)

    def _kill_processes(self):
        for proc in self.processes:
            try:
                os.kill(proc, 9)
            except:
                print "[FAIL] Terminal process %d." % proc
            else:
                print "[DONE] Terminal process %d." % proc

    def _setup(self):
        print
        print "--------------SETUP--------------"
        print

        self._setup_bindings()
        self._setup_duppings()
        self._setup_emulator()

    def _unset(self):
        print
        print "--------------UNSET--------------"
        print

        self._kill_processes()
        self._unset_emulator()
        self._unset_duppings()
        self._unset_bindings()

    def _chroot(self):
        def oschroot():
            os.chroot(self._rootdir)
            os.chdir('/')

        print
        print "--------------LOGIN--------------"
        print

        subprocess.call(self._execute, preexec_fn = oschroot, shell=True)

    def chroot(self):
        # try to lock chrootdir
        # many-to-one not allowed
        with FileLock(self._rootdir) as flock:
            try:
                self._setup()
                self._chroot()
            finally:
                self._unset()

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
