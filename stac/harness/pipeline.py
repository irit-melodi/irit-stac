# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Support for parser pipeline
"""

from collections import namedtuple
from os import path as fp
import os
import re
import sys

from attelo.harness import (RuntimeConfig)
from attelo.harness.interface import (HarnessException)
from attelo.harness.util import call, makedirs
from attelo.io import (Torpor, load_multipack)
import attelo.harness.parse as ath_parse

from .harness import (IritHarness)
from .local import (EVALUATIONS,
                    SNAPSHOTS,
                    TEST_EVALUATION_KEY,
                    TAGGER_JAR)
from .util import (concat_i)

# pylint: disable=too-few-public-methods


class StandaloneParser(IritHarness):
    """
    A variant of the test harness which can be used for
    standalone parsing
    """

    def __init__(self, soclog, tmp_dir):
        self.soclog = soclog
        self.tmp_dir = fp.abspath(tmp_dir)
        harness_dir = fp.dirname(fp.dirname(fp.abspath(__file__)))
        self.root_dir = fp.dirname(harness_dir)
        self.snap_dir = fp.abspath(latest_snap())
        super(StandaloneParser, self).__init__()
        super(StandaloneParser, self).load(RuntimeConfig.empty(),
                                           self.snap_dir,
                                           self.snap_dir)

    @property
    def test_evaluation(self):
        # overriden to skip TEST_CORPUS check
        if TEST_EVALUATION_KEY is None:
            return None
        test_confs = [x for x in self.evaluations
                      if x.key == TEST_EVALUATION_KEY]
        if test_confs:
            return test_confs[0]
        else:
            return None


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


def latest_snap():
    """
    Directory for last run (usually a symlink)
    """
    return fp.join(SNAPSHOTS, "latest")


def dact_features_path(hconf):
    """Path where dialogue act features are stored"""
    return fp.join(hconf.eval_dir, "%s.dialogue-acts.sparse" % hconf.dataset)


def dact_model_path(hconf, rconf):
    """Path where dialogue act model is stored"""
    parent_dir = hconf.combined_dir_path()
    template = '{dataset}.{learner}.{task}.{ext}'
    bname = template.format(dataset=hconf.dataset,
                            learner=rconf.key,
                            task='dialogue-acts',
                            ext='model')
    return fp.join(parent_dir, bname)


def stub_name(lconf_or_soclog):
    "return a short filename component from a soclog path"
    soclog = lconf_or_soclog.soclog\
        if isinstance(lconf_or_soclog, StandaloneParser) else lconf_or_soclog
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
    cache = lconf.model_paths(econf.learner,
                              None)
    parser = econf.parser.payload
    parser.fit([], [], cache)  # we assume everything is cached
    return ath_parse.jobs(mpack, parser, output_path)


def decode(lconf, evaluations):
    "Decode the input using all the model/learner combos we know"

    fpath = minicorpus_path(lconf) + '.relations.sparse'
    vocab_path = lconf.mpack_paths(test_data=False)[3]
    mpack = load_multipack(fpath + '.edu_input',
                           fpath + '.pairings',
                           fpath,
                           vocab_path)
    decoder_jobs = concat_i(_get_decoding_jobs(mpack, lconf, econf)
                            for econf in evaluations)
    lconf.parallel(decoder_jobs)
    for econf in evaluations:
        output_path = attelo_result_path(lconf, econf)
        ath_parse.concatenate_outputs(mpack, output_path)


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def link_files(src_dir, tgt_dir):
    """
    Hard-link all files from the source directory into the
    target directory (nb: files only; directories ignored)
    This does not cost space and it makes future
    archiving a bit more straightforward
    """
    for fname in os.listdir(src_dir):
        data_file = fp.join(src_dir, fname)
        eval_file = fp.join(tgt_dir, fname)
        if os.path.isfile(data_file):
            os.link(data_file, eval_file)


def check_3rd_party():
    """
    Die if our third party deps are missing
    """
    if not fp.isfile(TAGGER_JAR):
        sys.exit("""Need %s
See http://www.ark.cs.cmu.edu/TweetNLP""" % TAGGER_JAR)
