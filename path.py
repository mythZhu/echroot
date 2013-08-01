#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def cano_path(filepath, rootpath='/'):
    """ Canonicalize file path.

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
    try:
        make_dirs(os.path.dirname(nodepath))
        os.mknod(nodepath, mode)
    except:
        return False
    else:
        return True

def read_link(linkpath):
    """ Return the path to which the symbolic link points. 

        If @linkpath is not a link, return @linkpath itself.
    """
    if os.path.islink(linkpath):
        return os.readlink(linkpath)
    else:
        return linkpath
