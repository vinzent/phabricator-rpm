%global version_libphutil 2017.48
%global commit_libphutil f3386051a959f218ce96ffbec5fe4010decb83f9
%global shortcommit_libphutil %(c=%{commit_libphutil}; echo ${c:0:7})

%global version_arcanist 2017.51
%global commit_arcanist 08674ca997b62b695f773c32f0c20e51128bc053
%global shortcommit_arcanist %(c=%{commit_arcanist}; echo ${c:0:7})

%global version_phabricator 2018.2
%global commit_phabricator 53b4882b8073439f00502587e9979f93a56e232d
%global shortcommit_phabricator %(c=%{commit_phabricator}; echo ${c:0:7})

%if 0%{?rhel} && 0%{?rhel} <= 6
# EL6 requires
%global php_requires php php-cli php-process php-gd php-pecl-apc php-pecl-json php-mbstring php-mysql
%global php_requires_arcanist php-cli
%global mysqld_requires mysql-server
%else
%if 0%{?rhel} && 0%{?rhel} == 7
# EL7 requires
%global php_requires rh-php71-php rh-php71-php-cli rh-php71-php-process rh-php71-php-gd rh-php71-php-pecl-apcu rh-php71-php-json rh-php71-php-mbstring rh-php71-php-mysqlnd
%global php_requires_arcanist php-cli
%global mysqld_requires mariadb-server
%else
# Fedora >= 26 requires
%global php_requires php php-cli php-process php-gd php-pecl-apcu php-json php-mbstring php-mysqlnd
%global php_requires_arcanist php-cli
%global mysqld_requires mariadb-server
%endif
%endif

Name:           phabricator
Version:        %{version_phabricator}
Release:        2.0.alpha1%{?dist}
Summary:        Phabricator core - just the tool without dependencies.
BuildArch:      noarch
AutoReq:        no

Group:          Web
License:        Apache 2.0
URL:            http://www.phabricator.org
Source0:        https://github.com/phacility/libphutil/archive/%{commit_libphutil}/libphutil-%{shortcommit_libphutil}.tar.gz 
Source1:        https://github.com/phacility/arcanist/archive/%{commit_arcanist}/arcanist-%{shortcommit_arcanist}.tar.gz 
Source2:        https://github.com/phacility/phabricator/archive/%{commit_phabricator}/phabricator-%{shortcommit_phabricator}.tar.gz 
Source3:        phabricator.init
Source4:        phabricator.httpd.conf
Source5:        phabricator.sudoers
Source6:        phabricator.unit

Requires:       phabricator-arcanist = %{version_arcanist}
Requires:       phabricator-libphutil = %{version_libphutil}


%description
Phabricator is an open source collection of web applications which help
software companies build better software.

This is the just the code withouth any required dependencies.

%package standalone-server
Summary:        Run phabricator all-in-one on a single server
Version:        %{version_phabricator}
Requires:       %{mysqld_requires}
Requires:       %{php_requires}
Requires:       shadow-utils
Requires:       python-pygments
# Init systemd
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       chkconfig initscripts
%else
BuildRequires:  systemd
%{?systemd_requires}
%endif
Requires:       phabricator-libphutil = %{version_libphutil}
Requires:       phabricator-arcanist = %{version_arcanist}
Requires:       phabricator = %{version_phabricator}
AutoReq:        no

%description standalone-server
Install phabricator to run all-in-one on one server.

%package arcanist
Summary:        command-line interface to Phabricator
Version:        %{version_arcanist}
Requires:       %{php_requires_arcanist}
Requires:       phabricator-libphutil = %{version_libphutil}
AutoReq:        no

%description arcanist
Arcanists provides command-line access to many Phabricator tools (like
Differential, Files, and Paste), integrates with static analysis ("lint") and
unit tests, and manages common workflows like getting changes into Differential
for review.

%package libphutil
Summary:        a collection of utility classes and functions for PHP
Version:        %{version_libphutil}
AutoReq:        no

%description libphutil
libphutil is a collection of utility classes and functions for PHP. Some
features of the library include:
- libhutil library system
- futures
- filesystem
- xsprintf
- AAST/PHPAST
- Remarkup
- Daemons
- Utilities

%prep
tar -xzf %{SOURCE0}
tar -xzf %{SOURCE1}
tar -xzf %{SOURCE2}

%build
echo Nothing to build.

%install
DEST=${RPM_BUILD_ROOT}/opt/phacility
mkdir -p ${DEST}
for dir in libphutil arcanist phabricator; do
  cp -r ${dir}-* ${RPM_BUILD_ROOT}/opt/phacility/$dir
done

mkdir -p ${RPM_BUILD_ROOT}/var/opt/phabricator
mkdir ${RPM_BUILD_ROOT}/var/opt/phabricator/files
mkdir ${RPM_BUILD_ROOT}/var/opt/phabricator/repo

%if 0%{?rhel} && 0%{?rhel} <= 6
mkdir -p ${RPM_BUILD_ROOT}%{_initddir}
cp %{SOURCE3} \
  ${RPM_BUILD_ROOT}%{_initddir}/phabricator
%else
mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}
cp %{SOURCE6} \
  ${RPM_BUILD_ROOT}%{_unitdir}/phabricator.service
%endif

mkdir -p ${RPM_BUILD_ROOT}/var/log/phabricator

ln -sf /usr/libexec/git-core/git-http-backend \
  ${DEST}/phabricator/support/bin/git-http-backend

mkdir -p ${RPM_BUILD_ROOT}/etc/sudoers.d
cp %{SOURCE5} \
  ${RPM_BUILD_ROOT}/etc/sudoers.d/phabricator

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group phabricator >/dev/null || groupadd -r phabricator
getent passwd phabricator >/dev/null || \
    useradd -r -g phabricator -d /var/opt/phabricator -s /sbin/nologin \
    -c "Daemon user for Phabricator" phabricator

%post standalone-server
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add phabricator
%else
%systemd_user_post phabricator.service
%endif

CFG=/opt/phacility/phabricator/bin/config
if ! [ -e /opt/phacility/phabricator/conf/local/local.json ]; then
  $CFG set repository.default-local-path /var/opt/phabricator/repo
  $CFG set storage.local-disk.path /var/opt/phabricator/files
  $CFG set storage.upload-size-limit 10M
  $CFG set pygments.enabled true
  $CFG set phabricator.base-uri http://$(hostname -f)/
  $CFG set metamta.default-address phabricator@$(hostname -f)
  $CFG set metamta.domain $(hostname -f)
  $CFG set phd.user phabricator
  $CFG set phd.log-directory /var/log/phabricator
  $CFG set phd.pid-directory /var/run/phabricator
  $CFG set diffusion.allow-http-auth true
  $CFG set phabricator.csrf-key \
    $(dd if=/dev/urandom bs=128 count=1 2>/dev/null |  base64 | grep -Eo '[a-zA-Z0-9]' | head -30 | tr -d '\n')
  $CFG set phabricator.mail-key \
    $(dd if=/dev/urandom bs=128 count=1 2>/dev/null |  base64 | grep -Eo '[a-zA-Z0-9]' | head -30 | tr -d '\n')
fi

# Httpd needs access to the repo folder
if ! groupmems -g phabricator -l | grep -q apache; then
  groupmems -g phabricator -a apache
fi


%preun standalone-server
%if 0%{?rhel} && 0%{?rhel} <= 6
if [ $1 -eq 0 ] ; then
    /sbin/service phabricator stop >/dev/null 2>&1
    /sbin/chkconfig --del phabricator
fi
%else
%systemd_user_preun phabricator.service
%endif

%files
%defattr(-,root,root,-)
/opt/phacility/phabricator
%dir /var/opt/phabricator
%dir %attr(0750, phabricator, phabricator) /var/log/phabricator


%files standalone-server
%attr(0440,-,-) /etc/sudoers.d/phabricator
%if 0%{?rhel} && 0%{?rhel} <= 6
%attr(0755,-,-) %{_initddir}/phabricator
%else
%{_unitdir}/phabricator.service
%endif
%dir %attr(2750, phabricator, phabricator) /var/opt/phabricator/repo
%dir %attr(0700, apache, apache) /var/opt/phabricator/files


%files arcanist
/opt/phacility/arcanist

%files libphutil
/opt/phacility/libphutil

%changelog
