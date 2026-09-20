%global debug_package %{nil}
%global _build_id_links none

Name:           base
Version:        %{fedora}
Release:        1%{?dist}
Summary:        Minimal Fedora %{version} base for application chroots
License:        GPL-3.0-or-later AND (GPL-3.0-or-later WITH GCC-exception-3.1) AND LGPL-2.1-or-later AND LGPL-2.0-or-later AND BSD-2-Clause AND BSD-3-Clause AND ISC AND MIT AND LicenseRef-Fedora-Public-Domain
URL:            https://fedoraproject.org/

ExclusiveArch:  x86_64

BuildRequires:  bash >= 5.3
BuildRequires:  fedora-gpg-keys >= %{version}
BuildRequires:  fedora-release-common >= %{version}
BuildRequires:  /usr/lib/os-release
BuildRequires:  filesystem >= 3.18
BuildRequires:  glibc >= 2.43
BuildRequires:  glibc-common >= 2.43
BuildRequires:  glibc-minimal-langpack >= 2.43
BuildRequires:  libgcc >= 16
BuildRequires:  ncurses-libs >= 6.6
BuildRequires:  setup >= 2.15.0
BuildRequires:  tzdata

Provides:       bash = 5.3
Provides:       bash%{?_isa} = 5.3
Provides:       /bin/bash
Provides:       /bin/sh
Provides:       /lib64/ld-linux-x86-64.so.2
Provides:       basesystem
Provides:       filesystem = 3.18
Provides:       filesystem%{?_isa} = 3.18
Provides:       filesystem(merged-sbin)
Provides:       filesystem(unmerged-sbin-symlinks)
Provides:       glibc = 2.43
Provides:       glibc%{?_isa} = 2.43
Provides:       glibc-common = 2.43
Provides:       glibc-minimal-langpack = 2.43
Provides:       glibc-minimal-langpack%{?_isa} = 2.43
Provides:       glibc-langpack = 2.43
Provides:       libgcc = 16.1.1
Provides:       libgcc%{?_isa} = 16.1.1
Provides:       setup = 2.15.0
Provides:       fedora-gpg-keys = %{version}-999
Provides:       fedora-release = %{version}
Provides:       fedora-release-common = %{version}
Provides:       fedora-release-identity = %{version}
Provides:       fedora-release-identity-basic = %{version}
Provides:       system-release = %{version}
Provides:       system-release(%{version})
Provides:       user(adm)
Provides:       user(bin)
Provides:       user(daemon)
Provides:       user(ftp)
Provides:       user(games)
Provides:       user(halt)
Provides:       user(lp)
Provides:       user(mail)
Provides:       user(root)
Provides:       user(nobody)
Provides:       user(operator)
Provides:       user(shutdown)
Provides:       user(sync)
Provides:       group(adm)
Provides:       group(audio)
Provides:       group(bin)
Provides:       group(cdrom)
Provides:       group(clock)
Provides:       group(daemon)
Provides:       group(dialout)
Provides:       group(disk)
Provides:       group(floppy)
Provides:       group(ftp)
Provides:       group(games)
Provides:       group(halt)
Provides:       group(input)
Provides:       group(kmem)
Provides:       group(root)
Provides:       group(nobody)
Provides:       group(kvm)
Provides:       group(lock)
Provides:       group(lp)
Provides:       group(mail)
Provides:       group(man)
Provides:       group(mem)
Provides:       group(operator)
Provides:       group(render)
Provides:       group(sgx)
Provides:       group(shutdown)
Provides:       group(sync)
Provides:       group(sys)
Provides:       group(tape)
Provides:       group(tty)
Provides:       group(users)
Provides:       group(utmp)
Provides:       group(video)
Provides:       group(wheel)

%description
A minimal Fedora %{version} x86_64 chroot base assembled from files in the build
environment.  It provides the essential directory tree, Bash as /bin/sh,
glibc runtime libraries, C.UTF-8, libgcc, local identities, and Fedora release
identity.

Actual package Provides, backed by the corresponding runtime payload, are:
bash, glibc, glibc-minimal-langpack, glibc-langpack, libgcc,
fedora-release-identity, and system-release.  The user(...) and group(...)
capabilities are also backed by the packaged passwd and group databases.

base has no external runtime package dependencies.  Optional higher layers such
as fedora-repos and ncurses-base are installed separately and may depend on
capabilities supplied by base; their payloads are not duplicated here.

Fake or deliberately partial package Provides, used only to satisfy RPM base
dependencies without installing unused files, are: basesystem, filesystem,
setup, glibc-common, fedora-gpg-keys, fedora-release, fedora-release-common,
and fedora-release-identity-basic.

This package is for an empty chroot.  It must not be installed over a
normal Fedora system.

%prep

%build

%install
# Minimal chroot and usrmerge skeleton.  Device nodes and pseudo-filesystems are
# attached by the chroot creator when needed and must never be baked into RPM.
install -dm0755 \
    %{buildroot}/dev \
    %{buildroot}/etc \
    %{buildroot}/etc/pki/rpm-gpg \
    %{buildroot}/etc/ld.so.conf.d \
    %{buildroot}/etc/profile.d \
    %{buildroot}/home \
    %{buildroot}/proc \
    %{buildroot}/run \
    %{buildroot}/sys \
    %{buildroot}/usr \
    %{buildroot}%{_bindir} \
    %{buildroot}%{_prefix}/lib/sysimage/libdnf5 \
    %{buildroot}%{_prefix}/lib/sysimage/rpm \
    %{buildroot}%{_libdir} \
    %{buildroot}%{_datadir} \
    %{buildroot}/var \
    %{buildroot}/var/cache \
    %{buildroot}/var/cache/ldconfig \
    %{buildroot}/var/cache/libdnf5 \
    %{buildroot}/var/lib \
    %{buildroot}/var/lib/dnf \
    %{buildroot}/var/lib/rpm-state \
    %{buildroot}/var/log
install -dm0700 %{buildroot}/root
install -dm1777 %{buildroot}/tmp %{buildroot}/var/tmp

ln -s usr/bin %{buildroot}/bin
ln -s usr/lib %{buildroot}/lib
ln -s usr/lib64 %{buildroot}/lib64
ln -s usr/sbin %{buildroot}/sbin
ln -s bin %{buildroot}%{_prefix}/sbin
ln -s ../run %{buildroot}/var/run
ln -s /proc/self/mounts %{buildroot}/etc/mtab

# A shell is required by RPM scriptlets as well as for chroot maintenance.
install -pm0755 /usr/bin/bash %{buildroot}%{_bindir}/bash
ln -s bash %{buildroot}%{_bindir}/sh

# Copy dereferenced SONAME files so the payload does not depend on private,
# versioned filenames from the buildroot package layout.
for library in \
    ld-linux-x86-64.so.2 \
    libc.so.6 \
    libm.so.6 \
    libdl.so.2 \
    libpthread.so.0 \
    libresolv.so.2 \
    librt.so.1 \
    libutil.so.1 \
    libanl.so.1 \
    libBrokenLocale.so.1 \
    libmvec.so.1 \
    libnss_dns.so.2 \
    libnss_files.so.2; do
    test -e "%{_libdir}/${library}"
    cp -aL "%{_libdir}/${library}" "%{buildroot}%{_libdir}/${library}"
done
test -e %{_libdir}/libtinfo.so.6
cp -aL %{_libdir}/libtinfo.so.6 %{buildroot}%{_libdir}/libtinfo.so.6
test -e %{_libdir}/libgcc_s.so.1
cp -aL %{_libdir}/libgcc_s.so.1 %{buildroot}%{_libdir}/libgcc_s.so.1

# Copy only the compact converter set owned by glibc itself.  Optional
# glibc-gconv-extra modules cannot leak in from a richer build environment.
rpm -ql glibc | while IFS= read -r converter; do
    case "${converter}" in
        %{_libdir}/gconv/*)
            if test -f "${converter}" || test -L "${converter}"; then
                install -dm0755 "%{buildroot}$(dirname "${converter}")"
                cp -a "${converter}" "%{buildroot}${converter}"
            fi
            ;;
    esac
done
test -f %{buildroot}%{_libdir}/gconv/UTF-16.so

# Keep local identities and the small shell/readline configuration files.
for config in \
    group \
    gshadow \
    inputrc \
    passwd \
    shadow \
    shells; do
    test -e "/etc/${config}"
    cp -a "/etc/${config}" "%{buildroot}/etc/${config}"
done
install -pm0644 /etc/ld.so.conf %{buildroot}/etc/ld.so.conf
install -pm0644 /dev/null %{buildroot}/etc/resolv.conf
printf '127.0.0.1 localhost localhost.localdomain\n::1 localhost localhost.localdomain\n' > %{buildroot}/etc/hosts
printf 'multi on\n' > %{buildroot}/etc/host.conf
printf '%s\n' \
    'passwd: files' \
    'shadow: files' \
    'group: files' \
    'hosts: files dns' \
    > %{buildroot}/etc/nsswitch.conf
printf 'LANG=C.UTF-8\n' > %{buildroot}/etc/locale.conf

# Use a builtins-only profile; Fedora's full profile invokes Coreutils, which
# is intentionally not part of this base package.
printf '%s\n' \
    'PATH=/usr/bin' \
    'export PATH' \
    'umask 022' \
    'if [ -n "${BASH_VERSION-}" ] && [ -r /etc/bashrc ]; then . /etc/bashrc; fi' \
    'for script in /etc/profile.d/*.sh; do [ -r "${script}" ] && . "${script}"; done' \
    'unset script' \
    > %{buildroot}/etc/profile
printf '%s\n' \
    'if [ -n "${PS1-}" ]; then PS1="[\\u@\\h \\W]\\$ "; fi' \
    > %{buildroot}/etc/bashrc

# glibc's built-in C locale is ASCII; C.UTF-8 needs this compact locale tree.
test -d %{_prefix}/lib/locale/C.utf8
cp -a %{_prefix}/lib/locale/C.utf8 %{buildroot}%{_prefix}/lib/locale/

# Keep one real timezone and let applications needing named zones install the
# real tzdata package.  The base package does not Provide tzdata.
install -dm0755 %{buildroot}%{_datadir}/zoneinfo
install -pm0644 %{_datadir}/zoneinfo/UTC %{buildroot}%{_datadir}/zoneinfo/UTC
ln -s ../usr/share/zoneinfo/UTC %{buildroot}/etc/localtime

# Preserve the standard release-identification paths without pulling RPM/DNF
# executables into the chroot.
install -pm0644 %{_prefix}/lib/os-release %{buildroot}%{_prefix}/lib/os-release
ln -s ../usr/lib/os-release %{buildroot}/etc/os-release
install -pm0644 /etc/fedora-release %{buildroot}/etc/fedora-release
ln -s fedora-release %{buildroot}/etc/redhat-release
ln -s fedora-release %{buildroot}/etc/system-release

# The Fedora repo definitions resolve their gpgkey path inside the installroot.
# Keep only the current Fedora keys usable on this x86_64-only base, not the large
# historical and foreign-architecture key collection.
for key in \
    RPM-GPG-KEY-fedora-%{version}-primary \
    RPM-GPG-KEY-fedora-%{version}-%{_arch}; do
    test -e "/etc/pki/rpm-gpg/${key}"
    cp -aL "/etc/pki/rpm-gpg/${key}" "%{buildroot}/etc/pki/rpm-gpg/${key}"
done

# Repackaged binaries/data retain the license texts shipped by their source
# packages.  Namespacing prevents identically named COPYING files colliding.
install -dm0755 %{buildroot}%{_licensedir}/%{name}
for package in bash fedora-gpg-keys glibc libgcc ncurses-libs setup fedora-release-common tzdata; do
    if test -d "%{_licensedir}/${package}"; then
        install -dm0755 "%{buildroot}%{_licensedir}/%{name}/${package}"
        cp -a "%{_licensedir}/${package}/." "%{buildroot}%{_licensedir}/%{name}/${package}/"
    fi
done

%check
test "$(readlink %{buildroot}/bin)" = usr/bin
test "$(readlink %{buildroot}/lib64)" = usr/lib64
test "$(readlink %{buildroot}/sbin)" = usr/sbin
test "$(readlink %{buildroot}%{_prefix}/sbin)" = bin
test "$(readlink %{buildroot}%{_bindir}/sh)" = bash
test "$(readlink %{buildroot}/etc/localtime)" = ../usr/share/zoneinfo/UTC
test "$(readlink %{buildroot}/etc/mtab)" = /proc/self/mounts
test -d %{buildroot}/var/cache/libdnf5
test -d %{buildroot}%{_prefix}/lib/sysimage/rpm
test -s %{buildroot}/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-%{version}-%{_arch}

# Run the staged shell with the staged loader and libraries.  This catches an
# incomplete ELF closure without requiring chroot privileges in the builder.
env -i \
    %{buildroot}%{_libdir}/ld-linux-x86-64.so.2 \
    --library-path %{buildroot}%{_libdir} \
    %{buildroot}%{_bindir}/bash --noprofile --norc -c \
    'test "$(printf base-runtime-ok)" = base-runtime-ok'

%files
%license %{_licensedir}/%{name}
%dir /dev
%dir /etc
%dir /etc/pki
%dir /etc/pki/rpm-gpg
/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-%{version}-primary
/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-%{version}-%{_arch}
%config(noreplace) /etc/bashrc
%config(noreplace) /etc/group
%config(noreplace) /etc/gshadow
%config(noreplace) /etc/host.conf
%config(noreplace) /etc/hosts
%config(noreplace) /etc/inputrc
%config(noreplace) /etc/locale.conf
%config(noreplace) /etc/ld.so.conf
/etc/localtime
/etc/mtab
%config(noreplace) /etc/nsswitch.conf
/etc/os-release
%config(noreplace) /etc/passwd
%config(noreplace) /etc/profile
%dir /etc/profile.d
%config(noreplace) /etc/resolv.conf
/etc/fedora-release
/etc/redhat-release
%config(noreplace) /etc/shadow
%config(noreplace) /etc/shells
/etc/system-release
%dir /etc/ld.so.conf.d
/bin
%dir /home
/lib
/lib64
%dir /proc
%attr(0700,root,root) %dir /root
%dir /run
/sbin
%dir /sys
%attr(1777,root,root) %dir /tmp
%dir /usr
%dir %{_bindir}
%{_bindir}/bash
%{_bindir}/sh
%dir %{_prefix}/lib
%dir %{_prefix}/lib/sysimage
%dir %{_prefix}/lib/sysimage/libdnf5
%dir %{_prefix}/lib/sysimage/rpm
%dir %{_prefix}/lib/locale
%{_prefix}/lib/locale/C.utf8
%dir %{_libdir}
%{_libdir}/ld-linux-x86-64.so.2
%{_libdir}/lib*.so.*
%{_libdir}/gconv
%{_prefix}/sbin
%dir %{_datadir}
%dir %{_datadir}/zoneinfo
%{_datadir}/zoneinfo/UTC
%{_prefix}/lib/os-release
%dir /var
%dir /var/cache
%dir /var/cache/ldconfig
%dir /var/cache/libdnf5
%dir /var/lib
%dir /var/lib/dnf
%dir /var/lib/rpm-state
%dir /var/log
/var/run
%attr(1777,root,root) %dir /var/tmp

%changelog
* Sun Sep 20 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 44-1
- Add a minimal Fedora 44 chroot base assembled from buildroot files.
