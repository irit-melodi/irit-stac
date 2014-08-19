# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)


"""
Miscellaneous utility functions
"""

import os
import sys
from os import path as fp

# pylint: disable=no-name-in-module
from sh import head, tail
# pylint: enable=no-name-in-module

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


def merge_csv(csv_files, output_csv):
    """
    Concatenate multiple csv files (assumed to have the same
    header)

    There should be at least one file to work with
    """
    if not csv_files:
        raise ValueError("need non-empty list of csv files")
    any_csv = csv_files[0]
    with open(output_csv, "w") as combined:
        head("-n", "1", any_csv, _out=combined)
        for csv_file in csv_files:
            tail("-n", "+2", csv_file, _out=combined)


# ---------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------


def snap_model_path(lconf, econf, mtype):
    "(snap directory) model for a given loop/eval config"

    lname = econf.learner.name
    return fp.join(lconf.snap_dir,
                   "%s.%s.%s.model" % (lconf.dataset, lname, mtype))


def snap_dialogue_act_model_path(lconf, raw=False):
    "(snap directory) Model for a given dataset"

    prefix = "" if raw else "%s." % lconf.dataset
    return fp.join(lconf.snap_dir,
                   prefix + "dialogue-acts.model")
