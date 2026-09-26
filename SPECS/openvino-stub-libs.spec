%global debug_package %{nil}
%global _build_id_links none
%global ov_spec_hash %(sha256sum SPECS/openvino.spec | cut -c1-12)
%global ov_sonames %(rpmspec -q --builtrpms --queryformat '%%{NAME} [%%{REQUIRENAME} ]\n' SPECS/openvino.spec | awk '$1 == "openvino-libs" { for (i = 2; i <= NF; i++) { name = $i; sub(/[()].*/, "", name); if (name ~ /^lib.+[.]so/) printf "%%s ", name } }')

Name:           openvino-stub-libs
Version:        1
Release:        1.%{ov_spec_hash}%{?dist}
Summary:        Build-only stubs for OpenVINO runtime dependencies
License:        MIT

ExclusiveArch:  x86_64
BuildRequires:  gcc
BuildRequires:  binutils

%description
When needed, this package contains nonfunctional shared libraries whose SONAMEs
satisfy openvino-libs dependencies while building against OpenVINO.
It must not be installed in a runtime environment.

%prep
%setup -q -c -T

%build
for soname in %{ov_sonames}; do
    gcc %{build_cflags} %{build_ldflags} -shared -fPIC \
        -Wl,-soname,"${soname}" -x c /dev/null -o "${soname}"
done

%install
install -d %{buildroot}%{_libdir}/openvino-stub-libs
for soname in %{ov_sonames}; do
    install -m 755 "${soname}" %{buildroot}%{_libdir}/openvino-stub-libs/
done

%check
for soname in %{ov_sonames}; do
    LC_ALL=C readelf -d "${soname}" | grep -F "Library soname: [${soname}]" >/dev/null
done

%files
%{_libdir}/openvino-stub-libs/
