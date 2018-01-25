%global version_libphutil 2018.3
%global commit_libphutil 53f01ac1ae7815bc55e8c1532fe3de12287c8e24
%global shortcommit_libphutil %(c=%{commit_libphutil}; echo ${c:0:7})

%global version_arcanist 2018.3
%global commit_arcanist 886f6e6360ac6069ca8b8af12f69523deee6feda
%global shortcommit_arcanist %(c=%{commit_arcanist}; echo ${c:0:7})

%global version_phabricator 2018.3
%global commit_phabricator 73439dad9d491b05ecc633f47c9f4b59a7346f6c
%global shortcommit_phabricator %(c=%{commit_phabricator}; echo ${c:0:7})

%global prefix /opt/phab
%global prefix_var %{_localstatedir}%{prefix}
%global prefix_log %{_localstatedir}/log/phab
%global prefix_run %{prefix_var}

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

Name:           phab
Version:        %{version_phabricator}
Release:        0.0.alpha7%{?dist}
Summary:        Phabricator meta-package
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
Source7:        phabricator_storage_upgrade.unit
Source8:        phabricator_storage_dump.unit
Source9:        phabricator_storage_dump.timer
Source10:       phabricator.logrotate

Requires:       phab-arcanist = %{version_arcanist}
Requires:       phab-libphutil = %{version_libphutil}
Requires:       phab-phabricator = %{version_phabricator}


%description
Phabricator is an open source collection of web applications which help
software companies build better software.

This is the just the code withouth any required dependencies.

%package standalone-server
Summary:        Run phabricator all-in-one on a single server
Version:        %{version_phabricator}
Requires:       %{mysqld_requires}
Requires:       %{php_requires}
Requires:       python-pygments
Requires:       phab-libphutil = %{version_libphutil}
Requires:       phab-arcanist = %{version_arcanist}
Requires:       phab-phabricator = %{version_phabricator}
AutoReq:        no

%description standalone-server
Install phabricator to run all-in-one on one server.

%package phabricator
Summary:        Phabricator core
Version:        %{version_phabricator}
# Init systemd
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       chkconfig initscripts
%else
BuildRequires:  systemd
%{?systemd_requires}
%endif
Requires:       php-cli
Requires:       shadow-utils
Requires:       phab-libphutil = %{version_libphutil}
Requires:       phab-arcanist = %{version_arcanist}
AutoReq:        no

%description phabricator
Phabricator is an open source collection of web applications which help
software companies build better software.

%package arcanist
Summary:        command-line interface to Phabricator
Version:        %{version_arcanist}
Requires:       %{php_requires_arcanist}
Requires:       phab-libphutil = %{version_libphutil}
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
DEST=${RPM_BUILD_ROOT}%{prefix}
mkdir -p ${DEST}

cp -r libphutil-%{commit_libphutil} ${DEST}/libphutil
cp -r arcanist-%{commit_arcanist} ${DEST}/arcanist
cp -r phabricator-%{commit_phabricator} ${DEST}/phabricator

DEST_VAR=${RPM_BUILD_ROOT}%{prefix_var}
mkdir -p ${DEST_VAR}/files  ${DEST_VAR}/diffusion ${DEST_VAR}/storage_dump

# phabricator calls git and svn which in turn call ssh 
# and ssh requires $HOME/.ssh
mkdir ${DEST_VAR}/.ssh
mkdir ${DEST_VAR}/.subversion


mkdir -p ${RPM_BUILD_ROOT}%{prefix_log}/phd

mkdir -p ${RPM_BUILD_ROOT}%{prefix_run}/phd

%if 0%{?rhel} && 0%{?rhel} <= 6
mkdir -p ${RPM_BUILD_ROOT}%{_initddir}
cp %{SOURCE3} \
  ${RPM_BUILD_ROOT}%{_initddir}/phabricator
%else
mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}
cp %{SOURCE6} \
  ${RPM_BUILD_ROOT}%{_unitdir}/phabricator.service
cp %{SOURCE7} \
  ${RPM_BUILD_ROOT}%{_unitdir}/phabricator_storage_upgrade@.service
cp %{SOURCE8} \
  ${RPM_BUILD_ROOT}%{_unitdir}/phabricator_storage_dump@.service
cp %{SOURCE9} \
  ${RPM_BUILD_ROOT}%{_unitdir}/phabricator_storage_dump@.timer
%endif


mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sudoers.d
cp %{SOURCE5} \
  ${RPM_BUILD_ROOT}%{_sysconfdir}/sudoers.d/phabricator

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
cp %{SOURCE10} \
  ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/phab-phabricator

%clean
rm -rf $RPM_BUILD_ROOT

# ------------------------------------------------------------------
# Scripts
# ------------------------------------------------------------------
%pre phabricator
getent group phabricator >/dev/null || groupadd -r phabricator
getent passwd phabricator >/dev/null || \
    useradd -r -g phabricator -d %{prefix_var} -s /sbin/nologin \
    -c "Daemon user for Phabricator" phabricator

%post phabricator
%if 0%{?rhel} && 0%{?rhel} <= 6
/sbin/chkconfig --add phabricator
%else
%systemd_post phabricator.service phabricator_storage_upgrade@.service phabricator_storage_dump@.service phabricator_storage_dump@.timer
%endif

CFG=%{prefix}/phabricator/bin/config
if ! [ -e %{prefix}/phabricator/conf/local/local.json ]; then
  $CFG set repository.default-local-path %{prefix_var}/diffusion
  $CFG set storage.local-disk.path %{prefix_var}/files
  $CFG set pygments.enabled true
  $CFG set phabricator.base-uri http://$(hostname -f)/
  $CFG set metamta.default-address phabricator@$(hostname -f)
  $CFG set metamta.domain $(hostname -f)
  $CFG set phd.user phabricator
  $CFG set phd.log-directory %{prefix_log}/phd
  $CFG set phd.pid-directory %{prefix_run}/phd
  $CFG set diffusion.allow-http-auth true
  $CFG set phabricator.csrf-key \
    $(dd if=/dev/urandom bs=128 count=1 2>/dev/null |  base64 | grep -Eo '[a-zA-Z0-9]' | head -30 | tr -d '\n')
  $CFG set phabricator.mail-key \
    $(dd if=/dev/urandom bs=128 count=1 2>/dev/null |  base64 | grep -Eo '[a-zA-Z0-9]' | head -30 | tr -d '\n')
fi

%preun phabricator
%if 0%{?rhel} && 0%{?rhel} <= 6
  echo "nothing to do here in preun"
%else
%systemd_preun phabricator.service phabricator_storage_upgrade@.service phabricator_storage_dump@.service phabricator_storage_dump@.timer
%endif

%postun phabricator
%if 0%{?rhel} && 0%{?rhel} <= 6
  echo "nothing to do here in preun"
%else
# @todo starting phabricator_storage_upgrade@.service will stop
#   phabricator.service. needs more sophisticated scripting to upgrade
#   the storage without phabricator running
%systemd_postun phabricator_storage_upgrade@.service phabricator_storage_dump@.service phabricator_storage_dump@.timer
%systemd_postun_with_restart phabricator.service
%endif

%post standalone-server
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
%systemd_preun phabricator.service
%endif

%files
# ------------------------------------------------------------------
# Files
# ------------------------------------------------------------------

%files phabricator
%defattr(-,root,root,-)
%{prefix}/phabricator
%config(noreplace) %{_sysconfdir}/logrotate.d/phab-phabricator
%dir %attr(0750, phabricator, phabricator) %{prefix_var}/.ssh
%dir %attr(0750, phabricator, phabricator) %{prefix_var}/.subversion
%dir %attr(0750, phabricator, phabricator) %{prefix_var}/storage_dump
%dir %attr(0750, phabricator, phabricator) %{prefix_var}/phd
%dir %attr(0750, phabricator, phabricator) %{prefix_log}/phd
%dir %attr(0750, phabricator, phabricator) %{prefix_run}/phd

%if 0%{?rhel} && 0%{?rhel} <= 6
%attr(0755,-,-) %{_initddir}/phabricator
%else
%{_unitdir}/phabricator.service
%{_unitdir}/phabricator_storage_upgrade@.service
%{_unitdir}/phabricator_storage_dump@.service
%{_unitdir}/phabricator_storage_dump@.timer
%endif


%files standalone-server
%attr(0440,-,-) %{_sysconfdir}/sudoers.d/phabricator
%dir %attr(2750, phabricator, phabricator) %{prefix_var}/diffusion
%dir %attr(0700, apache, apache) %{prefix_var}/files


%files arcanist
%{prefix}/arcanist

%files libphutil
%{prefix}/libphutil

%changelog
