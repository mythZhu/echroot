#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import os
import shutil

from run import call
from path import norm_path, make_dirs

MAGICS = { "arm"  : ":arm:M::\\x7fELF\\x01\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x28\\x00:\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\x00\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xfa\\xff\\xff\\xff",
           "i386" : ":i386:M::\\x7fELF\\x01\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x03\\x00:\\xff\\xff\\xff\\xff\\xff\\xfe\\xfe\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xfe\\xff\\xff\\xff", }

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
        return ''
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
        magic = MAGICS.get(arch, None)
        if not magic:
            return False
        else:
            magic = magic + ":%s:\n" % qemu
            fd = open(register_node, 'w')
            fd.write(magic)
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
