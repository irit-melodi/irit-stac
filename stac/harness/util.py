# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)


"""
Miscellaneous utility functions
"""

from collections import (Counter)
import hashlib
import itertools
import os
import sys

from attelo.harness.util import timestamp
from joblib import Parallel

from .local import (LOCAL_TMP, SNAPSHOTS,
                    EVALUATIONS)


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


def concat_i(itr):
    """
    Walk an iterable of iterables as a single one
    """
    return itertools.chain.from_iterable(itr)


def md5sum_file(path, blocksize=65536):
    """
    Read a file and return its md5 sum
    """
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()


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

# ---------------------------------------------------------------------
# config
# ---------------------------------------------------------------------


def exit_ungathered():
    """
    You don't seem to have run the gather command
    """
    sys.exit("""No data to run experiments on.
Please run `irit-stac gather`""")


def sanity_check_config():
    """
    Die if there's anything odd about the config
    """
    conf_counts = Counter(econf.key for econf in EVALUATIONS)
    bad_confs = [k for k, v in conf_counts.items() if v > 1]
    if bad_confs:
        oops = ("Sorry, there's an error in your configuration.\n"
                "I don't dare to start evaluation until you fix it.\n"
                "ERROR! -----------------vvvv---------------------\n"
                "The following configurations more than once:{}\n"
                "ERROR! -----------------^^^^^--------------------"
                "").format("\n".join(bad_confs))
        sys.exit(oops)

# ---------------------------------------------------------------------
# parallel
# ---------------------------------------------------------------------


def parallel(lconf, n_jobs=None, verbose=None):
    """
    Run some delayed jobs in parallel (or sequentially
    depending on our settings)

    This exists wholly to allow us to bypass joblib in
    places we suspect that n_jobs=1 isn't quite the same
    as just straight shot sequential.
    """
    n_jobs = n_jobs or lconf.n_jobs
    verbose = verbose or 5

    def sequential(jobs):
        """
        run jobs in truly sequential fashion without any of
        this parallel nonsense
        """
        # pylint: disable=star-args
        for func, args, kwargs in jobs:
            func(*args, **kwargs)
        # pylint: enable=star-args

    if n_jobs == 0:
        return sequential
    else:
        return Parallel(n_jobs=n_jobs, verbose=verbose)
