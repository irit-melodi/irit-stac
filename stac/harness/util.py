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
from joblib import (Parallel)

from .local import (HARNESS_NAME,
                    LOCAL_TMP,
                    EVALUATIONS,
                    TEST_CORPUS,
                    TEST_EVALUATION_KEY)


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

# ---------------------------------------------------------------------
# config
# ---------------------------------------------------------------------


def exit_ungathered():
    """
    You don't seem to have run the gather command
    """
    sys.exit("""No data to run experiments on.
Please run `{} gather`""".format(HARNESS_NAME))


def test_evaluation():
    """
    Return the test evaluation or None if unset
    """
    if TEST_CORPUS is None:
        return None
    elif TEST_EVALUATION_KEY is None:
        return None
    test_confs = [x for x in EVALUATIONS if x.key == TEST_EVALUATION_KEY]
    if test_confs:
        return test_confs[0]
    else:
        return None


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
    if TEST_EVALUATION_KEY is not None and test_evaluation() is None:
        oops = ("Sorry, there's an error in your configuration.\n"
                "I don't dare to start evaluation until you fix it.\n"
                "ERROR! -----------------vvvv---------------------\n"
                "The test configuration '{}' does not appear in your "
                "configurations\n"
                "ERROR! -----------------^^^^^--------------------"
                "").format(TEST_EVALUATION_KEY)
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
        for func, args, kwargs in jobs:
            func(*args, **kwargs)

    if n_jobs == 0:
        return sequential
    else:
        return Parallel(n_jobs=n_jobs, verbose=verbose)
