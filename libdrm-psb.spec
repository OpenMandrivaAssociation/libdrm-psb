%define major 2
%define libname %mklibname drm-psb %{major}
%define develname %mklibname drm-psb -d
%define staticdevelname %mklibname drm-psb -d -s

%define priority 500

Summary:	Userspace interface to kernel DRM services
Name:		libdrm-psb
Version:	2.3.0
Release:	%mkrel 8
Group:		Development/X11
License:	MIT/X11
URL:		http://xorg.freedesktop.org
Source0:	http://dri.freedesktop.org/libdrm/libdrm-%{version}.tar.bz2
# (fc) do not change permission if not requested
Patch0:		libdrm-2.3.0-perm.patch
# ttm support (from debian/patches in http://moblin.org/repos/projects/libdrm.git)
Patch1: 00_poulsbo_libdrm_update.patch
Patch2: 01_poulsbo_libdrm_update.patch
Patch3: 02_poulsbo_libdrm_update.patch
Patch4: 03_poulsbo_libdrm_update.patch
Patch5: 04_poulsbo_libdrm_update.patch
Patch6: 05_poulsbo_libdrm_update.patch
Patch7: 06_poulsbo_libdrm_update.patch
Patch8: 07_poulsbo_libdrm_update.patch
Patch9: 08_poulsbo_libdrm_update.patch
BuildRequires: x11-util-macros >= 1.0.1
BuildRoot:	%{_tmppath}/%{name}-root

%description
Userspace interface to kernel DRM services

%package -n	%{libname}
Summary:	Userspace interface to kernel DRM services
Group:		Development/X11
Provides:	%{name} = %{version}

%description -n	%{libname}
Userspace interface to kernel DRM services

%package -n	%{develname}
Summary:	Development files for %{name}
Group:		Development/X11
Requires:	%{name} >= %{version}
Requires:	%{libname} = %{version}
Provides:       %{name}-devel = %{version}-%{release}
Obsoletes:      %{mklibname drm 2 -d}

%description -n	%{develname}
Development files for %{name}

%package -n	%{staticdevelname}
Summary:	Static development files for %{name}
Group:		Development/X11
Requires:	%{name}-devel >= %{version}
Requires:	%{libname} = %{version}
Provides:       %{name}-static-devel = %{version}-%{release}
Obsoletes:      %{mklibname drm 2 -d -s}

%description -n	%{staticdevelname}
Static development files for %{name}

%prep

%setup -q -n libdrm-%{version}
%patch0 -p1 -b .perm
%patch1 -p1 -b .drm
%patch2 -p1 -b .drm
%patch3 -p1 -b .drm
%patch4 -p1 -b .drm
%patch5 -p1 -b .drm
%patch6 -p1 -b .drm
%patch7 -p1 -b .drm
%patch8 -p1 -b .drm
%patch9 -p1 -b .drm

%build
%configure2_5x \
    --x-includes=%{_includedir} \
    --x-libraries=%{_libdir} \
    --enable-static

%make

%install
rm -rf %{buildroot}

%makeinstall_std 

# move to custom libdrm-psb subdirs
mkdir -p %{buildroot}%{_libdir}/%{name}
mv %{buildroot}%{_libdir}/*.{so*,la,a} %{buildroot}%{_libdir}/%{name}

mkdir -p %{buildroot}%{_includedir}/%{name}
mv %{buildroot}%{_includedir}/drm %{buildroot}%{_includedir}/*.h %{buildroot}%{_includedir}/%{name}

mv %{buildroot}%{_libdir}/pkgconfig/libdrm.pc %{buildroot}%{_libdir}/pkgconfig/%{name}.pc

# prefer libdrm-psb to standard libdrm, and abuse GL alternatives to do that
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf <<EOF
%{_libdir}/%{name}
EOF

%post -n %{libname}
# FIXME: handle 2009.1 extra_modules
%{_sbindir}/update-alternatives --install \
	%{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf %{priority} \
%if %{mdkversion} >= 200900
	--slave %{_libdir}/xorg/modules/extensions/libdri.so libdri.so %{_libdir}/xorg/modules/extensions/standard/libdri.so \
%endif
%if %{mdkversion} >= 200800
	--slave %{_libdir}/xorg/modules/extensions/libglx.so libglx %{_libdir}/xorg/modules/extensions/standard/libglx.so
%endif
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig

%postun -n %{libname}
%{_sbindir}/update-alternatives --remove gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/%{name}/*.so.*
%{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf

%files -n %{develname}
%defattr(-,root,root)
%dir %{_includedir}/%{name}/drm
%{_includedir}/%{name}/drm/*.h
%{_includedir}/%{name}/*.h
%{_libdir}/%{name}/*.la
%{_libdir}/%{name}/*.so
%{_libdir}/pkgconfig/*.pc

%files -n %{staticdevelname}
%defattr(-,root,root)
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*.a
