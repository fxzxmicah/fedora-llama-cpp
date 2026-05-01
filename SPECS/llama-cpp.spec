%global llama_build 8994
%global llama_tag b%{llama_build}
%global nccl_version 2.30.4
%global nccl_pkg_revision 1
%global cuda_series 13-2
%global cuda_root /usr/local/cuda-%(echo '%{cuda_series}' | tr '-' '.')
%global cuda_cmake_flags -Xcompiler=-fPIE

Name:           llama-cpp
Version:        %{llama_build}
Release:        1%{?dist}
Summary:        llama.cpp tools with OpenMP and CUDA support

License:        MIT AND BSD-3-Clause AND Apache-2.0
URL:            https://github.com/ggml-org/llama.cpp
Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/tags/%{llama_tag}.tar.gz
Source1:        https://github.com/NVIDIA/nccl/archive/refs/tags/v%{nccl_version}-%{nccl_pkg_revision}.tar.gz

Patch1:         0001-nccl-fix-nvtx-off-build.patch
Patch2:         0002-llama-cpp-propagate-nccl-link-dir.patch

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  cuda-cudart-devel-%{cuda_series}
BuildRequires:  cuda-driver-devel-%{cuda_series}
BuildRequires:  cuda-nvcc-%{cuda_series}
BuildRequires:  gcc-c++
BuildRequires:  libcublas-devel-%{cuda_series}
BuildRequires:  make
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(openssl)
BuildRequires:  python3

Requires:       libgomp%{?_isa}
Requires:       openssl-libs%{?_isa}

%ldconfig_scriptlets

# Keep bundled CUDA/NCCL libraries private. Installing them directly into
# %%{_libdir} would make this RPM globally provide NVIDIA libraries and risk
# conflicts with CUDA packages. llama.cpp binaries/libraries get RUNPATH below.
%global _privlibdir %{_libdir}/%{name}
%global __provides_exclude_from ^%{_privlibdir}/.*\\.so.*$
%global __requires_exclude ^(libcublas\\.so\\..*|libcublasLt\\.so\\..*|libcudart\\.so\\..*|libnccl\\.so\\..*)\\(\\).*

%description
llama.cpp provides tools for local inference with GGUF language models. This
package includes the llama-cli and llama-server tools with the CPU OpenMP
backend, the CUDA backend, and NCCL support.

The package bundles the proprietary CUDA runtime libraries needed by this
build, except libcuda.so.1, which is provided by the installed NVIDIA driver.

%prep
%autosetup -p1 -n llama.cpp-%{llama_tag} -a 1

%build
pushd nccl-%{nccl_version}-%{nccl_pkg_revision}
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_FLAGS=%{cuda_cmake_flags} \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/nccl-prefix \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCUDAToolkit_ROOT=%{cuda_root} \
    -DNVTX=OFF \
    -DPROFAPI=OFF \
    -DRDMA_CORE=OFF \
    -DMLX5DV=OFF \
    -DNET_PROFILER=OFF \
    -DBUILD_NCCL4PY=OFF \
    -DBUILD_NCCL_EP=OFF
%cmake_build --target nccl
mkdir -p %{_builddir}/nccl-prefix/include %{_builddir}/nccl-prefix/%{_lib}
cp -a %{_vpath_builddir}/include/nccl*.h %{_builddir}/nccl-prefix/include/
cp -a %{_vpath_builddir}/lib/libnccl.so* %{_builddir}/nccl-prefix/%{_lib}/
popd

%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_FLAGS=%{cuda_cmake_flags} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_RPATH=%{_privlibdir} \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON \
    -DCUDAToolkit_ROOT=%{cuda_root} \
    -DBUILD_SHARED_LIBS=ON \
    -DLLAMA_BUILD_COMMON=ON \
    -DLLAMA_BUILD_EXAMPLES=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_BUILD_WEBUI=ON \
    -DLLAMA_TESTS_INSTALL=OFF \
    -DLLAMA_TOOLS_INSTALL=OFF \
    -DLLAMA_OPENSSL=ON \
    -DLLAMA_LLGUIDANCE=OFF \
    -DLLAMA_BUILD_NUMBER=%{llama_build} \
    -DLLAMA_BUILD_COMMIT=%{llama_tag} \
    -DGGML_BUILD_EXAMPLES=OFF \
    -DGGML_BUILD_TESTS=OFF \
    -DGGML_NATIVE=OFF \
    -DGGML_SSE42=ON \
    -DGGML_AVX=ON \
    -DGGML_AVX2=ON \
    -DGGML_FMA=ON \
    -DGGML_F16C=ON \
    -DGGML_BMI2=ON \
    -DGGML_OPENMP=ON \
    -DGGML_CUDA=ON \
    -DGGML_CUDA_NCCL=ON \
    -DGGML_BLAS=OFF \
    -DGGML_RPC=OFF \
    -DGGML_VULKAN=OFF \
    -DGGML_OPENCL=OFF \
    -DGGML_OPENVINO=OFF \
    -DGGML_SYCL=OFF \
    -DGGML_HIP=OFF \
    -DGGML_METAL=OFF \
    -DNCCL_ROOT=%{_builddir}/nccl-prefix
%cmake_build --target llama-cli --target llama-server

%install
%cmake_install

install -Dpm0755 %{_vpath_builddir}/bin/llama-cli %{buildroot}%{_bindir}/llama-cli
install -Dpm0755 %{_vpath_builddir}/bin/llama-server %{buildroot}%{_bindir}/llama-server

mkdir -p %{buildroot}%{_privlibdir}
cp -a %{_builddir}/nccl-prefix/%{_lib}/libnccl.so.* %{buildroot}%{_privlibdir}/

for lib in libcudart.so libcublas.so libcublasLt.so; do
    matches=$(find %{cuda_root}/targets/x86_64-linux/lib -maxdepth 1 \( -name "$lib.*" -type f -o -name "$lib.*" -type l \))
    if [ -z "$matches" ]; then
        echo "Could not locate $lib" >&2
        exit 1
    fi
    cp -a $matches %{buildroot}%{_privlibdir}/
done

mkdir -p %{buildroot}%{_licensedir}/%{name}/cuda
for pkg in $(rpm -qa 'cuda-cudart*' 'libcublas*'); do
    for license in /usr/share/licenses/"$pkg"/*; do
        cp -a "$license" "%{buildroot}%{_licensedir}/%{name}/cuda/$(basename "$license").${pkg}"
    done
done
cp -a nccl-%{nccl_version}-%{nccl_pkg_revision}/LICENSE.txt \
    %{buildroot}%{_licensedir}/%{name}/LICENSE.nccl
cp -a LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE.%{name}

if ! find %{buildroot}%{_licensedir}/%{name}/cuda -type f | grep -q .; then
    echo "Could not locate CUDA/cuBLAS license files" >&2
    exit 1
fi

rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -f %{buildroot}%{_libdir}/libggml*.so
rm -f %{buildroot}%{_libdir}/libllama*.so
rm -f %{buildroot}%{_libdir}/*.a

%files
%license %{_licensedir}/%{name}/
%doc README.md
%{_bindir}/llama-cli
%{_bindir}/llama-server
%{_bindir}/convert_hf_to_gguf.py
%{_libdir}/libggml*.so.*
%{_libdir}/libllama*.so.*
%dir %{_privlibdir}
%{_privlibdir}/libcublas.so.*
%{_privlibdir}/libcublasLt.so.*
%{_privlibdir}/libcudart.so.*
%{_privlibdir}/libnccl.so.*

%changelog
* Fri May 01 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 8994-1
- Initial RPM with OpenMP, CUDA, NCCL, llama-cli, and llama-server.
