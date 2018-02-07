%global version_libphutil 2018.5
%global commit_libphutil fb082fb35626707d8620d5e486a03dbbd2c33019
%global shortcommit_libphutil %(c=%{commit_libphutil}; echo ${c:0:7})

%global version_arcanist 2018.3
%global commit_arcanist 886f6e6360ac6069ca8b8af12f69523deee6feda
%global shortcommit_arcanist %(c=%{commit_arcanist}; echo ${c:0:7})

%global version_phabricator 2018.5
%global commit_phabricator 4c14dd1e8925677f407b5ef4f1bd268a7d460daf
%global shortcommit_phabricator %(c=%{commit_phabricator}; echo ${c:0:7})

%global version_selinux 0.1.0

%global prefix /opt/phab
%global prefix_var %{_localstatedir}%{prefix}
%global prefix_log %{_localstatedir}/log/phab
%global prefix_run %{prefix_var}

%global selinux_variants targeted

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

Name:           phab
Version:        %{version_phabricator}
Release:        0.3.alpha8%{?dist}
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
Source11:       phabricator_storage_upgrade_handler
Source12:       phabricator-ssh-auth-wrapper
Source13:       phabricator-ssh-exec-wrapper
Source14:       phabricator.te
Source15:       phabricator.fc

Requires:       phab-arcanist = %{version_arcanist}
Requires:       phab-libphutil = %{version_libphutil}
Requires:       phab-phabricator = %{version_phabricator}
Requires:       phab-selinux >= %{version_selinux}
%{?systemd_requires}

BuildRequires:  systemd
BuildRequires:  checkpolicy, selinux-policy-devel

%description
Phabricator is an open source collection of web applications which help
software companies build better software.

This is the just the code withouth any required dependencies.

%package selinux
Summary:        Phabricator selinux policy
Version:        %{version_selinux}
Requires:       selinux-policy >= %{_selinux_policy_version}
Requires:       /usr/sbin/semodule, /sbin/restorecon, /sbin/fixfiles
AutoReq:        no

%description selinux
SELinux policy for phab-* packages

%package phabricator
Summary:        Phabricator core
Version:        %{version_phabricator}
Requires:       php-cli
Requires:       shadow-utils
Requires:       phab-libphutil = %{version_libphutil}
AutoReq:        no

%description phabricator
Phabricator is an open source collection of web applications which help
software companies build better software.

%package arcanist
Summary:        command-line intselinuxerface to Phabricator
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

test -d SELinux || mkdir SELinux
cp -p %{SOURCE14} %{SOURCE15} SELinux

%build
cd SELinux
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv phabricator.pp phabricator.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -

%install
DEST=${RPM_BUILD_ROOT}%{prefix}
mkdir -p ${DEST}

cp -r libphutil-%{commit_libphutil} ${DEST}/libphutil
cp -r arcanist-%{commit_arcanist} ${DEST}/arcanist
cp -r phabricator-%{commit_phabricator} ${DEST}/phabricator

install %{SOURCE11} ${DEST}/phabricator/bin/phabricator_storage_upgrade_handler
install %{SOURCE12} ${DEST}/phabricator/bin/ssh-auth-wrapper
install %{SOURCE13} ${DEST}/phabricator/bin/ssh-exec-wrapper

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

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
cp %{SOURCE10} \
  ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/phab-phabricator

for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 SELinux/phabricator.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/phabricator.pp
  rm -f SELinux/phabricator.pp.${selinuxvariant}
done

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

%post
%systemd_post phabricator.service phabricator_storage_upgrade@.service phabricator_storage_dump@.service phabricator_storage_dump@.timer

%post selinux
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s ${selinuxvariant} -i \
    %{_datadir}/selinux/${selinuxvariant}/phabricator.pp &> /dev/null || :
done
/sbin/fixfiles -R phab-phabricator restore || :
/sbin/restorecon -Ri %{prefix_var} %{prefix_run} %{prefix_log} || :


%post phabricator
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

%preun
%systemd_preun phabricator.service phabricator_storage_upgrade@.service phabricator_storage_dump@.service phabricator_storage_dump@.timer

%postun
%systemd_postun phabricator_storage_upgrade@.service phabricator_storage_dump@.service phabricator_storage_dump@.timer

%triggerpostun -- phabricator

systemctl daemon-reload >/dev/null 2>&1 || :

if [ $1 -ge 1 ]; then
  # Package upgrade, not uninstall
  %{prefix}/phabricator/bin/phabricator_storage_upgrade_handler
fi

%postun selinux
if [ $1 -eq 0 ] ; then
  for selinuxvariant in %{selinux_variants}
  do
    /usr/sbin/semodule -s ${selinuxvariant} -r phabricator &> /dev/null || :
  done
  /sbin/fixfiles -R phab-phabricator restore || :
  /sbin/restorecon -Ri %{prefix_var} %{prefix_run} %{prefix_log}  &> /dev/null || :
fi

%files
# ------------------------------------------------------------------
# Files
# ------------------------------------------------------------------
%{_unitdir}/phabricator*

%files selinux
%{_datadir}/selinux/*/phabricator.pp
%doc SELinux/*

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

%files arcanist
%{prefix}/arcanist

%files libphutil
%{prefix}/libphutil

%changelog
* Wed Feb 07 2018 Thomas Mueller <thomas@chaschperli.ch> - 2018.5-0.3.alpha8
- Update to 2018.5 Release - see
  https://secure.phabricator.com/w/changelog/2018.05/

* Thu Feb 01 2018 Thomas Mueller <thomas@chaschperli.ch> - 2018.4-0.2.alpha8
- Added initial SELinux bits

* Sun Jan 28 2018 Thomas Mueller <thomas@chaschperli.ch> - 2018.4-0.1.alpha8
- Phabricator 2018.4 - upstream changelog:
  https://secure.phabricator.com/w/changelog/2018.04/

