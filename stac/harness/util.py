# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)


"""
Miscellaneous utility functions
"""

import os
import sys

from attelo.harness.util import timestamp

from .local import LOCAL_TMP, SNAPSHOTS


def current_tmp():
    """
    Directory for the current run
    """
    return os.path.join(LOCAL_TMP, timestamp())


def latest_tmp():
    """
    Directory for last run (usually a symlink)
    """
    return os.path.join(LOCAL_TMP, "latest")


def latest_snap():
    """
    Directory for last run (usually a symlink)
    """
    return os.path.join(SNAPSHOTS, "latest")


def link_files(src_dir, tgt_dir):
    """
    Hard-link all files from the source directory into the
    target directory (nb: files only; directories ignored)
    This does not cost space and it makes future
    archiving a bit more straightforward
    """
    for fname in os.listdir(src_dir):
        data_file = os.path.join(src_dir, fname)
        eval_file = os.path.join(tgt_dir, fname)
        if os.path.isfile(data_file):
            os.link(data_file, eval_file)


def exit_ungathered():
    """
    You don't seem to have run the gather command
    """
    sys.exit("""No data to run experiments on.
Please run `irit-rst-dt gather`""")
