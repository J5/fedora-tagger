%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get _python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%define modname fedoratagger
%define eggname fedora_tagger

Name:           fedora-tagger
Version:        2.0.0a
Release:        1%{?dist}
Summary:        A web application for adding and ranking tags for Fedora packages

License:        LGPLv2
URL:            https://github.com/fedora-infra/fedora-tagger
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

%if %{?rhel}%{!?rhel:0} >= 6
BuildRequires:  python-sqlalchemy0.7
%else
BuildRequires:  python-sqlalchemy
%endif

BuildRequires:  python-flask
BuildRequires:  python-wtforms
BuildRequires:  python-flask-wtf
BuildRequires:  python-flask-Mako

BuildRequires:  python-kitchen
BuildRequires:  python-fedora

BuildRequires:  python-tw2.core
BuildRequires:  python-tw2.forms
BuildRequires:  python-tw2.jquery
BuildRequires:  python-tw2.jqplugins.ui
BuildRequires:  python-tw2.jqplugins.gritter

## Not needed for testing only when working with postgresql
#BuildRequires:  python-psycopg2

BuildRequires:  python-nose

%if %{?rhel}%{!?rhel:0} >= 6
Requires:  python-sqlalchemy0.7
%else
Requires:  python-sqlalchemy
%endif

Requires:  python-flask
Requires:  python-wtforms
Requires:  python-flask-wtf
Requires:  python-flask-Mako

Requires:  python-kitchen
Requires:  python-fedora

Requires:  python-tw2.core
Requires:  python-tw2.forms
Requires:  python-tw2.jquery
Requires:  python-tw2.jqplugins.ui
Requires:  python-tw2.jqplugins.gritter

Requires:  python-psycopg2

# Sad panda.  Oldschool mako doesn't handle encoding issues well.
%if %{?rhel}%{!?rhel:0} >= 6
BuildRequires:  python-mako0.4
Requires:       python-mako0.4
%endif


%description
A web application for adding and ranking tags for Fedora packages.

%prep
%setup -q

%if %{?rhel}%{!?rhel:0} >= 6
# Make sure that epel/rhel picks up the correct version of webob
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"Mako>=0.4.2\", \"sqlalchemy>=0.7\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py
%endif

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}
%{__python} setup.py archive_tw2_resources -f -o %{buildroot}%{_datadir}/%{modname}/toscawidgets -d fedoratagger

# This may not be necessary anymore
rm -fr %{buildroot}%{python_sitelib}/migration

%{__mkdir_p} %{buildroot}%{_datadir}/%{modname}/apache
%{__install} apache/%{modname}.wsgi %{buildroot}%{_datadir}/%{modname}/%{modname}.wsgi

%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{modname}/
%{__install} apache/%{modname}.cfg %{buildroot}%{_sysconfdir}/%{modname}/%{modname}.cfg

%pre
%{_sbindir}/groupadd -r %{modname} &>/dev/null || :
%{_sbindir}/useradd  -r -s /sbin/nologin -d %{_datadir}/%{modname} -M \
              -c 'Fedora Tagger' -g %{modname} %{modname} &>/dev/null || :

%files
%doc README.rst
%config %{_sysconfdir}/%{name}/
%{_datadir}/%{name}/
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{eggname}-%{version}-py%{pyver}.egg-info/

%changelog
* Fri Apr 05 2013 Ralph Bean <rbean@redhat.com> - 2.0.0a-1
- Initial packaging of rewrite against python-flask.

* Tue Oct 09 2012 Ralph Bean <rbean@redhat.com> - 0.2.3-5
- Don't spam the bus with users' entire voting histories.
* Tue Oct 09 2012 Ralph Bean <rbean@redhat.com> - 0.2.3-4
- Bugfix.  Iterators don't have a .__len__.
* Tue Oct 09 2012 Ralph Bean <rbean@redhat.com> - 0.2.3-3
- Bugfix.  Iterators don't have a .index method.
* Tue Oct 09 2012 Ralph Bean <rbean@redhat.com> - 0.2.3-2
- Reverse the rank ordering.
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