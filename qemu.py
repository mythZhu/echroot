#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess

from path import cano_path, make_dirs

def locate_static_qemu():
    """ Locate statically-linked qemu emulator. """
    qemu = "/usr/bin/qemu-arm-static"
    return os.path.exists(qemu) and qemu or None

def disable_selinux():
    """ disable selinux.
    
        Selinux will block qemu emulator to run.
    """
    with open(os.path.devnull) as nulldev:
        cmd = "setenforce 0"
        ret = subprocess.call(cmd, stdout=nulldev, stderr=nulldev, shell=True)

    return ret == 0

def setup_binfmt_misc():
    """ Mount binfmt_misc if it doesn't exist. """
    if not os.path.exists("/proc/sys/fs/binfmt_misc"):
        with open(os.path.devnull) as nulldev:
            cmd = "modprobe binfmt_misc"
            ret = subprocess.call(cmd, stdout=nulldev, stderr=nulldev, shell=True)

    if not os.path.exists("/proc/sys/fs/binfmt_misc/register"):
        with open(os.path.devnull) as nulldev:
            cmd = "mount -t binfmt_misc none /proc/sys/fs/binfmt_misc"
            ret = subprocess.call(cmd, stdout=nulldev, stderr=nulldev, shell=True)

def register_qemu_emulator(qemu, arch):
    """ Register qemu emulator for other arch executable file.

        Unregister it if it has been registered and is a 
        dynamically-linked executable
    """
    node = "/proc/sys/fs/binfmt_misc/arm"
    if os.path.exists(node):
        fd = open(node, 'w')
        fd.write("-1\n")
        fd.close()

    if not os.path.exists(node):
        magic = ":%s:M::\\x7fELF\\x01\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x02\\x00\\x28\\x00:\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\x00\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xff\\xfa\\xff\\xff\\xff:%s:\n" % (arch, qemu)
        fd = open("/proc/sys/fs/binfmt_misc/register", 'w')
        fd.write(magic)
        fd.close()

def setup_qemu_emulator(rootdir, arch):
    """ Install statically-linked qemu emulator into @rootdir. 

        NOTICE: Copy statically-linked qemu emulator from host 
                into @rootdir simply now.
    """
    qemu = locate_static_qemu()
    if not qemu:
        return ''

    setup_binfmt_misc()
    register_qemu_emulator(qemu, arch)

    dest = cano_path(qemu, rootdir)
    make_dirs(os.path.dirname(dest))
    shutil.copy(qemu, dest)

    return qemu
