
# phabricator-rpm

![copr build status](https://copr.fedorainfracloud.org/coprs/vinzentm/phabricator/package/phabricator/status_image/last_build.png)

Phabricator, libphutil and arcanist RPM's for Fedora, CentOS and RHEL.

## Limitations

* Currently does not work with SELinux enforcing mode when
  using hosted repositories with Diffusion
* phabricator-standalone-server is not finished. it should also
  configure a git user configured for Phabricator authorized keys
  (https://github.com/phacility/phabricator/tree/master/resources/sshd)
  (or provide a utility to enable the config)
* No `storage upgrade` is called in post-upgrade script right now.
  I might add it for phabricator-standalone-server when mysql credentials
  are configured.

## Quick start

On Fedora with the copr Repo:

```
dnf copr enable vinzentm/phabricator 
dnf install phabricator-standalone-server
```

You'll find the phabricator things here: `/opt/phacility/{libphutil,arcanist,phabricator}`

## Build

Prereqs:

```
dnf install rpmdevltools rpm-build git
```

Source RPM:

```
bin/build-srpm
```

Binary RPM:

```
bin/build-rpm
```
