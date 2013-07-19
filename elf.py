#!/usr/bin/env python

import os
import struct

# The ELF file header. 
# This appears at the start of every ELF file.
#
# define EI_NIDENT 16
#
# typedef struct {
#     unsigned char e_ident[EI_NIDENT];
#     uint16_t      e_type;
#     uint16_t      e_machine;
#     uint32_t      e_version;
#     uint32_t      e_entry;
#     uint32_t      e_phoff;
#     uint32_t      e_shoff;
#     uint32_t      e_flags;
#     uint16_t      e_ehsize;
#     uint16_t      e_phentsize;
#     uint16_t      e_phnum;
#     uint16_t      e_shentsize;
#     uint16_t      e_shnum;
#     uint16_t      e_shstrndx;
# } ElfHeader32;
#
# typedef struct {
#     unsigned char e_ident[EI_NIDENT];
#     uint16_t      e_type;
#     uint16_t      e_machine;
#     uint32_t      e_version;
#     uint64_t      e_entry;
#     uint64_t      e_phoff;
#     uint64_t      e_shoff;
#     uint32_t      e_flags;
#     uint16_t      e_ehsize;
#     uint16_t      e_phentsize;
#     uint16_t      e_phnum;
#     uint16_t      e_shentsize;
#     uint16_t      e_shnum;
#     uint16_t      e_shstrndx;
# } ElfHeader64;
#
ElfHeader32 = "<16sHHIIIIIHHHHHH"
ElfHeader64 = "<16sHHIQQQIHHHHHH"

# Fields in the e_ident array.  
# The EI_* entries are indices into the array.
# The entries under each EI_* macro are the values the byte may have. 
EI_MAG0         = 0 
EI_MAG1         = 1
EI_MAG2         = 2
EI_MAG3         = 3
ELFMAG          = '\x7fELF'

EI_CLASS        = 4
ELFCLASSNONE    = '\x00'
ELFCLASS32      = '\x01'
ELFCLASS64      = '\x02'

# Supported architectures until now.
# Some legal values for e_machine (architecture).
ARCH_386        = 3
ARCH_X86_64     = 62
ARCH_ARM        = 40
ARCH_ARM64      = 183


class ElfObject(object):

    def __init__(self, filepath):
        fileobj = open(filepath, 'rb')

        # get e_ident array
        ident_fmt = '<16s'
        ident_siz = struct.calcsize(ident_fmt)
        ident_wrd = struct.unpack(ident_fmt, fileobj.read(ident_siz))[0]
 
        # verify if fileobj is a known ELF object file 
        if ident_wrd[0:4] != ELFMAG:
            raise Exception("Not a valid ELF file")

        # identify ELF file class
        ehdr_fmt = ''
        if ident_wrd[EI_CLASS] == ELFCLASS32:
            ehdr_fmt = ElfHeader32
        if ident_wrd[EI_CLASS] == ELFCLASS64:
            ehdr_fmt = ElfHeader64
        ehdr_siz = struct.calcsize(ehdr_fmt)

        # get ELF file header from fileobj
        fileobj.seek(0)
        self._ehdr = struct.unpack(ehdr_fmt, fileobj.read(ehdr_siz))

        fileobj.close()

    @property
    def machine(self):
        return {ARCH_386      : 'Intel 80386',
                ARCH_X86_64   : 'x86-64',
                ARCH_ARM      : 'ARM',
                ARCH_ARM64    : 'ARM64'}.get(self._ehdr[2], None)
