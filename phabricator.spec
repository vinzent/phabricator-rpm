%global version_libphutil 2017.48
%global commit_libphutil f3386051a959f218ce96ffbec5fe4010decb83f9
%global shortcommit_libphutil %(c=%{commit_libphutil}; echo ${c:0:7})

%global version_arcanist 2017.51
%global commit_arcanist 08674ca997b62b695f773c32f0c20e51128bc053
%global shortcommit_arcanist %(c=%{commit_arcanist}; echo ${c:0:7})

%global version_phabricator 2018.1
%global commit_phabricator f9d9125f93ac3c274085f2b037f1e609106ecba0
%global shortcommit_phabricator %(c=%{commit_phabricator}; echo ${c:0:7})

Name:           phabricator
Version:        %{version_phabricator}
Release:        1%{?dist}
Summary:        collection of web applications to help build software
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

BuildRequires:  git
Requires:       shadow-utils
Requires:       git php php-cli php-process php-devel php-gd python-pygments
Requires:       php-pecl-apc php-pecl-json php-mbstring sudo
Requires:       phabricator-arcanist = %{version_arcanist}
Requires:       phabricator-libphutil = %{version_libphutil}

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       chkconfig initscripts
%else
BuildRequires:  systemd
%{?systemd_requires}
%endif

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       php-mysql
%elseif 0%{?rhel} && 0%{?rhel} == 7
Requires:       php-mysql
%else
Requires:       php-mysqlnd
%endif

%description
Phabricator is an open source collection of web applications which help
software companies build better software.

%package standalone-server
Summary:        Run phabricator all-in-one on a single server
Version:        %{version_phabricator}
Requires:       phabricator-libphutil = %{version_libphutil}
Requires:       phabricator-arcanist = %{version_arcanist}
Requires:       phabricator = %{version_phabricator}
AutoReq:        no

%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       mysql-server
%elseif 0%{?rhel} && 0%{?rhel} == 7
Requires:       mariadb-server
%else
Requires:       mariadb-server
%endif

%description standalone-server
Install phabricator to run all-in-one on one server.

%package arcanist
Summary:        command-line interface to Phabricator
Version:        %{version_arcanist}
Requires:       php-cli
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

%post
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


%preun
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

%if 0%{?rhel} && 0%{?rhel} <= 6
%attr(0755,-,-) %{_initddir}/phabricator
%else
%{_unitdir}/phabricator.service
%endif

%attr(0440,-,-) /etc/sudoers.d/phabricator
%dir %attr(0750, phabricator, phabricator)/var/opt/phabricator
%dir %attr(2750, phabricator, phabricator) /var/opt/phabricator/repo
%dir %attr(0700, apache, apache) /var/opt/phabricator/files
%dir %attr(0750, phabricator, phabricator)/var/log/phabricator

%files arcanist
/opt/phacility/arcanist

%files libphutil
/opt/phacility/libphutil

%changelog
