
# phabricator-rpm

![copr build status](https://copr.fedorainfracloud.org/coprs/vinzentm/phabricator/package/phabricator/status_image/last_build.png)

Phabricator, libphutil and arcanist RPM's for Fedora, CentOS and RHEL.

## Quick start

On Fedora with the copr Repo:

```
dnf copr enable vinzentm/phabricator 
dnf install phabricator-standalone-server
```

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
