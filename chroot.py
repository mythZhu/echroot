#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import subprocess

import fs
import elf
import interp

from fs.dup import Dupping, DuppingError
from fs.bind import Binding, BindingError
from utils.flock import FileLock, FileLockError

def what_arch(rootdir, checks):
    for chk in checks:
        path = fs.aux.norm_path(chk, rootdir)
        arch = elf.is_elfobj(path) and elf.ElfObject(path).machine
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
                 "/var/lock/:/var/lock/",
                 "/:/parent:ro", )

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
                newdir = fs.aux.cano_path(splits[1].strip(), self._rootdir)
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
                dstfile = fs.aux.norm_path(splits[1].strip(), self._rootdir)
                dupping = Dupping(srcfile, dstfile)
            except DuppingError:
                continue

            dupping.dup()
            dupping.dupped() and self._duppings.append(dupping)

    def _setup_interpre(self):
        if not self.arch:
            raise ChrootError("setup: cann't resolve arch of '%s'." % self._rootdir)

        if self.arch == what_arch('/', self.FILECHKS):
            self._interpre = "native"
        else:
            self._interpre = interp.qemu.setup(self._rootdir, self.arch)

        if not self._interpre:
            raise ChrootError("setup: cann't setup %s interpreter." % self.arch)

    def _unset_bindings(self):
        for binding in reversed(self._bindings):
            binding.unbind()

    def _unset_duppings(self):
        for dupping in self._duppings:
            dupping.undup()

    def _unset_interpre(self):
        if not self._interpre:
            return

        if self._interpre == "native":
            return

        if self._interpre.startswith("qemu"):
            interp.qemu.unset(self._rootdir, self._interpre)

    def _kill_processes(self):
        for proc in self.processes:
            try:
                os.kill(proc, 9)
            except:
                pass

    def _check(self):
        # TODO: more checks are necessary
        if not os.path.isdir(self._rootdir):
            raise ChrootError("check: '%s' not a directory." % self._rootdir)

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
            print 
            print "--------------------------------------------------------"
            print "           Welcome To Echroot - easy chroot             "
            print "--------------------------------------------------------"
            print 

            subprocess.call(self._execute, preexec_fn = oschroot, shell=True)

        except Exception, e:
            raise ChrootError("chroot: %s." % e)

    def chroot(self):
        with FileLock(self._rootdir) as flock:
            try:
                self._check()
                self._setup()
                self._chroot()

            except ChrootError, err:
                raise err

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
            if self._rootdir == os.readlink(path):
                proc = int(path.split('/')[2])
                procs.append(proc)

        return procs
