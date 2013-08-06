echroot - esay chroot
=====================

What's a chroot?
----------------
A chroot on Unix like operating systems is an operation that changes the apparent 
root directory for the current running process and its children. A program that is 
run in such a modified environment cannot name (and therefore normally not access) 
files outside the designated directory tree. The term "chroot" may refer to the 
chroot(2) system call or the chroot(8) wrapper program. The modified environment 
is called a "chroot jail".

What's this for?
----------------
Anyone who wants to run a chroot whose architecture is different from the host one.

Where's rootfs?
---------------
* Slackware and Arch for ARM:

  * ftp://ftp.armedslack.org/slackwarearm/slackwarearm-devtools/minirootfs/roots/
  * http://archlinuxarm.org/developers/downloads

* CentOS, Debian, Fedora, Scientific, Suse, Ubuntu, ALT, Arch, CERN,
  Gentoo, OpenSuse, Openwall, Slackware, SLES, and etc. for x86 and
  x86-64 CPUs:

  * http://download.openvz.org/template/precreated/
  * http://cdimage.ubuntu.com/ubuntu-core/releases/

* Gentoo for a lot of architectures:

  * http://distfiles.gentoo.org/releases/

Synposis
--------
echroot [OPTION] NEWROOT [COMMAND [ARG]...]
echroot OPTION

Description
-----------
Run COMMAND with root directory set to NEWROOT.

    --version 
          output version information and exit

    -h, --help 
          display this help and exit

License
-------

Author
------
Written by Myth
