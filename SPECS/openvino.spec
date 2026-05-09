%global openvino_version 2026.1.0
%global openvino_tag %{openvino_version}
%global ov_onednn_cpu_commit 6b6492b1ea9ef5ca9ff3c5c59ed71dcca683a446
%global ov_mlas_commit d1bc25ec4660cddd87804fcf03b2411b5dfb2e94
%global ov_onednn_gpu_commit 470e87eb07bdc805937a9f6d45d5c3a0fe4d27e7
%global ov_level_zero_ext_commit 42768cc73e74f6d371bd9dd51b1860b07774e7ec

%global debug_package %{nil}

Name:           openvino
Version:        %{openvino_version}
Release:        1%{?dist}
Summary:        Intel® Distribution of OpenVINO™ toolkit
License:        Apache-2.0
URL:            https://github.com/openvinotoolkit/openvino/

Source0:        https://github.com/openvinotoolkit/openvino/archive/refs/tags/%{openvino_tag}.tar.gz
Source1:        https://github.com/openvinotoolkit/oneDNN/archive/%{ov_onednn_cpu_commit}/oneDNN-%{ov_onednn_cpu_commit}.tar.gz
Source2:        https://github.com/openvinotoolkit/mlas/archive/%{ov_mlas_commit}/mlas-%{ov_mlas_commit}.tar.gz
Source3:        https://github.com/oneapi-src/oneDNN/archive/%{ov_onednn_gpu_commit}/oneDNN-%{ov_onednn_gpu_commit}.tar.gz
Source4:        https://github.com/intel/level-zero-npu-extensions/archive/%{ov_level_zero_ext_commit}/level-zero-npu-extensions-%{ov_level_zero_ext_commit}.tar.gz

Patch1:         0001-openvino-dependencies-package-name.patch
Patch2:         0002-openvino-xbyak-system-includes.patch

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  flatbuffers-compiler
BuildRequires:  oneapi-level-zero-devel
BuildRequires:  ocl-icd-devel
BuildRequires:  cmake(xbyak)
BuildRequires:  cmake(libxml2)
BuildRequires:  cmake(pugixml)
BuildRequires:  cmake(nlohmann_json)
BuildRequires:  cmake(flatbuffers)
BuildRequires:  cmake(tbb)
BuildRequires:  cmake(zlib)
BuildRequires:  python3

%description
Intel® Distribution of OpenVINO™ toolkit is a tool for optimizing and deploying
inference solutions using deep learning models.

%package libs
Summary:    OpenVINO runtime libraries

%description libs
The OpenVINO runtime libraries and plugins required to run inference.

%package devel
Summary:    OpenVINO development files
Requires:   %{name}-libs = %{version}-%{release}

%description devel
Header files and CMake configuration files for developing applications with OpenVINO.

%prep
%autosetup -n openvino-%{openvino_tag} -p1
%setup -q -T -D -n openvino-%{openvino_tag} -a1 -a2 -a3 -a4

mv -T oneDNN-%{ov_onednn_cpu_commit} src/plugins/intel_cpu/thirdparty/onednn
mv -T mlas-%{ov_mlas_commit} src/plugins/intel_cpu/thirdparty/mlas
mv -T oneDNN-%{ov_onednn_gpu_commit} src/plugins/intel_gpu/thirdparty/onednn_gpu
mv -T level-zero-npu-extensions-%{ov_level_zero_ext_commit} src/plugins/intel_npu/thirdparty/level-zero-ext

%build
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DBUILD_SHARED_LIBS=ON \
    -DCPACK_GENERATOR=RPM \
    -DENABLE_TESTS=OFF \
    -DENABLE_SAMPLES=OFF \
    -DENABLE_DOCS=OFF \
    -DENABLE_TEMPLATE=OFF \
    -DENABLE_MULTI=OFF \
    -DENABLE_AUTO=OFF \
    -DENABLE_AUTO_BATCH=OFF \
    -DENABLE_HETERO=OFF \
    -DENABLE_PROXY=OFF \
    -DENABLE_PROFILING_ITT=OFF \
    -DENABLE_PROFILING_FIRST_INFERENCE=OFF \
    -DENABLE_JS=OFF \
    -DENABLE_INTEL_CPU=ON \
    -DENABLE_INTEL_GPU=ON \
    -DENABLE_INTEL_NPU=ON \
    -DENABLE_INTEL_NPU_INTERNAL=OFF \
    -DENABLE_INTEL_NPU_PROTOPIPE=OFF \
    -DENABLE_INTEL_NPU_COMPILER=OFF \
    -DENABLE_PLUGINS_XML=ON \
    -DENABLE_PKGCONFIG_GEN=OFF \
    -DENABLE_PYTHON=OFF \
    -DENABLE_PYTHON_PACKAGING=OFF \
    -DENABLE_SYSTEM_TBB=ON \
    -DENABLE_SYSTEM_PUGIXML=ON \
    -DENABLE_SYSTEM_OPENCL=ON \
    -DENABLE_SYSTEM_LEVEL_ZERO=ON \
    -DENABLE_SYSTEM_FLATBUFFERS=ON \
    -DENABLE_OV_ONNX_FRONTEND=OFF \
    -DENABLE_OV_PADDLE_FRONTEND=OFF \
    -DENABLE_OV_IR_FRONTEND=OFF \
    -DENABLE_OV_PYTORCH_FRONTEND=OFF \
    -DENABLE_OV_JAX_FRONTEND=OFF \
    -DENABLE_OV_TF_FRONTEND=OFF \
    -DENABLE_OV_TF_LITE_FRONTEND=OFF \
    -DENABLE_WHEEL=OFF

%cmake_build

%install
%cmake_install

# clean up
rm -rf %{buildroot}%{_datadir}/openvino
rm -rf %{buildroot}%{_datadir}/doc

%files libs
%license LICENSE
%{_libdir}/openvino-%{version}
%{_libdir}/libopenvino*.so.*

%files devel
%doc README.md
%{_includedir}/openvino/
%{_libdir}/cmake/openvino%{version}
%{_libdir}/libopenvino*.so

%changelog
* Sat May 02 2026 Fxzx micah <48860358+fxzxmicah@users.noreply.github.com> - 2026.1.0-1
- Init package.
