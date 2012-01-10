%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get _python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%define modname fedoratagger
%define eggname fedora_tagger

Name:           fedora-tagger
Version:        0.1
Release:        0.22%{?dist}
Summary:        A web application for adding and ranking tags for Fedora packages

License:        TODO
URL:            https://github.com/ralphbean/fedora-tagger
Source0:        %{name}-%{version}.tar.bz2
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
BuildRequires:  python-sqlalchemy
BuildRequires:  python-repoze-what
BuildRequires:  python-repoze-who-friendlyform
BuildRequires:  python-repoze-what-pylons
BuildRequires:  python-repoze-who
BuildRequires:  python-repoze-what-plugins-sql
BuildRequires:  python-kitchen
BuildRequires:  pycurl
BuildRequires:  python-tw2
BuildRequires:  python-tw2-forms
BuildRequires:  python-tw2-jqplugins-gritter
BuildRequires:  python-tw2-jquery-ui
BuildRequires:  python-docutils
BuildRequires:  python-bunch
BuildRequires:  python-fedora
BuildRequires:  python-fedora-turbogears2

Requires:       TurboGears2
Requires:       python-mako
Requires:       python-zope-sqlalchemy
Requires:       python-sqlalchemy
Requires:       python-repoze-what
Requires:       python-repoze-who-friendlyform
Requires:       python-repoze-what-pylons
Requires:       python-repoze-who
#Requires:       python-repoze-what-quickstart
Requires:       python-repoze-what-plugins-sql
Requires:       python-kitchen
Requires:       pycurl
Requires:       python-tw2
#Requires:       python-jit
#Requires:       python-tw2-jqplugins-gritter
Requires:       python-tw2-jquery-ui

%description
A web application for adding and ranking tags for Fedora packages.

%prep
%setup -q

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


%files
%doc README.rst
%{_datadir}/%{name}/
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{eggname}-%{version}-py%{pyver}.egg-info/

%changelog
* Mon Jan 09 2012 Luke Macken <lmacken@redhat.com> - 0.1-1
- Initial RPM package
