#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

def call(cmdline):
    """ wrapper for subprocess calls.

        Return a tuple (returncode, stdout, stderr).
    """
    pipe = subprocess.PIPE
    proc = subprocess.Popen(cmdline, stdout=pipe, stderr=pipe, shell=True)
    sout, serr = proc.communicate()

    return (proc.returncode, sout, serr)
