# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Support for parser pipeline
"""

from collections import namedtuple
import re
import sys

from attelo.harness.util import call, makedirs
from attelo.io import Torpor

from os import path as fp

from .local import TAGGER_JAR


# pylint: disable=pointless-string-statement
class LoopConfig(object):
    "that which is common to outerish loops"

    def __init__(self, soclog, snap_dir, tmp_dir):
        self.soclog = soclog
        self.snap_dir = fp.abspath(snap_dir)
        self.tmp_dir = fp.abspath(tmp_dir)
        self.dataset = "all"
        harness_dir = fp.dirname(fp.dirname(fp.abspath(__file__)))
        self.root_dir = fp.dirname(fp.dirname(harness_dir))

    def tmp(self, relpath):
        """
        Subpath within our tmp directory
        """
        return fp.join(self.tmp_dir, relpath)

    def abspath(self, relpath):
        """
        Absolute path given one which is relative to the STAC root
        dir
        """
        return fp.join(self.root_dir, relpath)

    def pyt(self, script, *args, **kwargs):
        "call python on one of our scripts"
        abs_script = self.abspath(fp.join("code", script))
        cmd = ["python", abs_script] + list(args)
        call(cmd, **kwargs)
# pylint: enable=pointless-string-statement


class Stage(namedtuple('Stage',
                       ['logname',
                        'function',
                        'description'])):
    """
    Individual pipeline stage

    :type function: `(LoopConfig, FilePath) -> IO ()`
    """
    pass


def stac_msg(msg, **kwargs):
    "stac announcement context manager"
    return Torpor("[stac] " + msg, **kwargs)


def run_pipeline(lconf, stages):
    """
    Run each of the stages of the pipeline in succession. ::

        (LoopConfig, [Stage]) -> IO ()

    They don't feed into each other (yet); communication between stages is
    based on assumed side effects (ie. writing into files at conventional
    locations).
    """
    logdir = lconf.tmp("logs")
    makedirs(logdir)
    for stage in stages:
        msg = stage.description
        logpath = fp.join(logdir, stage.logname + ".txt")
        with stac_msg(msg or "", quiet=msg is None):
            with open(logpath, 'w') as log:
                stage.function(lconf, log)

# ---------------------------------------------------------------------
# pipeline paths
# ---------------------------------------------------------------------


def stub_name(lconf_or_soclog):
    "return a short filename component from a soclog path"
    soclog = lconf_or_soclog.soclog\
        if isinstance(lconf_or_soclog, LoopConfig) else lconf_or_soclog
    stub = fp.splitext(fp.basename(soclog))[0]
    stub = re.sub(r'-', '_', stub)
    return stub


def unseg_path(lconf):
    "path to unsegmented csv file (converted from glozz)"
    return lconf.tmp("unsegmented.csv")


def seg_path(lconf):
    "path to segmented csv file"
    return lconf.tmp("segmented.csv")


def minicorpus_path(lconf, result=False):
    """
    path to temporary minicorpus dir mimicking structure
    of actual corpus
    """
    return lconf.tmp('resultcorpus' if result else 'minicorpus')


def minicorpus_doc_path(lconf, result=False):
    """
    path to subdir of the minicorpus for the file itself
    """
    return fp.join(minicorpus_path(lconf, result),
                   stub_name(lconf))


def minicorpus_stage_path(lconf, stage, result=False):
    """
    path to subdir of the minicorpus for the file itself
    """
    return fp.join(minicorpus_doc_path(lconf, result),
                   stage)


def unannotated_dir_path(lconf, result=False):
    """
    path to the unannotated directory
    """
    return fp.join(minicorpus_doc_path(lconf, result),
                   "unannotated")


def unannotated_stub_path(lconf):
    """
    path to unannotated files (minus extension)
    """
    return fp.join(unannotated_dir_path(lconf),
                   stub_name(lconf) + "_0")


def features_path(lconf):
    """
    features extracted from the input soclog
    """
    return lconf.tmp("extracted-features.csv")


def parsed_bname(lconf, econf):
    """
    short name for virtual author consisting of dataset used to
    parse the file and the learner/decoder config
    """
    return ".".join([lconf.dataset, econf.name])

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def check_3rd_party():
    """
    Die if our third party deps are missing
    """
    if not fp.isfile(TAGGER_JAR):
        sys.exit("""Need %s
See http://www.ark.cs.cmu.edu/TweetNLP""" % TAGGER_JAR)
