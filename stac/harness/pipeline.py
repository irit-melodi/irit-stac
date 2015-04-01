# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Support for parser pipeline
"""

from collections import namedtuple
from os import path as fp
import re
import sys

from attelo.harness.util import call, makedirs
from attelo.io import (Torpor, load_multipack, load_model)
import attelo.harness.decode as ath_decode
from joblib import (Parallel)

from .local import (TAGGER_JAR, TRAINING_CORPUS)
from .path import (attelo_doc_model_paths,
                   vocab_path)
from .util import (concat_i, latest_snap)

# pylint: disable=too-few-public-methods


class PipelineConfig(object):
    """
    An object which behaves enough like LoopConfig for the
    purposes of the parsing pipeline that we can dig up the
    input files it needs to get by
    """

    def __init__(self, soclog, tmp_dir):
        self.soclog = soclog
        self.snap_dir = fp.abspath(latest_snap())
        self.eval_dir = self.snap_dir  # compatibility with LoopConfig
        self.scratch_dir = self.snap_dir  # compatibility with LoopConfig
        self.tmp_dir = fp.abspath(tmp_dir)
        self.dataset = fp.basename(TRAINING_CORPUS)
        harness_dir = fp.dirname(fp.dirname(fp.abspath(__file__)))
        self.root_dir = fp.dirname(harness_dir)

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
        abs_script = self.abspath(script)
        cmd = ["python", abs_script] + list(args)
        call(cmd, **kwargs)


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
        if isinstance(lconf_or_soclog, PipelineConfig) else lconf_or_soclog
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


def resource_np_path(lconf):
    """
    path to temporary minicorpus dir mimicking structure
    of actual corpus
    """
    return lconf.tmp('resource-nps.conll')


def parsed_bname(lconf, econf):
    """
    short name for virtual author consisting of dataset used to
    parse the file and the learner/decoder config
    """
    return ".".join([lconf.dataset, econf.key])


def result_path(lconf, econf):
    """
    Path to directory where we are saving results
    """
    parent = lconf.tmp("parsed")
    return fp.join(parent, parsed_bname(lconf, econf))


def attelo_result_path(lconf, econf):
    """
    Path to attelo graph file
    """
    return result_path(lconf, econf)


# ---------------------------------------------------------------------
# decoding
# ---------------------------------------------------------------------


def _get_decoding_jobs(mpack, lconf, econf):
    """
    Run the decoder on a single config and convert the output
    """
    makedirs(lconf.tmp("parsed"))
    output_path = attelo_result_path(lconf, econf)
    model_paths = attelo_doc_model_paths(lconf,
                                         econf.learner,
                                         None)
    models = model_paths.fmap(load_model)
    return ath_decode.jobs(mpack,
                           models,
                           econf.decoder.payload,
                           econf.settings.mode,
                           output_path)


def decode(lconf, evaluations):
    "Decode the input using all the model/learner combos we know"

    fpath = minicorpus_path(lconf) + '.relations.sparse'
    with open(vocab_path(lconf)) as lines:
        num_features = len(list(lines))
    mpack = load_multipack(fpath + '.edu_input',
                           fpath + '.pairings',
                           fpath,
                           n_features=num_features)
    decoder_jobs = concat_i(_get_decoding_jobs(mpack, lconf, econf)
                            for econf in evaluations)
    Parallel(n_jobs=-1)(decoder_jobs)
    for econf in evaluations:
        output_path = attelo_result_path(lconf, econf)
        ath_decode.concatenate_outputs(mpack, output_path)


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
