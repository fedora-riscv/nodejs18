%if 0%{?rhel} && 0%{?rhel} < 8
%bcond_without bundled_zlib
%else
%bcond_with bundled_zlib
%endif

# LTO is currently broken on Node.js builds
%define _lto_cflags %{nil}

# Heavy-handed approach to avoiding issues with python
# bytecompiling files in the node_modules/ directory
%global __python %{python3}

# == Master Relase ==
# This is used by both the nodejs package and the npm subpackage that
# has a separate version - the name is special so that rpmdev-bumpspec
# will bump this rather than adding .1 to the end.
%global baserelease %autorelease

%{?!_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}

# == Node.js Version ==
# Note: Fedora should only ship LTS versions of Node.js (currently expected
# to be major versions with even numbers). The odd-numbered versions are new
# feature releases that are only supported for nine months, which is shorter
# than a Fedora release lifecycle.
%global nodejs_epoch 1
%global nodejs_major 18
%global nodejs_minor 15
%global nodejs_patch 0
# nodejs_soversion - from NODE_MODULE_VERSION in src/node_version.h
%global nodejs_soversion 108
%global nodejs_abi %{nodejs_soversion}
%global nodejs_version %{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}
%global nodejs_release %{baserelease}
%global nodejs_envr %{nodejs_epoch}:%{nodejs_version}-%{nodejs_release}

%global nodejs_datadir %{_datarootdir}/node-%{nodejs_major}

# Determine if this should be the default version for this Fedora release
# The default version will own /usr/bin/node and friends
%if 0%{?fedora} == 37 || 0%{?fedora} == 38
%global nodejs_default %{nodejs_major}
%endif

%global nodejs_default_sitelib %{_prefix}/lib/node_modules
%global nodejs_private_sitelib %{nodejs_default_sitelib}_%{nodejs_major}


# == Bundled Dependency Versions ==
# v8 - from deps/v8/include/v8-version.h
# Epoch is set to ensure clean upgrades from the old v8 package
%global v8_epoch 3
%global v8_major 10
%global v8_minor 2
%global v8_build 154
%global v8_patch 26
%global v8_version %{v8_major}.%{v8_minor}.%{v8_build}.%{v8_patch}
%global v8_release %{nodejs_epoch}.%{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}.%{nodejs_release}

# zlib - from deps/zlib/zlib.h
%global zlib_version 1.2.13

# c-ares - from deps/cares/include/ares_version.h
# https://github.com/nodejs/node/pull/9332
%global c_ares_version 1.18.1

# llhttp - from deps/llhttp/include/llhttp.h
%global llhttp_version 6.0.10

# libuv - from deps/uv/include/uv/version.h
%global libuv_version 1.44.2

# nghttp2 - from deps/nghttp2/lib/includes/nghttp2/nghttp2ver.h
%global nghttp2_version 1.51.0

# ICU - from tools/icu/current_ver.dep
%global icu_major 72
%global icu_minor 1
%global icu_version %{icu_major}.%{icu_minor}

%global icudatadir %{nodejs_datadir}/icudata
%{!?little_endian: %global little_endian %(%{python3} -c "import sys;print (0 if sys.byteorder=='big' else 1)")}
# " this line just fixes syntax highlighting for vim that is confused by the above and continues literal


# OpenSSL minimum version
%global openssl11_minimum 1:1.1.1
%global openssl30_minimum 1:3.0.2

# punycode - from lib/punycode.js
# Note: this was merged into the mainline since 0.6.x
# Note: this will be unmerged in an upcoming major release
%global punycode_version 2.1.0

# npm - from deps/npm/package.json
%global npm_epoch 1
%global npm_version 9.5.0

# In order to avoid needing to keep incrementing the release version for the
# main package forever, we will just construct one for npm that is guaranteed
# to increment safely. Changing this can only be done during an update when the
# base npm version number is increasing.
%global npm_release %{nodejs_epoch}.%{nodejs_major}.%{nodejs_minor}.%{nodejs_patch}.%{nodejs_release}

%global npm_envr %{npm_epoch}:%{npm_version}-%{npm_release}

# uvwasi - from deps/uvwasi/include/uvwasi.h
%global uvwasi_version 0.0.15

# histogram_c - assumed from timestamps
%global histogram_version 0.9.7


Name: nodejs18
Epoch: %{nodejs_epoch}
Version: %{nodejs_version}
Release: %{nodejs_release}
Summary: JavaScript runtime
License: MIT and ASL 2.0 and ISC and BSD
Group: Development/Languages
URL: http://nodejs.org/

ExclusiveArch: %{nodejs_arches}

# nodejs bundles openssl, but we use the system version in Fedora
# because openssl contains prohibited code, we remove openssl completely from
# the tarball, using the script in Source100
Source0: node-v%{nodejs_version}-stripped.tar.gz
Source1: npmrc
Source2: btest402.js
# The binary data that icu-small can use to get icu-full capability
Source3: https://github.com/unicode-org/icu/releases/download/release-%{icu_major}-%{icu_minor}/icu4c-%{icu_major}_%{icu_minor}-data-bin-b.zip
Source4: https://github.com/unicode-org/icu/releases/download/release-%{icu_major}-%{icu_minor}/icu4c-%{icu_major}_%{icu_minor}-data-bin-l.zip
Source100: nodejs-sources.sh

# These are full sources for dependencies included as WASM blobs in the source of Node itself.
# Note: These sources would also include pre-compiled WASM blobs… so they are adjusted not to.
# Recipes for creating these blobs are included in the sources.
# These are generated by nodejs-sources.sh
Source101: cjs-module-lexer-1.2.2-stripped.tar.gz
Source102: wasi-sdk-11.0-linux.tar.gz
Source111: undici-5.20.0-stripped.tar.gz
Source112: wasi-sdk-14.0-linux.tar.gz

Patch: 0001-Remove-unused-OpenSSL-config.patch

%if 0%{?nodejs_default}
%global pkgname nodejs
%package -n %{pkgname}
Summary: JavaScript runtime
%else
%global pkgname nodejs18
%endif

BuildRequires: make
BuildRequires: python%{python3_pkgversion}-devel
BuildRequires: python%{python3_pkgversion}-setuptools
BuildRequires: python%{python3_pkgversion}-jinja2
%if 0%{?rhel} && 0%{?rhel} < 9
BuildRequires: python-unversioned-command
%endif
%if %{with bundled_zlib}
Provides: bundled(zlib) = %{zlib_version}
%else
BuildRequires: zlib-devel
%endif
BuildRequires: brotli-devel
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires: devtoolset-11-gcc
BuildRequires: devtoolset-11-gcc-c++
%else
BuildRequires: gcc >= 8.3.0
BuildRequires: gcc-c++ >= 8.3.0
%endif

BuildRequires: jq

# needed to generate bundled provides for npm dependencies
# https://src.fedoraproject.org/rpms/nodejs/pull-request/2
# https://pagure.io/nodejs-packaging/pull-request/10
BuildRequires: nodejs-packaging

BuildRequires: chrpath
BuildRequires: libatomic
BuildRequires: ninja-build
BuildRequires: unzip

BuildRequires: systemtap-sdt-devel


Provides: nodejs = %{nodejs_envr}

%if %{with bundled}
Provides:      bundled(libuv) = %{libuv_version}
%else
BuildRequires: libuv-devel >= 1:%{libuv_version}
Requires:      libuv >= 1:%{libuv_version}
%endif

# Node.js frequently bumps this faster than Fedora can follow,
# so we will bundle it.
Provides: bundled(nghttp2) = %{nghttp2_version}

# Temporarily bundle llhttp because the upstream doesn't
# provide releases for it.
Provides: bundled(llhttp) = %{llhttp_version}


%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires: openssl11-devel >= %{openssl11_minimum}
Requires: openssl11 >= %{openssl11_minimum}
%global ssl_configure --shared-openssl --shared-openssl-includes=%{_includedir}/openssl11 --shared-openssl-libpath=%{_libdir}/openssl11
%else

%if 0%{?fedora} >= 36
BuildRequires: openssl >= %{openssl30_minimum}
BuildRequires: openssl-devel >= %{openssl30_minimum}
%global openssl_fips_configure --openssl-is-fips
%else
Requires: openssl >= %{openssl11_minimum}
BuildRequires: openssl-devel >= %{openssl11_minimum}
%global openssl_fips_configure %{nil}
%endif

%global ssl_configure --shared-openssl %{openssl_fips_configure}
%endif

%if 0%{?nodejs_default}
%global dtrace_configure --with-dtrace
%else
# dtrace is only installed for the default version
%global dtrace_configure %{nil}
%endif


# we need the system certificate store
Requires: ca-certificates

Requires: %{pkgname}-libs%{?_isa} = %{nodejs_envr}

%if 0%{?fedora} || 0%{?rhel} >= 8
# Pull in the docs and full-icu data by default
Recommends: %{pkgname}-docs = %{nodejs_envr}
Recommends: %{pkgname}-full-i18n%{?_isa} = %{nodejs_envr}
Recommends: %{pkgname}-npm >= %{npm_envr}
%endif

# we need ABI virtual provides where SONAMEs aren't enough/not present so deps
# break when binary compatibility is broken
Provides: nodejs(abi) = %{nodejs_abi}
Provides: nodejs(abi%{nodejs_major}) = %{nodejs_abi}

# this corresponds to the "engine" requirement in package.json
Provides: nodejs(engine) = %{nodejs_version}

# Node.js currently has a conflict with the 'node' package in Fedora
# The ham-radio group has agreed to rename their binary for us, but
# in the meantime, we're setting an explicit Conflicts: here
Conflicts: node <= 0.3.2-12

# The punycode module was absorbed into the standard library in v0.6.
# It still exists as a seperate package for the benefit of users of older
# versions.  Since we've never shipped anything older than v0.10 in Fedora,
# we don't need the seperate nodejs-punycode package, so we Provide it here so
# dependent packages don't need to override the dependency generator.
# See also: RHBZ#11511811
# UPDATE: punycode will be deprecated and so we should unbundle it in Node v8
# and use upstream module instead
# https://github.com/nodejs/node/commit/29e49fc286080215031a81effbd59eac092fff2f
Provides: nodejs-punycode = %{punycode_version}
Provides: npm(punycode) = %{punycode_version}

# Node.js has forked c-ares from upstream in an incompatible way, so we need
# to carry the bundled version internally.
# See https://github.com/nodejs/node/commit/766d063e0578c0f7758c3a965c971763f43fec85
Provides: bundled(c-ares) = %{c_ares_version}

# Node.js is closely tied to the version of v8 that is used with it. It makes
# sense to use the bundled version because upstream consistently breaks ABI
# even in point releases. Node.js upstream has now removed the ability to build
# against a shared system version entirely.
# See https://github.com/nodejs/node/commit/d726a177ed59c37cf5306983ed00ecd858cfbbef
Provides: bundled(v8) = %{v8_version}

# Node.js is bound to a specific version of ICU which may not match the OS
# We cannot pin the OS to this version of ICU because every update includes
# an ABI-break, so we'll use the bundled copy.
Provides: bundled(icu) = %{icu_version}

# Upstream added new dependencies, but so far they are not available in Fedora
# or there's no option to built it as a shared dependency, so we bundle them
Provides: bundled(uvwasi) = %{uvwasi_version}
Provides: bundled(histogram) = %{histogram_version}



%description
Node.js is a platform built on Chrome's JavaScript runtime \
for easily building fast, scalable network applications. \
Node.js uses an event-driven, non-blocking I/O model that \
makes it lightweight and efficient, perfect for data-intensive \
real-time applications that run across distributed devices.}


%if 0%{?nodejs_default}
%description -n %{pkgname}
Node.js is a platform built on Chrome's JavaScript runtime \
for easily building fast, scalable network applications. \
Node.js uses an event-driven, non-blocking I/O model that \
makes it lightweight and efficient, perfect for data-intensive \
real-time applications that run across distributed devices.}
%endif


%package -n %{pkgname}-devel
Summary: JavaScript runtime - development headers
Group: Development/Languages
Requires: %{pkgname}%{?_isa} = %{nodejs_envr}
Requires: %{pkgname}-libs%{?_isa} = %{nodejs_envr}
Requires: openssl-devel%{?_isa}
%if !%{with bundled_zlib}
Requires: zlib-devel%{?_isa}
%endif
Requires: brotli-devel%{?_isa}
Requires: nodejs-packaging

%if %{without bundled}
Requires: libuv-devel%{?_isa}
%endif

Provides: nodejs-devel = %{nodejs_envr}
Conflicts: nodejs-devel


%description -n %{pkgname}-devel
Development headers for the Node.js JavaScript runtime.


%package -n %{pkgname}-libs
Summary: Node.js and v8 libraries

# Compatibility for obsolete v8 package
%if 0%{?__isa_bits} == 64
Provides: libv8.so.%{v8_major}()(64bit) = %{v8_epoch}:%{v8_version}
Provides: libv8_libbase.so.%{v8_major}()(64bit) = %{v8_epoch}:%{v8_version}
Provides: libv8_libplatform.so.%{v8_major}()(64bit) = %{v8_epoch}:%{v8_version}
%else
# 32-bits
Provides: libv8.so.%{v8_major} = %{v8_epoch}:%{v8_version}
Provides: libv8_libbase.so.%{v8_major} = %{v8_epoch}:%{v8_version}
Provides: libv8_libplatform.so.%{v8_major} = %{v8_epoch}:%{v8_version}
%endif

Provides: v8 = %{v8_epoch}:%{v8_version}-%{nodejs_release}
Provides: v8%{?_isa} = %{v8_epoch}:%{v8_version}-%{nodejs_release}
Obsoletes: v8 < 1:6.7.17-10

Provides: nodejs-libs = %{nodejs_envr}

%description -n %{pkgname}-libs
Libraries to support Node.js and provide stable v8 interfaces.


%package -n %{pkgname}-full-i18n
Summary: Non-English locale data for Node.js
Requires: %{pkgname}%{?_isa} = %{nodejs_envr}


%description -n %{pkgname}-full-i18n
Optional data files to provide full-icu support for Node.js. Remove this
package to save space if non-English locales are not needed.


%package -n v8-%{v8_major}.%{v8_minor}-devel
Summary: v8 - development headers
Epoch: %{v8_epoch}
Version: %{v8_version}
Release: %{v8_release}
Requires: %{pkgname}-devel%{?_isa} = %{nodejs_envr}
Requires: %{pkgname}-libs%{?_isa} = %{nodejs_envr}
Provides: v8-devel = %{v8_epoch}:%{v8_version}-%{v8_release}

Conflicts: v8-devel
Conflicts: v8-314-devel


%description -n v8-%{v8_major}.%{v8_minor}-devel
Development headers for the v8 runtime.


%package -n %{pkgname}-npm
Summary: Node.js Package Manager
Epoch: %{npm_epoch}
Version: %{npm_version}
Release: %{npm_release}

# If we're using the companion NPM build, make sure to keep it in lock-step
# with the Node version.
Requires: %{pkgname} = %{nodejs_envr}
%if 0%{?fedora} || 0%{?rhel} >= 8
Recommends: %{pkgname}-docs = %{nodejs_envr}
%endif

# Do not add epoch to the virtual NPM provides or it will break
# the automatic dependency-generation script.
Provides: npm(npm) = %{npm_version}

# Satisfy dependency requests for "npm"
Provides: npm = %{npm_envr}

%if 0%{?nodejs_default}
# Obsolete the old 'npm' package
Obsoletes: npm < 1:9
%endif


%description -n %{pkgname}-npm
npm is a package manager for node.js. You can use it to install and publish
your node programs. It manages dependencies and does other cool stuff.


%package -n %{pkgname}-docs
Summary: Node.js API documentation
Group: Documentation
BuildArch: noarch
Requires(meta): %{pkgname} = %{nodejs_envr}

Provides: nodejs-docs = %{nodejs_envr}


%description -n %{pkgname}-docs
The API documentation for the Node.js JavaScript runtime.


%prep
%autosetup -p1 -n node-v%{nodejs_version}

# remove bundled dependencies that we aren't building
%if !%{with bundled_zlib}
rm -rf deps/zlib
%endif

rm -rf deps/brotli
rm -rf deps/v8/third_party/jinja2
rm -rf tools/inspector_protocol/jinja2

# check for correct versions of dependencies we are bundling
check_wasm_dep() {
  local -r name="$1" source="$2" packagejson="$3"
  local -r expected_version="$(jq -r '.version' "${packagejson}")"

  if ls "${source}"|grep -q --fixed-strings "${expected_version}"; then
    printf '%s version matches\n' "${name}" >&2
  else
    printf '%s version MISMATCH: %s !~ %s\n' "${name}" "${expected_version}" "${source}" >&2
    return 1
  fi
}

check_wasm_dep cjs-module-lexer '%{SOURCE101}' deps/cjs-module-lexer/package.json
check_wasm_dep undici           '%{SOURCE111}' deps/undici/src/package.json

# Replace any instances of unversioned python with python3
pfiles=( $(grep -rl python) )
%py3_shebang_fix ${pfiles[@]}


%build

# Activate DevToolset 11 on EPEL 7
%if 0%{?rhel} && 0%{?rhel} < 8
. /opt/rh/devtoolset-11/enable
%endif

# When compiled on armv7hl this package generates an out of range
# reference to the literal pool.  This is most likely a GCC issue.
%ifarch armv7hl
%define _lto_cflags %{nil}
%endif

# Decrease debuginfo verbosity to reduce memory consumption during final
# library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

export CC='%{__cc}'
export CXX='%{__cxx}'
export NODE_GYP_FORCE_PYTHON=%{python3}

# build with debugging symbols and add defines from libuv (#892601)
# Node's v8 breaks with GCC 6 because of incorrect usage of methods on
# NULL objects. We need to pass -fno-delete-null-pointer-checks
# 2022-07-14: There's a bug in either torque or gcc that causes a
# segmentation fault on ppc64le and s390x if compiled with -O2. Things
# run fine on -O1 and -O3, so we'll just go with -O3 (like upstream)
# while this gets sorted out.
extra_cflags=(
    -D_LARGEFILE_SOURCE
    -D_FILE_OFFSET_BITS=64
    -DZLIB_CONST
    -fno-delete-null-pointer-checks
    -O3
)
export CFLAGS="%{optflags} ${extra_cflags[*]}" CXXFLAGS="%{optflags} ${extra_cflags[*]}"
export LDFLAGS="%{build_ldflags}"

# Fake up the unversioned python executable because gyp calls it from the PATH
mkdir .bin
cwd=$(pwd)
ln -srf /usr/bin/python3 ./.bin/python
export PATH="${cwd}/.bin:$PATH"

%{python3} configure.py \
           --verbose \
           --ninja \
           --enable-lto \
           --prefix=%{_prefix} \
           --shared \
           --libdir=%{_lib} \
           %{ssl_configure} \
           %{dtrace_configure} \
           %{!?with_bundled_zlib:--shared-zlib} \
           --shared-brotli \
           --shared-libuv \
           --with-intl=small-icu \
           --with-icu-default-data-dir=%{icudatadir} \
           --without-corepack \
           --openssl-use-def-ca-store

%ninja_build -C out/Release


%install

# The ninja build does not put the shared library in the expected location, so
# we will move it.
mv out/Release/lib/libnode.so.%{nodejs_soversion} out/Release/
./tools/install.py install %{buildroot} %{_prefix}


# own the sitelib directory
mv %{buildroot}%{nodejs_default_sitelib} \
   %{buildroot}%{nodejs_private_sitelib}

%if 0%{?nodejs_default}
ln -srf %{buildroot}%{nodejs_private_sitelib} \
        %{buildroot}%{nodejs_default_sitelib}
%else
rm -f %{buildroot}%{_datadir}/systemtap/tapset/node.stp
%endif


# Set the binary permissions properly
chmod 0755 %{buildroot}/%{_bindir}/node
chrpath --delete %{buildroot}%{_bindir}/node

# Rename the node binary
mv %{buildroot}%{_bindir}/node %{buildroot}%{_bindir}/node-%{nodejs_major}

# Move the npm binary to npm-NODEJS_MAJOR
rm -f %{buildroot}%{_bindir}/npm

ln -srf %{buildroot}%{nodejs_private_sitelib}/npm/bin/npm-cli.js \
        %{buildroot}%{_bindir}/npm-%{nodejs_major}

# Move the npx binary to npm-NODEJS_MAJOR
rm -f %{buildroot}%{_bindir}/npx

ln -srf %{buildroot}%{nodejs_private_sitelib}/npm/bin/npx-cli.js \
        %{buildroot}%{_bindir}/npx-%{nodejs_major}

# Add the symlinks back for the default version
%if 0%{?nodejs_default}
ln -srf %{buildroot}%{_bindir}/node-%{nodejs_major} \
        %{buildroot}%{_bindir}/node

ln -srf %{buildroot}%{_bindir}/npm-%{nodejs_major} \
        %{buildroot}%{_bindir}/npm

ln -srf %{buildroot}%{_bindir}/npx-%{nodejs_major} \
        %{buildroot}%{_bindir}/npx
%endif

# Install library symlink
ln -srf %{buildroot}%{_libdir}/libnode.so.%{nodejs_soversion} \
        %{buildroot}%{_libdir}/libnode.so

# Install v8 compatibility symlinks
for header in %{buildroot}%{_includedir}/node/libplatform %{buildroot}%{_includedir}/node/v8*.h; do
    header=$(basename ${header})
    ln -sf ./node/${header} %{buildroot}%{_includedir}/${header}
done
ln -s ./node/cppgc %{buildroot}%{_includedir}/cppgc

for soname in libv8 libv8_libbase libv8_libplatform; do
    ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/%{pkgname}-${soname}.so
    ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/%{pkgname}-${soname}.so.%{v8_major}
done

%if 0%{?nodejs_default}
for soname in libv8 libv8_libbase libv8_libplatform; do
    ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/${soname}.so
    ln -s libnode.so.%{nodejs_soversion} %{buildroot}%{_libdir}/${soname}.so.%{v8_major}
done
%endif

# install documentation
mkdir -p %{buildroot}%{_pkgdocdir}/html
cp -pr doc/* %{buildroot}%{_pkgdocdir}/html
rm -f %{buildroot}%{_pkgdocdir}/html/nodejs.1

# node-gyp needs common.gypi too
mkdir -p %{buildroot}%{nodejs_datadir}
cp -p common.gypi %{buildroot}%{nodejs_datadir}

# The config.gypi file is platform-dependent, so rename it to not conflict
mv %{buildroot}%{_includedir}/node/config.gypi \
   %{buildroot}%{_includedir}/node/config-%{_arch}.gypi

# Install the GDB init tool into the documentation directory
mv %{buildroot}/%{_datadir}/doc/node/gdbinit %{buildroot}/%{_pkgdocdir}/gdbinit

mkdir -p %{buildroot}%{_mandir}/nodejs-%{nodejs_major}/man1 \
         %{buildroot}%{_mandir}/nodejs-%{nodejs_major}/man5 \
         %{buildroot}%{_mandir}/nodejs-%{nodejs_major}/man7 \
         %{buildroot}%{nodejs_default_sitelib}/npm/man \
         %{buildroot}%{nodejs_private_sitelib}/npm/man \
         %{buildroot}%{_pkgdocdir}/npm

# install manpage docs to mandir
cp -pr deps/npm/man/* \
       %{buildroot}%{_mandir}/nodejs-%{nodejs_major}/
rm -rf %{buildroot}%{nodejs_private_sitelib}/npm/man
ln -srf %{buildroot}%{_mandir}/nodejs-%{nodejs_major} \
        %{buildroot}%{nodejs_private_sitelib}/npm/man

%if 0%{?nodejs_default}
for i in 1 5 7; do
  mkdir -p %{buildroot}%{_mandir}/man${i}
  for manpage in %{buildroot}%{nodejs_private_sitelib}/npm/man/man$i/*; do
    basename=$(basename ${manpage})
    ln -srf %{buildroot}%{nodejs_private_sitelib}/npm/man/man${i}/${manpage} \
            %{buildroot}%{_mandir}/man${i}/${basename}
  done
done
%endif

# Install the node interpreter manpage
mv %{buildroot}%{_mandir}/man1/node.1 \
   %{buildroot}%{_mandir}/nodejs-%{nodejs_major}/man1/

%if 0%{?nodejs_default}
ln -srf %{buildroot}%{_mandir}/nodejs-%{nodejs_major}/man1/node.1 \
        %{buildroot}%{_mandir}/man1/
%endif

# Install Gatsby HTML documentation to %%{_pkgdocdir}
cp -pr deps/npm/docs %{buildroot}%{_pkgdocdir}/npm/
rm -rf %{buildroot}%{nodejs_private_sitelib}/npm/docs
ln -srf %{buildroot}%{_pkgdocdir}/npm %{buildroot}%{nodejs_private_sitelib}/npm/docs

# Node tries to install some python files into a documentation directory
# (and not the proper one). Remove them for now until we figure out what to
# do with them.
rm -f %{buildroot}/%{_defaultdocdir}/node/lldb_commands.py \
      %{buildroot}/%{_defaultdocdir}/node/lldbinit

# Some NPM bundled deps are executable but should not be. This causes
# unnecessary automatic dependencies to be added. Make them not executable.
# Skip the npm bin directory or the npm binary will not work.
find %{buildroot}%{nodejs_private_sitelib}/npm \
    -not -path "%{buildroot}%{nodejs_private_sitelib}/npm/bin/*" \
    -executable -type f \
    -exec chmod -x {} \;

# The above command is a little overzealous. Add a few permissions back.
chmod 0755 %{buildroot}%{nodejs_private_sitelib}/npm/node_modules/@npmcli/run-script/lib/node-gyp-bin/node-gyp
chmod 0755 %{buildroot}%{nodejs_private_sitelib}/npm/node_modules/node-gyp/bin/node-gyp.js

# Drop the NPM default configuration in place
%if 0%{?nodejs_default}
mkdir -p %{buildroot}%{_sysconfdir}
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/npmrc

# NPM upstream expects it to be in /usr/etc/npmrc, so we'll put a symlink here
# This is done in the interests of keeping /usr read-only.
mkdir -p %{buildroot}%{_prefix}/etc
ln -rsf %{buildroot}%{_sysconfdir}/npmrc \
        %{buildroot}%{_prefix}/etc/npmrc
%endif

# Install the full-icu data files
mkdir -p %{buildroot}%{icudatadir}
%if 0%{?little_endian}
unzip -d %{buildroot}%{icudatadir} %{SOURCE4} icudt%{icu_major}l.dat
%else
unzip -d %{buildroot}%{icudatadir} %{SOURCE3} icudt%{icu_major}b.dat
%endif


%check
# Fail the build if the versions don't match
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node-%{nodejs_major} -e "require('assert').equal(process.versions.node, '%{nodejs_version}')"
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node-%{nodejs_major} -e "require('assert').equal(process.versions.v8.replace(/-node\.\d+$/, ''), '%{v8_version}')"
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node-%{nodejs_major} -e "require('assert').equal(process.versions.ares.replace(/-DEV$/, ''), '%{c_ares_version}')"

# Ensure we have punycode and that the version matches
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node-%{nodejs_major} -e "require(\"assert\").equal(require(\"punycode\").version, '%{punycode_version}')"

# Ensure we have npm and that the version matches
LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}%{_bindir}/node-%{nodejs_major} %{buildroot}%{_bindir}/npm-%{nodejs_major} version --json |jq -e '.npm == "%{npm_version}"'

# Make sure i18n support is working
NODE_PATH=%{buildroot}%{_prefix}/lib/node_modules:%{buildroot}%{nodejs_private_sitelib}/npm/node_modules LD_LIBRARY_PATH=%{buildroot}%{_libdir} %{buildroot}/%{_bindir}/node-%{nodejs_major} --icu-data-dir=%{buildroot}%{icudatadir} %{SOURCE2}


%if 0%{?rhel} && 0%{?rhel} < 8
%pretrans %{pkgname}-npm -p <lua>
-- Remove all of the symlinks from the bundled npm node_modules directory
base_path = "%{_prefix}/lib/node_modules/npm/node_modules/"
d_st = posix.stat(base_path)
if d_st then
  for f in posix.files(base_path) do
    path = base_path..f
    st = posix.stat(path)
    if st and st.type == "link" then
      os.remove(path)
    end
  end
end
%endif

# This can be removed once F37 is EOL
%pretrans -n %{pkgname} -p <lua>
path = "/usr/lib/node_modules"
st = posix.stat(path)
if st and st.type == "directory" then
  status = os.rename(path, path .. ".rpmmoved")
  if not status then
    suffix = 0
    while not status do
      suffix = suffix + 1
      status = os.rename(path .. ".rpmmoved", path .. ".rpmmoved." .. suffix)
    end
    os.rename(path, path .. ".rpmmoved")
  end
end


%files -n %{pkgname}
%doc CHANGELOG.md onboarding.md GOVERNANCE.md README.md

%if 0%{?nodejs_default}
%{_bindir}/node
%doc %{_mandir}/man1/node.1*
%{nodejs_default_sitelib}

%dir %{_datadir}/systemtap
%dir %{_datadir}/systemtap/tapset
%{_datadir}/systemtap/tapset/node.stp
%dir %{_usr}/lib/dtrace
%{_usr}/lib/dtrace/node.d

%endif

%{_bindir}/node-%{nodejs_major}
%{nodejs_private_sitelib}

%doc %{_mandir}/nodejs-%{nodejs_major}/man1/node.1*


%files -n %{pkgname}-devel
%{_includedir}/node
%{_libdir}/libnode.so
%{nodejs_datadir}/common.gypi
%{_pkgdocdir}/gdbinit


%files -n %{pkgname}-full-i18n
%dir %{icudatadir}
%{icudatadir}/icudt%{icu_major}*.dat


%files -n %{pkgname}-libs
%license LICENSE
%{_libdir}/libnode.so.%{nodejs_soversion}
%{_libdir}/%{pkgname}-libv8.so.%{v8_major}
%{_libdir}/%{pkgname}-libv8_libbase.so.%{v8_major}
%{_libdir}/%{pkgname}-libv8_libplatform.so.%{v8_major}
%dir %{nodejs_datadir}/
%if 0%{?nodejs_default}
%{_libdir}/libv8.so.%{v8_major}
%{_libdir}/libv8_libbase.so.%{v8_major}
%{_libdir}/libv8_libplatform.so.%{v8_major}
%endif

%files -n v8-%{v8_major}.%{v8_minor}-devel
%{_includedir}/libplatform
%{_includedir}/v8*.h
%{_includedir}/cppgc
%{_libdir}/%{pkgname}-libv8.so
%{_libdir}/%{pkgname}-libv8_libbase.so
%{_libdir}/%{pkgname}-libv8_libplatform.so
%{_libdir}/libv8.so
%{_libdir}/libv8_libbase.so
%{_libdir}/libv8_libplatform.so


%files -n %{pkgname}-npm
%if 0%{?nodejs_default}
%{_bindir}/npm
%{_bindir}/npx
%{_prefix}/etc/npmrc
%config(noreplace) %{_sysconfdir}/npmrc
%ghost %{_sysconfdir}/npmignore

%doc %{_mandir}/man*/
%exclude %doc %{_mandir}/man1/node.1*
%endif

%{_bindir}/npm-%{nodejs_major}
%{_bindir}/npx-%{nodejs_major}
%{nodejs_private_sitelib}/npm

%doc %{_mandir}/nodejs-%{nodejs_major}/
%exclude %doc %{_mandir}/nodejs-%{nodejs_major}/man1/node.1*


%files -n %{pkgname}-docs
%doc doc
%dir %{_pkgdocdir}
%{_pkgdocdir}/html
%{_pkgdocdir}/npm/docs


%changelog
%autochangelog
