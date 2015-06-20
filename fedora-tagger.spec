%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get _python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%define modname fedoratagger
%define eggname fedora_tagger

Name:           fedora-tagger
Version:        2.3.1
Release:        1%{?dist}
Summary:        A web application for adding and ranking tags for Fedora packages

License:        LGPLv2
URL:            https://github.com/fedora-infra/fedora-tagger
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-setuptools

%if %{?rhel}%{!?rhel:0} <= 6
BuildRequires:  python-sqlalchemy0.7
BuildRequires:  python-ordereddict
%else
BuildRequires:  python-sqlalchemy
%endif

BuildRequires:  python-flask
BuildRequires:  python-wtforms
BuildRequires:  python-flask-wtf
BuildRequires:  python-flask-mako
BuildRequires:  python-requests
BuildRequires:  PyYAML
BuildRequires:  python-alembic

BuildRequires:  python-kitchen
BuildRequires:  python-fedora
BuildRequires:  python-fedora-flask
BuildRequires:  python-openid
BuildRequires:  python-openid-cla
BuildRequires:  python-openid-teams

BuildRequires:  python-tw2-core
BuildRequires:  python-tw2-forms
BuildRequires:  python-tw2-jquery
BuildRequires:  python-tw2-jqplugins-ui
BuildRequires:  python-tw2-jqplugins-gritter

BuildRequires:  fedmsg
BuildRequires:  python-pkgwat-api
BuildRequires:  python-docutils
BuildRequires:  python-pylibravatar
BuildRequires:  python-pydns


## Not needed for testing only when working with postgresql
#BuildRequires:  python-psycopg2

BuildRequires:  python-nose

%if %{?rhel}%{!?rhel:0} <= 6
Requires:  python-sqlalchemy0.7
Requires:  python-ordereddict
%else
Requires:  python-sqlalchemy
%endif

Requires:  python-flask
Requires:  python-wtforms
Requires:  python-flask-wtf
Requires:  python-flask-mako
Requires:  python-requests
Requires:  PyYAML
Requires:  python-alembic

Requires:  python-kitchen
Requires:  python-fedora
Requires:  python-fedora-flask
Requires:  python-openid
Requires:  python-openid-cla
Requires:  python-openid-teams

Requires:  python-tw2-core
Requires:  python-tw2-forms
Requires:  python-tw2-jquery
Requires:  python-tw2-jqplugins-ui
Requires:  python-tw2-jqplugins-gritter

Requires:  fedmsg
Requires:  python-pkgwat-api
Requires:  python-docutils
Requires:  python-pylibravatar
Requires:  python-pydns

Requires:  python-psycopg2

# Sad panda.  Oldschool mako doesn't handle encoding issues well.
%if %{?rhel}%{!?rhel:0} <= 6
BuildRequires:  python-mako0.4
Requires:       python-mako0.4
%endif


%description
A web application for adding and ranking tags for Fedora packages.

%prep
%setup -q

%if %{?rhel}%{!?rhel:0} <= 6
# Make sure that epel/rhel picks up the correct version of webob
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"Mako>=0.4.2\", \"sqlalchemy>=0.7\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py
%endif

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}
%{__python} setup.py archive_tw2_resources -f -o %{buildroot}%{_datadir}/%{modname}/toscawidgets -d fedora-tagger

# This may not be necessary anymore
rm -fr %{buildroot}%{python_sitelib}/migration

%{__mkdir_p} %{buildroot}%{_datadir}/%{modname}/apache
%{__install} apache/%{modname}.wsgi %{buildroot}%{_datadir}/%{modname}/%{modname}.wsgi

%{__mkdir_p} %{buildroot}%{_datadir}/%{modname}/alembic
%{__install} alembic.ini %{buildroot}%{_datadir}/%{modname}/alembic.ini
cp -rf alembic/* %{buildroot}%{_datadir}/%{modname}/alembic

%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{modname}/
%{__install} apache/%{modname}.cfg %{buildroot}%{_sysconfdir}/%{modname}/%{modname}.cfg

%pre
%{_sbindir}/groupadd -r %{modname} &>/dev/null || :
%{_sbindir}/useradd  -r -s /sbin/nologin -d %{_datadir}/%{modname} -M \
              -c 'Fedora Tagger' -g %{modname} %{modname} &>/dev/null || :

%files
%doc README.rst
%{_bindir}/fedoratagger-update-db
%{_bindir}/fedoratagger-merge-tag
%{_bindir}/fedoratagger-remove-pkgs
%config %{_sysconfdir}/%{modname}/
%{_datadir}/%{modname}/
%config %{_datadir}/%{modname}/alembic.ini
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{eggname}-%{version}-py%{pyver}.egg-info/

%changelog
* Fri Jun 19 2015 Ralph Bean <rbean@redhat.com> - 2.3.1-1
- Lengthen metadata cache field.

* Fri Jun 19 2015 Ralph Bean <rbean@redhat.com> - 2.3.0-1
- Cache pkgwat data in the db for faster response times.

* Thu Dec 11 2014 Ralph Bean <rbean@redhat.com> - 2.2.1-1
- Fixes to rating json for fedmsg.crypto.
- PEP8 pass.
- Exclude el6-docs.
- Enhance add-tags dialog.

* Fri Nov 14 2014 Ralph Bean <rbean@redhat.com> - 2.2.0-1
- New release with modernizations for el7.

* Tue Jul 15 2014 Ralph Bean <rbean@redhat.com> - 2.1.5-1
- Bugfixes to the duplciate tag handling scripts.

* Thu Jul 10 2014 Ralph Bean <rbean@redhat.com> - 2.1.4-1
- Removing duplicate tags.

* Wed May 21 2014 Ralph Bean <rbean@redhat.com> - 2.1.3-1
- Various enhancements.

* Tue Feb 04 2014 Ralph Bean <rbean@redhat.com> - 2.1.2-1
- A /dump api fix for gnome-software
- Hash the IPs of anonymous users.
- New dep on python-ordereddict.

* Thu Jan 30 2014 Ralph Bean <rbean@redhat.com> - 2.1.1-1
- Make the usage api more explicit for gnome-software.

* Thu Jan 30 2014 Ralph Bean <rbean@redhat.com> - 2.1.0-1
- Add more granular stats for users (@yograterol)
- Add a Usage table to count how many users declare they are using a package.
- Add import of gnome-software meta-applications.
- Return more information in the ratings dump api endpoint.
- Add alembic upgrade scripts.
- New deps on requests, alembic, and pyyaml.

* Fri Nov 15 2013 Ralph Bean <rbean@redhat.com> - 2.0.8-1
- Fix search bar -- js locking error.

* Fri Nov 15 2013 Ralph Bean <rbean@redhat.com> - 2.0.7-1
- Fix search bar on the main page (form and function).

* Tue Oct 22 2013 Ralph Bean <rbean@redhat.com> - 2.0.6-1
- Dynamically update the title.
- No longer pull tags from the old pkgdb in the cronjov.
- Add a search bar to the main page.
- Expand the API for gnome-software.

* Thu May 16 2013 Ralph Bean <rbean@redhat.com> - 2.0.5-2
- Always force new tags to be lowercased.
- Remove some console.log js statements.

* Wed May 15 2013 Ralph Bean <rbean@redhat.com> - 2.0.5-1
- Fix https://github.com/fedora-infra/fedora-tagger/issues/90
- Fix https://github.com/fedora-infra/fedora-tagger/issues/89
- Fix https://github.com/fedora-infra/fedora-tagger/issues/84
- Fix https://github.com/fedora-infra/fedora-tagger/issues/87
- Fix https://github.com/fedora-infra/fedora-tagger/issues/88

* Fri May 10 2013 Ralph Bean <rbean@redhat.com> - 2.0.4-1
- Fix unicode issues in the sqlitebuildtags export API.

* Thu May 09 2013 Ralph Bean <rbean@redhat.com> - 2.0.3-1
- Fix openid login redirect.
- Fix score UI updating dynamically.
- Fix broken links in the more details dialog.
- Fix to caching users' rank.
- Add sqlitebuildtags export URL for bodhi.

* Fri Apr 26 2013 Ralph Bean <rbean@redhat.com> - 2.0.2-1
- Add compat URL for fedora-packages cronjob.
- Bugfix - rank changes weren't saved back to the DB.

* Wed Apr 24 2013 Ralph Bean <rbean@redhat.com> - 2.0.1-1
- Incorporated some lessons learned in staging.

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
