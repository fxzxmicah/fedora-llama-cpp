#!/usr/bin/sh
set -eu

if [ "$#" -ne 5 ]; then
    echo "Usage: $0 BUILDROOT PREFIX LIBDIR BINDIR INCLUDEDIR" >&2
    exit 2
fi

buildroot=$1
prefix=$2
libdir=$3
bindir=$4
includedir=$5

repo_packages=$(dnf repoquery --installed --installed-from-repo="*cuda*" --queryformat "%{name}\n")

if [ -z "$repo_packages" ]; then
    echo "Could not determine packages installed from a CUDA repository" >&2
    exit 1
fi

missing=0

check_file() {
    src=$1
    dest=

    case $src in
        "(contains"|"no"|"files)")
            return 0
            ;;
        /usr/local/cuda-*/targets/x86_64-linux/lib/stubs/*)
            dest=${buildroot}${libdir}/stubs/${src##*/}
            ;;
        /usr/local/cuda-*/targets/x86_64-linux/lib/cmake/*)
            dest=${buildroot}${libdir}/cmake/${src#*/targets/x86_64-linux/lib/cmake/}
            ;;
        /usr/local/cuda-*/targets/x86_64-linux/lib/*)
            dest=${buildroot}${libdir}/${src##*/}
            ;;
        /usr/local/cuda-*/targets/x86_64-linux/include/*)
            dest=${buildroot}${includedir}/cuda/${src#*/targets/x86_64-linux/include/}
            ;;
        /usr/local/cuda-*/nvvm/*)
            dest=${buildroot}${prefix}/nvvm/${src#*/nvvm/}
            ;;
        /usr/local/cuda-*/src/*)
            dest=${buildroot}${prefix}/src/${src#*/src/}
            ;;
        /usr/local/cuda-*/bin/*)
            dest=${buildroot}${bindir}/${src#*/bin/}
            ;;
        /usr/lib64/pkgconfig/*.pc)
            dest=${buildroot}${libdir}/pkgconfig/${src##*/}
            ;;
        /usr/share/licenses/*/*)
            return 0
            ;;
        /etc/ld.so.conf.d/*)
            return 0
            ;;
        /usr/local/cuda-*|/usr/local/cuda-*/include|/usr/local/cuda-*/lib64|/usr/local/cuda-*/targets|/usr/local/cuda-*/targets/x86_64-linux|/usr/local/cuda-*/targets/x86_64-linux/lib|/usr/local/cuda-*/targets/x86_64-linux/lib/cmake|/usr/local/cuda-*/targets/x86_64-linux/include|/usr/local/cuda-*/targets/x86_64-linux/lib/stubs|/usr/local/cuda-*/bin|/usr/local/cuda-*/nvvm|/usr/local/cuda-*/nvvm/bin|/usr/local/cuda-*/nvvm/include|/usr/local/cuda-*/nvvm/lib64|/usr/local/cuda-*/nvvm/libdevice|/usr/local/cuda-*/src)
            return 0
            ;;
        /usr/share/licenses/*)
            return 0
            ;;
        *)
            echo "Unhandled CUDA package file: $src" >&2
            missing=1
            return 0
            ;;
    esac

    if [ ! -e "$dest" ]; then
        echo "Missing CUDA repackaged file: $src -> ${dest#$buildroot}" >&2
        missing=1
    fi
}

for pkg in $repo_packages; do
    files=$(rpm -ql "$pkg")
    for src in $files; do
        check_file "$src"
    done
done

if [ "$missing" -ne 0 ]; then
    exit 1
fi
