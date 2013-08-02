#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import struct

""" The ELF file header. 

    This appears at the start of every ELF file.

    typedef struct {
        unsigned char e_ident[16];
        uint16_t      e_type;
        uint16_t      e_machine;
        uint32_t      e_version;
        uint32_t      e_entry;
        uint32_t      e_phoff;
        uint32_t      e_shoff;
        uint32_t      e_flags;
        uint16_t      e_ehsize;
        uint16_t      e_phentsize;
        uint16_t      e_phnum;
        uint16_t      e_shentsize;
        uint16_t      e_shnum;
        uint16_t      e_shstrndx;
    } ElfHeader32;

    typedef struct {
        unsigned char e_ident[16];
        uint16_t      e_type;
        uint16_t      e_machine;
        uint32_t      e_version;
        uint64_t      e_entry;
        uint64_t      e_phoff;
        uint64_t      e_shoff;
        uint32_t      e_flags;
        uint16_t      e_ehsize;
        uint16_t      e_phentsize;
        uint16_t      e_phnum;
        uint16_t      e_shentsize;
        uint16_t      e_shnum;
        uint16_t      e_shstrndx;
    } ElfHeader64;

"""

ElfHeader32 = "16sHHIIIIIHHHHHH"
ElfHeader64 = "16sHHIQQQIHHHHHH"

""" Fields in the e_ident array.  

    The EI_* entries are indices into the array. 
    The entries under each EI_* macro are the values 
    the byte may have. 
"""

EI_MAG0      = 0
ELFMAG0      = 0x7f

EI_MAG1      = 1
ELFMAG1      = 'E'

EI_MAG2      = 2
ELFMAG2      = 'L'

EI_MAG3      = 3
ELFMAG3      = 'F'

ELFMAG       = '\x7fELF'
SELFMAG      = 4

EI_CLASS     = 4
ELFCLASSNONE = '\x00'
ELFCLASS32   = '\x01'
ELFCLASS64   = '\x02'

EI_DATA      = 5
ELFDATANONE  = 0
ELFDATA2LSB  = 1
ELFDATA2MSB  = 2
ELFDATANUM   = 3

""" Some legal values for e_machine (architecture). 
"""
EM_NOME      = 0
EM_386       = 3
EM_X86_64    = 62
EM_ARM       = 40
EM_AARCH64   = 183


class ElfObjectError(Exception):
    """ Base exception class for ElfObject class"""
    pass


class ElfObject(object):
    """ ELF file parsing class.

        Automatically check if the file is an ELF and 
        parse ELF header.
    """

    ORDREF = { ELFDATANONE : '=',
               ELFDATA2LSB : '<',
               ELFDATA2MSB : '>',
               ELFDATANUM  : '=', }

    FMTREF = { ELFCLASSNONE : '',
               ELFCLASS32   : ElfHeader32,
               ELFCLASS64   : ElfHeader64, }

    def __init__(self, filepath):
        """ Prepare the elf object.

            Check if @filepath is an ELF. If not, raise
            an exception.If so, extract the ELF header
            according to ELF file class.
        """
        if not is_elf(filepath):
            raise ElfObjectError("Not a valid ELF file")
            
        # extract ident array
        ident_wrd = unpack_from(filepath, "=16s", 0)

        # identify ELF data order and file class
        # determine the ELF header format
        ehdr_ord = self.ORDREF.get(ident_wrd[EI_DATA], '=')
        ehdr_fmt = self.FMTREF.get(ident_wrd[EI_CLASS], '')
        ehdr_fmt = ehdr_ord + ehdr_fmt

        # extract the ELF header
        self._ehdr = unpack_from(filepath, ehdr_fmt, 0)

    @property
    def machine(self):
        return {EM_386      : 'i386',
                EM_X86_64   : 'x86_64',
                EM_ARM      : 'arm',
                EM_AARCH64  : 'aarch64',}.get(self._ehdr[2], None)

    @property
    def order(self):
        return {ELFDATA2LSB : 'LSB',
                ELFDATA2MSB : 'MSB',}.get(self._ehdr[0][EI_DATA], None)


def unpack_from(filepath, filefmt, offset=0):
    """ Unpack the binnary file.
    
        Unpack according to @filefmt, starting at @offset.
    """
    with open(filepath) as fileobj:
        fileobj.seek(offset)
        siz = struct.calcsize(filefmt)
        wrd = struct.unpack(filefmt, fileobj.read(siz))

    return len(wrd) == 1 and wrd[0] or wrd


def is_elf(filepath):
    """ Check if the file is an ELF. 
        
        Return `True` is @filepath is an ELF file.
    """
    return os.path.lexists(filepath) and \
           unpack_from(filepath, "=16s", 0)[:SELFMAG] == ELFMAG
