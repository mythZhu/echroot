#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from echroot.fs import aux
from echroot.utils import runner

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
        self._olddir = aux.cano_path(olddir)
        self._newdir = aux.cano_path(newdir)
        self._option = ','.join(options or [''])
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
        return runner.call("mount -o bind,%s %s %s" % (self._option, 
                                                       self._olddir, 
                                                       self._newdir))[0] == 0

    def _unbind(self):
        """ Call umount(8) to unbind.

            Mountpoints are expected to be binded already.
        """ 
        return runner.call("umount %s" % self._newdir)[0] == 0

    def binded(self):
        """ Test if this binding is binded. """
        # Sometimes os.path.ismount performs incorrectly.
        # Check mount table is a better way.
        with open("/proc/mounts", 'r') as mnts:
            for mnt in mnts.readlines():
                newdir = aux.cano_path(mnt.split()[1])
                if self._newdir == newdir: 
                    return True
            else:
                return False

    def bind(self):
        """ Bind olddir to newdir.

            If mountpoints doesn't exist, they will be 
            created here and deleted in 'unbind' method 
            later.
        """
        if self.binded(): 
            return

        if not os.path.exists(self._newdir):
            self._mkstat = aux.make_dirs(self._newdir)

        self._bind() or self._mkstat and aux.remove_dirs(self._newdir)

    def unbind(self):
        """ Unbind newdir from olddir.

            mountpints created in 'bind' method will be
            deleted here.
        """
        if not self.binded():
            return

        self._unbind() and self._mkstat and aux.remove_dirs(self._newdir)
