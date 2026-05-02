%global llama_build 8994
%global llama_tag b%{llama_build}
%global openvino_version 2026.1.0
%global openvino_tag %{openvino_version}
%global cuda_series 13-2
%global cuda_root /usr/local/cuda-%(echo '%{cuda_series}' | tr '-' '.')
%global cuda_cmake_flags -Xcompiler=-fPIE
%global _privlibdir %{_libdir}/%{name}

Name:           llama-cpp
Version:        %{llama_build}
Release:        1%{?dist}
Summary:        llama.cpp tools with OpenMP, CUDA, and OpenVINO support

License:        MIT AND BSD-3-Clause AND Apache-2.0
URL:            https://github.com/ggml-org/llama.cpp
Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/tags/%{llama_tag}.tar.gz
Source1:        https://github.com/openvinotoolkit/openvino/archive/refs/tags/%{openvino_tag}.tar.gz

Patch1:         0001-llama-cpp-cudatoolkit-root-path.patch

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  cuda-cudart-devel-%{cuda_series}
BuildRequires:  cuda-driver-devel-%{cuda_series}
BuildRequires:  cuda-nvcc-%{cuda_series}
BuildRequires:  gcc-c++
BuildRequires:  libcublas-devel-%{cuda_series}
BuildRequires:  make
BuildRequires:  ninja-build
BuildRequires:  ocl-icd-devel
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  python3

%ldconfig_scriptlets

# Keep bundled CUDA and OpenVINO runtime libraries private. Installing them
# directly into %%{_libdir} would make this RPM globally provide libraries that
# normally belong to external runtimes and development packages.
%global __provides_exclude_from ^%{_privlibdir}/.*\\.so.*$
%global __requires_exclude ^(libcublas\\.so\\..*|libcublasLt\\.so\\..*|libcudart\\.so\\..*|libopenvino.*|libtbb.*)\\(\\).*

%description
llama.cpp provides tools for local inference with GGUF language models. This
package includes the llama-cli and llama-server tools with the CPU OpenMP
backend, the CUDA backend, and the OpenVINO backend for Intel hardware.

This build is intended for runtime use. It does not include NCCL or multi-GPU
CUDA support.

%prep
%autosetup -p1 -n llama.cpp-%{llama_tag} -a 1

%build
pushd openvino-%{openvino_version}
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DBUILD_SHARED_LIBS=ON \
    -DENABLE_TESTS=OFF \
    -DENABLE_SAMPLES=OFF \
    -DENABLE_DOCS=OFF \
    -DENABLE_TEMPLATE=OFF \
    -DENABLE_MULTI=OFF \
    -DENABLE_AUTO=OFF \
    -DENABLE_AUTO_BATCH=OFF \
    -DENABLE_HETERO=OFF \
    -DENABLE_PROXY=OFF \
    -DENABLE_INTEL_CPU=ON \
    -DENABLE_INTEL_GPU=ON \
    -DENABLE_INTEL_NPU=ON \
    -DENABLE_PLUGINS_XML=ON \
    -DENABLE_PKGCONFIG_GEN=OFF \
    -DENABLE_OV_ONNX_FRONTEND=OFF \
    -DENABLE_OV_PADDLE_FRONTEND=OFF \
    -DENABLE_OV_IR_FRONTEND=OFF \
    -DENABLE_OV_PYTORCH_FRONTEND=OFF \
    -DENABLE_OV_JAX_FRONTEND=OFF \
    -DENABLE_OV_TF_FRONTEND=OFF \
    -DENABLE_OV_TF_LITE_FRONTEND=OFF
%cmake_build
%cmake_install
popd

%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_FLAGS=%{cuda_cmake_flags} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_RPATH=%{_privlibdir} \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON \
    -DCUDAToolkit_ROOT=%{cuda_root} \
    -DOpenVINO_DIR=%{buildroot}%{_libdir}/cmake/openvino%{openvino_version} \
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
    -DGGML_CUDA_NCCL=OFF \
    -DGGML_BLAS=OFF \
    -DGGML_RPC=OFF \
    -DGGML_VULKAN=OFF \
    -DGGML_OPENCL=OFF \
    -DGGML_OPENVINO=ON \
    -DGGML_SYCL=OFF \
    -DGGML_HIP=OFF \
    -DGGML_METAL=OFF
%cmake_build --target llama-cli --target llama-server

%install
%cmake_install

install -Dpm0755 %{_vpath_builddir}/bin/llama-cli %{buildroot}%{_bindir}/llama-cli

mkdir -p %{buildroot}%{_privlibdir}

for lib in libcudart.so libcublas.so libcublasLt.so; do
    matches=$(find %{cuda_root}/targets/x86_64-linux/lib -maxdepth 1 \( -name "$lib.*" -type f -o -name "$lib.*" -type l \))
    if [ -z "$matches" ]; then
        echo "Could not locate $lib" >&2
        exit 1
    fi
    cp -a $matches %{buildroot}%{_privlibdir}/
done

cp -a %{buildroot}%{_libdir}/libopenvino*.so.* %{buildroot}%{_privlibdir}/
cp -a %{buildroot}%{_libdir}/libtbb*.so.* %{buildroot}%{_privlibdir}/
cp -a %{buildroot}%{_libdir}/openvino-%{openvino_version}/* %{buildroot}%{_privlibdir}/

mkdir -p %{buildroot}%{_licensedir}/%{name}/cuda
for pkg in cuda-cudart-%{cuda_series} libcublas-%{cuda_series}; do
    for license in /usr/share/licenses/"$pkg"/*; do
        cp -a "$license" "%{buildroot}%{_licensedir}/%{name}/cuda/$(basename "$license").${pkg}"
    done
done
cp -a openvino-%{openvino_version}/LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE.openvino
cp -a LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -f %{buildroot}%{_libdir}/*.so

%files
%license %{_licensedir}/%{name}/
%doc README.md
%{_bindir}/llama-cli
%{_bindir}/llama-server
%{_bindir}/convert_hf_to_gguf.py
%{_libdir}/libggml*.so.*
%{_libdir}/libllama*.so.*
%{_libdir}/libmtmd.so.*
%{_privlibdir}

%changelog
* Sat May 02 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 8994-1
- Dual-backend build with CUDA and OpenVINO runtime support.
