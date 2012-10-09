%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get _python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%define modname fedoratagger
%define eggname fedora_tagger

Name:           fedora-tagger
Version:        0.2.3
Release:        1%{?dist}
Summary:        A web application for adding and ranking tags for Fedora packages

License:        LGPLv2
URL:            https://github.com/ralphbean/fedora-tagger
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  libcurl-devel
BuildRequires:  python-kitchen
BuildRequires:  python-nose
BuildRequires:  python-paste
BuildRequires:  python-paste-deploy
BuildRequires:  TurboGears2
BuildRequires:  python-pylons
BuildRequires:  python-mako
BuildRequires:  python-zope-sqlalchemy
%if %{?rhel}%{!?rhel:0} >= 6
BuildRequires:  python-sqlalchemy0.7
%else
BuildRequires:  python-sqlalchemy
%endif
BuildRequires:  python-repoze-what
BuildRequires:  python-repoze-who-friendlyform
BuildRequires:  python-repoze-what-pylons
BuildRequires:  python-repoze-who
BuildRequires:  python-repoze-what-plugins-sql
BuildRequires:  python-kitchen
BuildRequires:  pycurl
BuildRequires:  python-tw2-core
BuildRequires:  python-tw2-forms
BuildRequires:  python-tw2-jqplugins-ui
BuildRequires:  python-tw2-jqplugins-gritter
BuildRequires:  python-docutils
BuildRequires:  python-bunch
BuildRequires:  python-fedora
BuildRequires:  python-fedora-turbogears2
BuildRequires:  fedmsg >= 0.1.5
%if %{?rhel}%{!?rhel:0} >= 6
BuildRequires:  python-argparse
%endif

Requires:       TurboGears2
Requires:       python-mako
Requires:       python-zope-sqlalchemy
%if %{?rhel}%{!?rhel:0} >= 6
Requires:  python-sqlalchemy0.7
%else
Requires:  python-sqlalchemy
%endif
Requires:       python-repoze-what
Requires:       python-repoze-who-friendlyform
Requires:       python-repoze-what-pylons
Requires:       python-repoze-who
#Requires:       python-repoze-what-quickstart
Requires:       python-repoze-what-plugins-sql
Requires:       python-kitchen
Requires:       pycurl
Requires:       python-tw2-core
Requires:       python-tw2-jqplugins-gritter
Requires:       python-tw2-jqplugins-ui
Requires:       python-fedora-turbogears2
Requires:       python-psycopg2
Requires:       fedmsg >= 0.1.5
%if %{?rhel}%{!?rhel:0} >= 6
Requires:  python-argparse
%endif

%description
A web application for adding and ranking tags for Fedora packages.

%prep
%setup -q

%if %{?rhel}%{!?rhel:0} >= 6

# Make sure that epel/rhel picks up the correct version of webob
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"WebOb>=1.0\", \"sqlalchemy>=0.7\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py

%endif


%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}
%{__python} setup.py archive_tw2_resources -f -o %{buildroot}%{_datadir}/%{name}/public/toscawidgets -d fedora_tagger

rm -fr %{buildroot}%{python_sitelib}/migration

%{__mkdir_p} %{buildroot}%{_datadir}/%{name}/apache
%{__install} apache/%{modname}.wsgi %{buildroot}%{_datadir}/%{name}/apache/%{modname}.wsgi


%pre
%{_sbindir}/groupadd -r %{modname} &>/dev/null || :
%{_sbindir}/useradd  -r -s /sbin/nologin -d %{_datadir}/%{modname} -M \
              -c 'Fedora Tagger' -g %{modname} %{modname} &>/dev/null || :


%files
%doc README.rst
%{_datadir}/%{name}/
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{eggname}-%{version}-py%{pyver}.egg-info/

%changelog
* Tue Oct 09 2012 Ralph Bean <rbean@redhat.com> - 0.2.3-1
- More intelligent rank calculation.
- Unescape nested widgets to support tw2.core>=2.1.2.
* Fri Aug 17 2012 Ralph Bean <rbean@redhat.com> - 0.2.2-1
- Removing duplicates when updating from koji and yum.
- F17->F18
- Greater detail in fedmsg messages.
- No more .login fedmsg event.
- Export a yumdb.. migration of functionality from pkgdb.
* Mon Jul 30 2012 Ralph Bean <rbean@redhat.com> - 0.2.1-1
- Creating a fedoratagger user and group for mod_wsgi.
* Tue May 29 2012 Ralph Bean <rbean@redhat.com> - 0.2.0a-1
- First stab at fedmsg in stg.
* Fri May 25 2012 Ralph Bean <rbean@redhat.com> - 0.1.6-1
- Emergency revert of python-tgscheduler.  It was barfing on db01.
* Wed May 23 2012 Ralph Bean <rbean@redhat.com> - 0.1.5-1
- python-tgscheduler now handles updating package metadata.
- Removed a hardcoded link to the stg deployment of f-packages.
* Thu Apr 26 2012 Ralph Bean <rbean@redhat.com> - 0.1.4-1
- Added a controller method /_update to get new packages from pkgdb+yum
- Unicode safeguards in websetup/bootstrap.py
* Wed Apr 25 2012 Ralph Bean <rbean@redhat.com> - 0.1.3-1
- New version.  Fixes a typo-bug in the gritter notification
- Added LGPLv2 license.
* Wed Apr 25 2012 Ralph Bean <rbean@redhat.com> - 0.1.2-2
- Dependency fixes
- Removed the patch; using awk instead
* Thu Mar 29 2012 Ralph Bean <rbean@redhat.com> - 0.1.2-1
- Statistics window
- Toggle notifications
* Tue Feb 28 2012 Ralph Bean <rbean@redhat.com> - 0.1.1-1
- jQuery UI styling
- Statistics
- Toggle Notifications
- Misc fixups
* Mon Jan 09 2012 Luke Macken <lmacken@redhat.com> - 0.1-1
- Initial RPM package
