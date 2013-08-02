#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import os
import shutil

from run import call
from path import norm_path, make_dirs
from magic import MAGIC

def disable_selinux():
    """ disable selinux.
    
        Selinux will block qemu emulator to run.
    """
    return call("setenforce 0")[0] == 0

def install_qemu_emulator(rootdir, arch):
    """ Install statically-linked qemu emulator. 
        
        If failed to find qemu-@arch-static emulator at the local, 
        turn to recommanded repos for help.
    """
    try:
        srcpath = "/usr/bin/qemu-%s-static" % arch
        dstpath = norm_path(srcpath, rootdir)
        make_dirs(os.path.dirname(dstpath))
        shutil.copy(srcpath, dstpath)
    except:
        return None
    else:
        return dstpath

def register_qemu_emulator(qemu, arch):
    """ Register qemu emulator for other arch executable file.

        Mount binfmt_misc if it doesn't exist. Unregister qemu-@arch, 
        if it has been registered and isn't a statically-linked executable
    """
    binfmt_node = "/proc/sys/fs/binfmt_misc"
    if not os.path.exists(binfmt_node):
        call("modprobe %s" % os.path.basename(binfmt_node))

    register_node = "/proc/sys/fs/binfmt_misc/register"
    if not os.path.exists(register_node):
        call("mount -t binfmt_misc none %s" % os.path.dirname(register_node))

    qemu_node = "/proc/sys/fs/binfmt_misc/%s" % arch

    if os.path.exists(qemu_node):
        fd = open(qemu_node, 'w')
        fd.write("-1\n")
        fd.close()

    if not os.path.exists(qemu_node):
        magic = MAGIC.get(arch, None)
        if not magic:
            return False
        else:
            fd = open(register_node, 'w')
            fd.write("%s:%s:\n" %(magic, qemu))
            fd.close()
            return True

def setup_qemu_emulator(rootdir, arch):
    """ Install and register qemu emulator in @rootdir. 

        Statically-linked qemu emulator is expected to be
        configured rather than dynamically-linked one.
    """
    qemu = install_qemu_emulator(rootdir, arch)

    if qemu:
        register_qemu_emulator(qemu.replace(rootdir, '/'), arch)
        disable_selinux()
        return qemu
    else:
        return ''

def unset_qemu_emulator(rootdir, arch, qemu):
    """ Unregister and remove qemu emulator in @rootdir. 
    """
    qemu_node = "/proc/sys/fs/binfmt_misc/%s" % arch

    if os.path.exists(qemu_node):
        fd = open(qemu_node, 'w')
        fd.write("-1\n")
        fd.close()

    if os.path.exists(qemu):
        os.unlink(qemu)
