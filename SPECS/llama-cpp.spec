%global llama_build 11054
%global llama_tag b%{llama_build}
%global cuda_cmake_flags -Xcompiler=-fPIE

Name:           llama-cpp
Version:        %{llama_build}
Release:        1%{?dist}
Summary:        llama.cpp tools with OpenMP, CUDA, and OpenVINO support
License:        MIT
URL:            https://github.com/ggml-org/llama.cpp

Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/tags/%{llama_tag}.tar.gz
Source1:        https://github.com/ggml-org/llama.cpp/releases/download/%{llama_tag}/llama-%{llama_tag}-ui.tar.gz

Patch1:         0001-llama-cpp-openvino-optional-opencl.patch
Patch2:         0002-llama-cpp-static-tool-helpers.patch
Patch3:         0003-llama-cpp-gcc16-warning-fixes.patch

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  cuda-devel
BuildRequires:  openvino-devel
BuildRequires:  tbb-devel

%description
llama.cpp provides tools for local inference with GGUF language models. This
package includes the llama-cli and llama-server tools with the CPU OpenMP
backend, the CUDA backend, and the OpenVINO backend for Intel hardware.

This build is intended for runtime use.

%package tools
Summary:        Additional llama.cpp command-line tools
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description tools
Additional llama.cpp command-line tools built against the CPU OpenMP, CUDA,
and OpenVINO backends.

%prep
%autosetup -n llama.cpp-%{llama_tag} -p1
%setup -q -T -D -n llama.cpp-%{llama_tag} -a1

mv -T llama-%{llama_tag} tools/ui/dist

%build
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_CUDA_FLAGS=%{cuda_cmake_flags} \
    -DCMAKE_CUDA_ARCHITECTURES=86-real\;89-real\;120a-real\;121a-real \
    -DBUILD_SHARED_LIBS=ON \
    -DLLAMA_BUILD_APP=ON \
    -DLLAMA_BUILD_COMMON=ON \
    -DLLAMA_BUILD_EXAMPLES=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_BUILD_UI=OFF \
    -DLLAMA_USE_PREBUILT_UI=OFF \
    -DLLAMA_TESTS_INSTALL=OFF \
    -DLLAMA_TOOLS_INSTALL=ON \
    -DLLAMA_OPENSSL=OFF \
    -DLLAMA_LLGUIDANCE=OFF \
    -DLLAMA_SUBPROCESS=ON \
    -DLLAMA_BUILD_NUMBER=%{llama_build} \
    -DLLAMA_BUILD_COMMIT=%{llama_tag} \
    -DGGML_BUILD_EXAMPLES=OFF \
    -DGGML_BUILD_TESTS=OFF \
    -DGGML_BACKEND_DL=OFF \
    -DGGML_NATIVE=OFF \
    -DGGML_CPU=ON \
    -DGGML_CPU_REPACK=ON \
    -DGGML_CPU_ALL_VARIANTS=OFF \
    -DGGML_SSE42=ON \
    -DGGML_AVX=ON \
    -DGGML_AVX2=ON \
    -DGGML_FMA=ON \
    -DGGML_F16C=ON \
    -DGGML_BMI2=ON \
    -DGGML_OPENMP=ON \
    -DGGML_LLAMAFILE=ON \
    -DGGML_CUDA=ON \
    -DGGML_CUDA_NCCL=OFF \
    -DGGML_CUDA_NO_PEER_COPY=OFF \
    -DGGML_CUDA_NO_VMM=OFF \
    -DGGML_CUDA_FA=ON \
    -DGGML_CUDA_GRAPHS=ON \
    -DGGML_BLAS=OFF \
    -DGGML_RPC=OFF \
    -DGGML_VULKAN=OFF \
    -DGGML_OPENCL=OFF \
    -DGGML_OPENVINO=ON \
    -DGGML_SYCL=OFF \
    -DGGML_HIP=OFF \
    -DGGML_METAL=OFF

%cmake_build

%install
%cmake_install

# clean up
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -f %{buildroot}%{_libdir}/*.so

%check
test -f %{_libdir}/stubs/libcuda.so
cuda_stub_dir=$(mktemp -d)
trap 'rm -rf -- "$cuda_stub_dir"' EXIT
ln -s %{_libdir}/stubs/libcuda.so "$cuda_stub_dir/libcuda.so.1"
LD_LIBRARY_PATH="$cuda_stub_dir:%{buildroot}%{_libdir}" %{buildroot}%{_bindir}/llama-cli --version >/dev/null
LD_LIBRARY_PATH="$cuda_stub_dir:%{buildroot}%{_libdir}" %{buildroot}%{_bindir}/llama-server --version >/dev/null

%files
%license LICENSE
%doc README.md
%{_bindir}/llama-cli
%{_bindir}/llama-server
%{_libdir}/libggml*.so.*
%{_libdir}/libllama*.so.*
%{_libdir}/libmtmd.so.*

%files tools
%{_bindir}/llama
%{_bindir}/llama-batched-bench
%{_bindir}/llama-bench
%{_bindir}/llama-completion
%{_bindir}/llama-cvector-generator
%{_bindir}/llama-export-lora
%{_bindir}/llama-fit-params
%{_bindir}/llama-gguf-split
%{_bindir}/llama-imatrix
%{_bindir}/llama-mtmd-cli
%{_bindir}/llama-perplexity
%{_bindir}/llama-quantize
%{_bindir}/llama-results
%{_bindir}/llama-tokenize
%{_bindir}/llama-tts

%changelog
* Sun Sep 20 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 11054-1
- Update to b11054.
- Build with CUDA 13.4 and the Fedora 44 default GCC 16 toolchain.
- Refresh downstream patches and build options.

* Mon Jun 1 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 9400-1
- Update to version 9409.
- New patch made OpenCL optional.

* Sat May 02 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 8994-1
- Dual-backend build with CUDA and OpenVINO runtime support.
