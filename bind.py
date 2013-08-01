#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

from path import cano_path, make_dirs, remove_dirs

class BindingError(Exception):
    """ Base exception class for Binding class. """
    pass

class Binding(object):
    """ Represent a bind mount of directory.

        For more detail, man 8 mount.
    """

    def __init__(self, olddir, newdir, *options):
        """ Prepare for mountpoints.
            
            @olddir must be a directory. @newdir is expected 
            to be a directory. The case that @newdir doesn't 
            exist is all right, too.
        """
        self._olddir = cano_path(olddir)
        self._newdir = cano_path(newdir)
        self._option = ','.join(options or ["bind"])
        self._mkstat = False

        if not os.path.isdir(self._olddir):
            raise BindingError("olddir '%s' is not directory." % self._olddir)
        if os.path.exists(self._newdir) and \
           not os.path.isdir(self._newdir):
            raise BindingError("newdir '%s' is not directory." % self._newdir)

    def __str__(self):
        """ Format Binding to String. """
        label = self.binded() and "--->" or "-x->"
        return ' '.join([self._olddir, label, self._newdir])

    def _bind(self):
        """ Call mount(8) to bind. 

            Mountpoints are expected to be available and unbinded.
        """
        with open(os.path.devnull) as devnull:
            cmd = "mount -o %s %s %s" % (self._option, self._olddir, self._newdir)
            ret = subprocess.call(cmd, stdout=devnull, stderr=devnull, shell=True)

        return ret == 0

    def _unbind(self):
        """ Call umount(8) to unbind.

            Mountpoints are expected to be binded already.
        """ 
        with open(os.path.devnull) as devnull:
            cmd = "umount %s" % self._newdir
            ret = subprocess.call(cmd, stdout=devnull, stderr=devnull, shell=True)

        return ret == 0

    def binded(self):
        """ Test if this binding is binded. """
        return os.path.ismount(self._newdir)

    def bind(self):
        """ Bind olddir to newdir.

            If mountpoints doesn't exist, they will be 
            created here and deleted in 'unbind' method 
            later.
        """
        if self.binded(): 
            return

        self._mkstat = make_dirs(self._newdir)
        self._bind() or self._makstat and remove_dirs(self._newdir)

    def unbind(self):
        """ Unbind newdir from olddir.

            mountpints created in 'bind' method will be
            deleted here.
        """
        if not self.binded():
            return

        self._unbind() and self._mkstat and remove_dirs(self._newdir)
