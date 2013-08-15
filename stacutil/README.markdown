Utility modules that several STAC scripts may have in common.
In case of duplication, the versions in this directory should
be considered canonical.

By rights, this should be a Python library of some sort, but
for now I would rather avoid introducing another install step
for them, so I'm using hardlinks in my local filesystems
instead (not symlinks as this would not work out too well with
Windows SVN).
