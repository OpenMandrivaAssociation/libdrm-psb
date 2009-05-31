%define major 2
%define libname %mklibname drm-psb %{major}
%define develname %mklibname drm-psb -d
%define staticdevelname %mklibname drm-psb -d -s

%define extra_module_dir        %{_libdir}/xorg/extra-modules
%define xorg1_6_extra_modules	%{_libdir}/xorg/xorg-1.6-extra-modules
%define priority 500

%define _enable_libtoolize 1

Summary:	Userspace interface to kernel DRM services
Name:		libdrm-psb
Version:	2.3.0
Release:	%mkrel 23
Group:		Development/X11
License:	MIT/X11
URL:		http://xorg.freedesktop.org
Source0:	libdrm_%{version}-23.tar.gz
# (fc) do not change permission if not requested
# (blino) rediff for ttm/psb branch
Patch0:		libdrm-psb-2.3.0-perm.patch
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

%setup -q -n libdrm
%patch0 -p1 -b .perm
autoreconf

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
%{_sbindir}/update-alternatives --install \
	%{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf %{priority} \
%if %{mdkversion} >= 200910
	--slave %{extra_module_dir} xorg_extra_modules %{xorg1_6_extra_modules}
%else
%if %{mdkversion} >= 200900
	--slave %{_libdir}/xorg/modules/extensions/libdri.so libdri.so %{_libdir}/xorg/modules/extensions/standard/libdri.so \
%endif
%if %{mdkversion} >= 200800
	--slave %{_libdir}/xorg/modules/extensions/libglx.so libglx %{_libdir}/xorg/modules/extensions/standard/libglx.so
%endif
%endif
# Call /sbin/ldconfig explicitely due to alternatives
/sbin/ldconfig

%postun -n %{libname}
if [ ! -f %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf ]; then
   %{_sbindir}/update-alternatives --remove gl_conf %{_sysconfdir}/ld.so.conf.d/GL/%{name}.conf
fi
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
