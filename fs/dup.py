#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import aux

class DuppingError(Exception):
    """ Base exception class for dupping class. """
    pass

class Dupping(object):
    """ Represent a dup of file.

        This class is responsible for copying source file 
        and restoring overwrited dest file. Shadow copy is
        default method.
    """

    def __init__(self, srcfile, dstfile, shadow=True):
        """ Prepare for a dup instance.
            
            @srcfile must exist as a common file. @dstfile
            shouldn't exist. If @dstfile exists already, it 
            must be a common file, too.
        """
        self._srcfile = aux.norm_path(srcfile)
        self._dstfile = aux.norm_path(dstfile)
        self._shadow = shadow
        self._mkstat = False

        if not os.path.isfile(self._srcfile):
            raise DuppingError("srcfile '%s' is not file." % self._srcfile)
        if os.path.lexists(self._dstfile) and \
           not os.path.isfile(self._dstfile):
            raise DuppingError("dstfile '%s' is not file." % self._dstfile)

        bakdir = os.path.dirname(self._dstfile)
        bakname = ".%s.bak" % os.path.basename(self._dstfile)
        self._bakfile = os.path.join(bakdir, bakname)

        if os.path.lexists(self._bakfile):
            raise DuppingError("Cann't create backup file.")

    def __str__(self):
        """ Format Dupping to String. """
        label = self.dupped() and "====" or "!=!="
        return ' '.join([self._srcfile, label, self._dstfile])

    def dupped(self):
        """ Test if this dupping is dupped.

            Return `True` if there is a backup file belonging
            to this dupping.
        """
        return os.path.lexists(self._bakfile)

    def dup(self):
        """ Copy srcfile as dstfile.

            If dstfile doesn't exist, create it. Backup file
            will be create here and be deleted in 'undup'
            method later.

            NOTICE: Directories created here CANN'T be removed
            by 'undup' method.
        """
        if self.dupped(): 
            return

        if not os.path.lexists(self._dstfile):
            self._mkstat = aux.make_node(self._dstfile, 0666)

        os.rename(self._dstfile, self._bakfile)
        aux.copy_file(self._srcfile, self._dstfile, self._shadow)

    def undup(self):
        """ Delete dstfile and restore origin dstfile.

            Dstfile created in 'dup' method will be deleted
            here and backup file will be restored if necessary.
        """
        if not self.dupped():
            return

        os.unlink(self._dstfile)
        os.rename(self._bakfile, self._dstfile)
        self._mkstat and os.unlink(self._dstfile)
