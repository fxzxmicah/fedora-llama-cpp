%global cuda_series 13-2
%global cuda_version %(echo '%{cuda_series}' | tr '-' '.')
%global cuda_root /usr/local/cuda-%{cuda_version}

%global debug_package %{nil}

Name:           cuda
Version:        %{cuda_version}
Release:        1%{?dist}
Summary:        NVIDIA CUDA runtime and development libraries
License:        NVIDIA Proprietary
URL:            https://developer.nvidia.com/cuda/toolkit/

Source1:        cuda-check-leftovers.sh

ExclusiveArch:  x86_64

BuildRequires:  cuda-cudart-devel-%{cuda_series}
BuildRequires:  cuda-driver-devel-%{cuda_series}
BuildRequires:  cuda-nvcc-%{cuda_series}
BuildRequires:  libcublas-devel-%{cuda_series}

%description
NVIDIA CUDA runtime and development libraries.

%package libs
Summary: CUDA runtime libraries

%description libs
The CUDA runtime libraries required to run applications.

%package devel
Summary: CUDA development tools and libraries
Requires: %{name}-libs = %{version}-%{release}

%description devel
The CUDA development headers, compiler, and static libraries.

%prep

%build

%install
install -dm0755 %{buildroot}%{_bindir}
install -dm0755 %{buildroot}%{_includedir}/cuda
install -dm0755 %{buildroot}%{_libdir}/cmake
install -dm0755 %{buildroot}%{_libdir}/pkgconfig
install -dm0755 %{buildroot}%{_libdir}/stubs
install -dm0755 %{buildroot}%{_prefix}/src
install -dm0755 %{buildroot}%{_licensedir}/%{name}-libs
install -dm0755 %{buildroot}%{_licensedir}/%{name}-devel

cp -a %{cuda_root}/targets/x86_64-linux/lib/*.so* %{buildroot}%{_libdir}/
cp -a %{cuda_root}/targets/x86_64-linux/lib/*.a %{buildroot}%{_libdir}/
cp -a %{cuda_root}/targets/x86_64-linux/lib/cmake/. %{buildroot}%{_libdir}/cmake/
cp -a %{cuda_root}/targets/x86_64-linux/lib/stubs/*.so %{buildroot}%{_libdir}/stubs/
cp -a %{cuda_root}/targets/x86_64-linux/include/. %{buildroot}%{_includedir}/cuda/

cp -a %{cuda_root}/bin/. %{buildroot}%{_bindir}/
cp -a %{cuda_root}/nvvm %{buildroot}%{_prefix}/
cp -a %{cuda_root}/src/. %{buildroot}%{_prefix}/src/

cp -a %{_libdir}/pkgconfig/cuda*.pc %{buildroot}%{_libdir}/pkgconfig/
cp -a %{_libdir}/pkgconfig/cublas*.pc %{buildroot}%{_libdir}/pkgconfig/

sed -i \
    -e '/^cudaroot=/d' \
    -e 's|^libdir=.*|libdir=%{_libdir}|' \
    -e 's|^includedir=.*|includedir=%{_includedir}/cuda|' \
    %{buildroot}%{_libdir}/pkgconfig/*.pc

sed -i \
    -e '/^LD_LIBRARY_PATH[[:space:]]*+=/d' \
    -e 's|^PATH[[:space:]]*+=.*|PATH            += $(CICC_PATH):|' \
    -e 's|^INCLUDES[[:space:]]*+=.*|INCLUDES        +=  "-I$(TOP)/include/cuda" $(_SPACE_)|' \
    -e 's|^SYSTEM_INCLUDES[[:space:]]*+=.*|SYSTEM_INCLUDES +=  "-isystem" "$(TOP)/include/cuda/cccl" $(_SPACE_)|' \
    -e 's|^LIBRARIES[[:space:]]*=+.*|LIBRARIES        =+ $(_SPACE_) "-L$(TOP)/%{_lib}/stubs" "-L$(TOP)/%{_lib}"|' \
    %{buildroot}%{_bindir}/nvcc.profile

for pkg in cuda-cudart-%{cuda_series} libcublas-%{cuda_series}; do
    for license in /usr/share/licenses/"$pkg"/*; do
        cp -a "$license" "%{buildroot}%{_licensedir}/%{name}-libs/$(basename "$license").${pkg}"
    done
done

for pkg in cuda-cudart-devel-%{cuda_series} cuda-driver-devel-%{cuda_series} cuda-nvcc-%{cuda_series} libcublas-devel-%{cuda_series} cuda-cccl-%{cuda_series} cuda-crt-%{cuda_series} cuda-culibos-devel-%{cuda_series} libnvptxcompiler-%{cuda_series} libnvvm-%{cuda_series}; do
    for license in /usr/share/licenses/"$pkg"/*; do
        cp -a "$license" "%{buildroot}%{_licensedir}/%{name}-devel/$(basename "$license").${pkg}"
    done
done

%check
sh %{SOURCE1} "%{buildroot}" "%{_prefix}" "%{_libdir}" "%{_bindir}" "%{_includedir}"

%files libs
%license %{_licensedir}/%{name}-libs/*
%{_libdir}/*.so.*

%files devel
%license %{_licensedir}/%{name}-devel/*
%{_bindir}/*
%{_includedir}/cuda
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/cmake/*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/stubs
%{_prefix}/nvvm
%{_prefix}/src/*

%changelog
* Tue May 05 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 13.2-1
- Repackage CUDA runtime and development files into standard Fedora paths.
