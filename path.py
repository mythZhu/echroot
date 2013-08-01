#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

def norm_path(filepath, rootpath='/'):
    """ Normalize file path to absolute path.

        Expand ~ and ~user constructions and transform file
        path to absolute one. If necessary, substitute 
        @rootpath for '/'.
    """
    filepath = os.path.abspath(os.path.expanduser(filepath))
    rootpath = os.path.abspath(os.path.expanduser(rootpath))
    canopath = os.path.join(rootpath, filepath.lstrip('/'))

    return canopath

def cano_path(filepath, rootpath='/'):
    """ Canonicalize file path to real path.

        Expand ~ and ~user constructions and eliminate any
        symbolic links encountered in the path. If necessary, 
        substitute @rootpath for '/'.
    """
    filepath = os.path.realpath(os.path.expanduser(filepath))
    rootpath = os.path.realpath(os.path.expanduser(rootpath))
    canopath = os.path.join(rootpath, filepath.lstrip('/'))

    return canopath

def make_dirs(dirpath):
    """ Create a leaf directory and all intermediate ones.

        os.makedirs without exception.
        Return `True` if @dirpath has been created.
    """
    try:
        os.makedirs(dirpath)
    except:
        return False
    else:
        return True

def remove_dirs(dirpath):
    """ remove a leaf directory and all empty intermediate ones.

        os.removedirs without exception.
        Return `True` if @dirpath has been removed.
    """
    try:
        os.removedirs(dirpath)
    except:
        return False
    else:
        return True

def make_node(nodepath, mode=0600):
    """ Create a filesystem node.

        Create directory of @nodepath, if necessary. Then
        create @nodepath without exception. Return `True`
        if @nodepath has been created successfully.
    """
    make_dirs(os.path.dirname(nodepath))
    os.mknod(nodepath, mode)

def copy_file(srcfile, dstfile, shadow=True):
    """ Copy data from @srcfile to @dstfile.

        Shadow copy is default method.
    """
    if os.path.islink(srcfile):
        linkto = os.readlink(srcfile)
        os.symlink(linkto, dstfile)
    else:
        shutil.copyfile(srcfile, dstfile)
