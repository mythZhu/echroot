#!/bin/sh

# repositories
#
URLS="
i386 http://ftp.us.debian.org/debian/pool/main/q/qemu/qemu-user-static_1.5.0+dfsg-5_i386.deb\n
amd64 http://ftp.us.debian.org/debian/pool/main/q/qemu/qemu-user-static_1.5.0+dfsg-5_amd64.deb\n
"
# parse arguments
#
QEMU=$1
ROOT=$2

if [[ -z "${QEMU}" || -z "${ROOT}" ]]; then
    echo "Usage: ./fetch-qemu QEMU ROOT"
    exit 1
fi

# identify host arch
#
case `uname -m` in
    "i*86") 
        ARCH="i386"
        ;;
    "x86_64")
        ARCH="x86_64"
        ;;
esac

# determine repository
#
URL=`echo -e ${URLS} | grep "^${ARCH}" | tr -s ' ' | cut -d ' ' -f2`

[ -z "${URL}" ] && exit 1


# download qemu package
#
wget -np -nd --tries=2 --timeout=60 --quiet ${URL} -O qemu-static.deb

[ ! -e "qemu-static.deb" ] && exit 1

# extract qemu binary file
#
ar p qemu-static.deb data.tar.gz | tar zx -C ${ROOT} ./usr/bin/${QEMU}
rm -rf qemu-static.deb

# succeed to exit
#
echo "FINISH" && exit 0
