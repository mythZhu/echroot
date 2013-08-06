#!/bin/sh

# locate echroot
PROG=`which echroot`
[ -z "${PROG}" ] && exit

# download rootfs
wget -np -nd --tries=2 --timeout=60 \
http://distfiles.gentoo.org/releases/arm/autobuilds/current-stage3-armv4tl/stage3-armv4tl-20130304.tar.bz2 \
-O rootfs.tar.bz2

# unzip rootfs
rm -rf rootfs
mkdir -p rootfs
tar -jxvf rootfs.tar.bz2 -C rootfs

# chroot rootfs
${PROG} ./rootfs echo 'OK'

# clean 
rm -rf rootfs*
