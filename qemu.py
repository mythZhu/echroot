#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import os
import re
import shutil

from run import call
from path import norm_path, make_dirs
from magic import MAGIC

def disable_selinux():
    """ disable selinux.
    
        Selinux will block qemu emulator to run.
    """
    return call("setenforce 0")[0] == 0

def install_qemu_emulator(rootdir, qemubase):
    """ Install statically-linked qemu emulator. 
        
        If failed to find qemu-@arch-static emulator at the local, 
        turn to recommanded repos for help.
    """
    for srcdir in os.getenv("PATH", "/usr/local/bin/:/usr/bin/").split(':'):
        srcpath = os.path.join(srcdir, qemubase)
        if os.path.exists(srcpath):
            dstdir = norm_path("/usr/bin/", rootdir)
            dstpath = os.path.join(dstdir, qemubase)
            make_dirs(dstdir) and shutil.copy(srcpath, dstpath)
            return True
    else:
        return False

def uninstall_qemu_emulator(rootdir, qemubase):
    """ Uninstall statically-linked qemu emulator. 

        Remove '@rootdir/usr/bin/@qemubase' simply.
    """
    qemupath = os.path.join("/usr/bin/", qemubase)
    qemupath = norm_path(qemupath, rootdir)
    
    if os.path.exists(qemupath):
        os.unlink(qemupath)

    return os.path.exists(qemupath)

def register_qemu_emulator(qemu, arch):
    """ Register qemu emulator for @arch executable file.

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
        unregister_qemu_emulator(qemu, arch)

    if not os.path.exists(qemu_node):
        magic = MAGIC.get(arch, None)
        if not magic:
            return False
        else:
            fd = open(register_node, 'w')
            fd.write("%s:%s:\n" %(magic, qemu))
            fd.close()
            return True

def unregister_qemu_emulator(qemu, arch):
    """ Unregister qemu emulator for @arch executable file.

        Remove @arch node from binfmt_misc directory.
    """
    qemu_node = "/proc/sys/fs/binfmt_misc/%s" % arch

    if os.path.exists(qemu_node):
        fd = open(qemu_node, 'w')
        fd.write("-1\n")
        fd.close()

    return not os.path.exists(qemu_node)

def setup_qemu_emulator(rootdir, arch):
    """ Install and register qemu emulator in @rootdir. 

        Statically-linked qemu emulator is expected to be
        configured rather than dynamically-linked one.
    """
    qemubase = "qemu-%s-static" % arch
    qemupath = os.path.join("/usr/bin/", qemubase)

    stat = install_qemu_emulator(rootdir, qemubase) and \
           register_qemu_emulator(qemupath, arch) and \
           disable_selinux()

    if stat:
        return qemubase
    else:
        return None

def unset_qemu_emulator(rootdir, qemubase):
    """ Unregister and remove qemu emulator in @rootdir. """
    arch = re.match("qemu-([a-zA-A]*)-static", qemubase).group(1)
    qemupath = os.path.join("/usr/bin/", qemubase)

    return unregister_qemu_emulator(qemupath, arch) and \
           uninstall_qemu_emulator(rootdir, qemubase)
