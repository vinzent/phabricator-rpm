
# phabricator-rpm

Phabricator, libphutil and arcanist RPM's for Fedora, CentOS and RHEL.

The package is based on the stable branches. Version is generated from
"Promote YYYY Week N" merge commit message. The third number
is the "commit count since last Promote".

## What is where?

* The application is here: /opt/phab/{libphutil,arcanist,phabricator}
* Phabricator local config: /opt/phab/phabricator/config/local/local.json
  (to be edited with /opt/phab/phabricator/bin/config)
* Default path for data is /var/opt/phab/\*

## Limitations

* Packages don't depend on PHP (exception: phab-arcanist on php-cli)
  There are so many possibilities it would not make sense to depend on a
  specific php version and create useless dependencies. 
* The systemd services provided by phab don't depend on the database service.
  It's up to you to add dependencies with `/etc/systemd/system/*.service.d/local.conf`
  dropins.
* No httpd config is provided - too many possibilities how it could be
  integrated.


## Quick start

On Fedora with the copr Repo:

```
dnf copr enable vinzentm/phabricator 
dnf install phab
```

You'll find the phabricator things here: `/opt/phab/{libphutil,arcanist,phabricator}`

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
