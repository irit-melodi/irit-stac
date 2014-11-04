# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
parse a soclog file
"""

from __future__ import print_function
from os import path as fp
import glob
import re
import os
import sys
import shutil
import tempfile

import sh


from attelo.io import Torpor
from attelo.harness.util import\
    makedirs, call, force_symlink

from ..local import\
    CORENLP_SERVER_DIR, CORENLP_ADDRESS,\
    TAGGER_JAR, LEX_DIR,\
    EVALUATIONS, ATTELO_CONFIG_FILE
from ..util import\
    exit_ungathered, latest_snap, latest_tmp,\
    snap_model_path, snap_dialogue_act_model_path,\
    merge_csv

NAME = 'parse'
_DEBUG = 0


#pylint: disable=pointless-string-statement
class LoopConfig(object):
    "that which is common to outerish loops"

    def __init__(self, soclog, snap_dir, tmp_dir):
        self.soclog = soclog
        self.snap_dir = fp.abspath(snap_dir)
        self.tmp_dir = fp.abspath(tmp_dir)
        self.dataset = "all"
        harness_dir = fp.dirname(fp.dirname(fp.abspath(__file__)))
        self.root_dir = fp.dirname(fp.dirname(fp.dirname(harness_dir)))

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
#pylint: enable=pointless-string-statement

# ---------------------------------------------------------------------
# helper paths
# ---------------------------------------------------------------------


def _stub_name(lconf_or_soclog):
    "return a short filename component from a soclog path"
    soclog = lconf_or_soclog.soclog\
        if isinstance(lconf_or_soclog, LoopConfig) else lconf_or_soclog
    stub = fp.splitext(fp.basename(soclog))[0]
    stub = re.sub(r'-', '_', stub)
    return stub


def _unseg_path(lconf):
    "path to unsegmented csv file (converted from glozz)"
    return lconf.tmp("unsegmented.csv")


def _seg_path(lconf):
    "path to segmented csv file"
    return lconf.tmp("segmented.csv")


def _minicorpus_path(lconf, result=False):
    """
    path to temporary minicorpus dir mimicking structure
    of actual corpus
    """
    return lconf.tmp('resultcorpus' if result else 'minicorpus')


def _minicorpus_doc_path(lconf, result=False):
    """
    path to subdir of the minicorpus for the file itself
    """
    return fp.join(_minicorpus_path(lconf, result),
                   _stub_name(lconf))


def _minicorpus_stage_path(lconf, stage, result=False):
    """
    path to subdir of the minicorpus for the file itself
    """
    return fp.join(_minicorpus_doc_path(lconf, result),
                   stage)


def _unannotated_dir_path(lconf, result=False):
    """
    path to the unannotated directory
    """
    return fp.join(_minicorpus_doc_path(lconf, result),
                   "unannotated")


def _unannotated_stub_path(lconf):
    """
    path to unannotated files (minus extension)
    """
    return fp.join(_unannotated_dir_path(lconf),
                   _stub_name(lconf) + "_0")


def _features_path(lconf):
    """
    features extracted from the input soclog
    """
    return lconf.tmp("extracted-features.csv")


def _parsed_bname(lconf, econf):
    """
    short name for virtual author consisting of dataset used to
    parse the file and the learner/decoder config
    """
    return ".".join([lconf.dataset, econf.name])


def _stac_msg(msg, **kwargs):
    "stac announcement context manager"
    return Torpor("[stac] " + msg, **kwargs)

# ---------------------------------------------------------------------
# pipeline stages
# ---------------------------------------------------------------------


def _soclog_to_csv(lconf, log):
    """
    extract annotations from a soclog file and
    convert to the csv format more familiar to the
    rest of the scripts
    """
    turns_path = lconf.tmp("turns")
    unseg_path = _unseg_path(lconf)
    with open(turns_path, "w") as turns_file:
        lconf.pyt("txt2csv/extract_turns.py", lconf.soclog,
                  stdout=turns_file)
    lconf.pyt("txt2csv/extract_annot.py", turns_path,
              stdout=log)
    os.rename(turns_path + "csv", unseg_path)
    os.unlink(turns_path)


def _segment_into_edus(lconf, log):
    """
    segment (csv -> csv)
    """
    lconf.pyt("segmentation/simple-segments",
              "--csv", _unseg_path(lconf),
              _seg_path(lconf),
              stderr=log)


def _segmented_to_glozz(lconf, log):
    """
    convert the segmented CSV into glozz format
    (because that's what some of our other tools
    expectd)

    Return a corpus directory
    """
    lconf.pyt("csv2glozz/csvtoglozz.py",
              "-f", _seg_path(lconf),
              stderr=log,
              cwd=lconf.tmp_dir)

    their_stub = lconf.tmp('segmented')
    unanno_stub = _unannotated_stub_path(lconf)
    makedirs(fp.dirname(unanno_stub))
    os.rename(their_stub + '.aa', unanno_stub + '.aa')
    os.rename(their_stub + '.ac', unanno_stub + '.ac')


def _postag(lconf, log):
    """
    Run part of speech tagger on input
    """
    corpus_dir = _minicorpus_path(lconf)
    lconf.pyt("run-3rd-party",
              "--ark-tweet-nlp", lconf.abspath(TAGGER_JAR),
              corpus_dir, corpus_dir,
              stderr=log)


def _sentence_parse(lconf, log):
    """
    Run sentence parser on input.
    """
    corpus_dir = _minicorpus_path(lconf)
    lconf.pyt("run-3rd-party",
              "--corenlp-server", lconf.abspath(CORENLP_SERVER_DIR),
              "--corenlp-address", CORENLP_ADDRESS,
              #"--corenlp", CORENLP_DIR,
              corpus_dir, corpus_dir,
              stderr=log)


def _dialogue_acts(lconf, log):
    """
    Using a previously predicted dialogue act model,
    guess dialogue acts for all the EDUs
    """
    corpus_dir = _minicorpus_path(lconf)
    model_path = snap_dialogue_act_model_path(lconf)
    lconf.pyt("parser/dialogue-acts", "annotate",
              "-C", lconf.abspath(ATTELO_CONFIG_FILE),
              corpus_dir,
              lconf.abspath(LEX_DIR),
              "--model", model_path,
              "--output", corpus_dir,
              stderr=log)


def _feature_extraction(lconf, log):
    """
    Extract features from our input glozz file
    """
    corpus_dir = _minicorpus_path(lconf)
    cmd = ["stac-learning", "extract",
           "--parsing", "--experimental",
           corpus_dir,
           lconf.abspath(LEX_DIR),
           lconf.tmp_dir]
    call(cmd, stderr=log)


def _decode_one(lconf, econf, log):
    """
    Run the decoder on a single config and convert the output
    """
    def parsed_subpath(parent):
        "subdirectory for parser output of some sort"
        return fp.join(parent, _parsed_bname(lconf, econf))

    tmp_parsed_dir = parsed_subpath(lconf.tmp("tmp-parsed"))
    makedirs(tmp_parsed_dir)
    cmd = ["attelo", "decode",
           "-C", lconf.abspath(ATTELO_CONFIG_FILE),
           "-A", snap_model_path(lconf, econf, "attach"),
           "-R", snap_model_path(lconf, econf, "relate"),
           "-d", econf.decoder.decoder,
           "-o", tmp_parsed_dir,
           _features_path(lconf),
           _features_path(lconf)]
    call(cmd, cwd=tmp_parsed_dir, stderr=log)

    # combine mini csv files from each dialogue into
    # single file for whole input
    parsed_dir = lconf.tmp("parsed")
    makedirs(parsed_dir)
    parsed_csv = parsed_subpath(parsed_dir) + ".csv"
    merge_csv(glob.glob(fp.join(tmp_parsed_dir, "*.csv")),
              parsed_csv)

    # units/foo
    src_units_dir = _minicorpus_stage_path(lconf, "units")
    tgt_units_dir = _minicorpus_stage_path(lconf, "units",
                                           result=True)
    makedirs(tgt_units_dir)
    force_symlink(fp.join(src_units_dir, 'simple-da'),
                  parsed_subpath(tgt_units_dir))
    for section in ["parsed", "pos-tagged"]:
        force_symlink(_minicorpus_stage_path(lconf, section),
                      _minicorpus_stage_path(lconf, section,
                                             result=True))

    # discourse/foo
    discourse_dir = _minicorpus_stage_path(lconf, "discourse",
                                           result=True)
    lconf.pyt("parser/parse-to-glozz",
              _unannotated_dir_path(lconf),
              parsed_csv,
              parsed_subpath(discourse_dir))

    # unannotated
    force_symlink(_unannotated_dir_path(lconf),
                  _unannotated_dir_path(lconf, result=True))


def _decode(lconf, log, evaluations=None):
    "Decode the input using all the model/learner combos we know"

    evaluations = evaluations or EVALUATIONS
    for econf in evaluations:
        with _stac_msg("Decoding (dataset: %s, learner: %s, decoder: %s)" %
                       (lconf.dataset,
                        econf.learner.name,
                        econf.decoder.name)):
            _decode_one(lconf, econf, log)


def _graph(lconf, log):
    "Visualise the parses"

    corpus_dir = _minicorpus_path(lconf, result=True)
    cmd = ["stac-util", "graph", corpus_dir,
           "--output", corpus_dir]
    call(cmd, stderr=log)


def _pipeline(lconf, evaluations=None):
    """
    All of the parsing process
    """

    logdir = lconf.tmp("logs")

    def _stage(logname, stage_fn, msg):
        """run a parsing stage

        :type stage_fn: lconf -> filepath -> ()
        """
        logpath = fp.join(logdir, logname + ".txt")
        with _stac_msg(msg or "", quiet=msg is None):
            with open(logpath, 'w') as log:
                stage_fn(lconf, log)

    makedirs(logdir)

    _stage("0100-extract_annot", _soclog_to_csv,
           "Converting (soclog -> stac csv)")
    _stage("0150-segmentation", _segment_into_edus,
           "Segmenting")
    _stage("0200-csv2glozz", _segmented_to_glozz,
           "Converting (stac csv -> glozz)")
    _stage("0300-pos-tagging", _postag,
           "POS tagging")
    _stage("0400-parsing", _sentence_parse,
           "Sentence parsing (if slow, is starting parser server)")
    _stage("0500-dialogue-acts", _dialogue_acts,
           "Dialogue act annotation")
    _stage("0600-features", _feature_extraction,
           "Feature extraction")
    _stage("0700-decoding",
           lambda x, y: _decode(x, y, evaluations=evaluations),
           None)
    _stage("0800-graphs", _graph,
           "Drawing graphs")

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------


def config_argparser(psr):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    psr.set_defaults(func=main)
    psr.add_argument("soclog", metavar="FILE",
                     help="input soclog")
    psr.add_argument("output", metavar="DIR",
                     help="output directory")
    psr.add_argument("--tmpdir", metavar="DIR",
                     help="put intermediary files here "
                     "(for debugging, default is via mktemp)")


def _check_3rd_party():
    """
    Die if our third party deps are missing
    """
    if not fp.isfile(TAGGER_JAR):
        sys.exit("""Need %s
See http://www.ark.cs.cmu.edu/TweetNLP""" % TAGGER_JAR)


def _mk_parser_temp(args):
    """
    Create a temporary directory to save intermediary parser files
    in (may be specified from args but defaults to some mktemp recipe)
    """
    if args.tmpdir is None:
        tmpdir = fp.join(tempfile.mkdtemp(prefix="stac"),
                         _stub_name(args.soclog))
    else:
        tmpdir = args.tmpdir
    makedirs(tmpdir)
    return tmpdir


# pylint: disable=no-member
def _copy_results(lconf, output_dir):
    "copy interesting files from tmp dir to output dir"

    # copy the csv parses
    parsed_results = fp.join(output_dir, "parsed")
    if fp.exists(parsed_results):
        shutil.rmtree(parsed_results)
    shutil.copytree(lconf.tmp("parsed"), parsed_results)

    # copy the svg graphs into single flat dir
    graphs_dir = fp.join(output_dir, "graphs")
    makedirs(graphs_dir)
    svg_files = sh.find(_minicorpus_path(lconf, result=True),
                        "-name", "*.svg", _iter=True)
    for svg in (f.strip() for f in svg_files):
        svg2 = fp.join(graphs_dir,
                       fp.basename(fp.dirname(svg)) + ".svg")
        shutil.copyfile(svg, svg2)
# pylint: enable=no-member


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    _check_3rd_party()
    data_dir = latest_tmp()
    if not os.path.exists(data_dir):
        exit_ungathered()
    lconf = LoopConfig(soclog=args.soclog,
                       snap_dir=latest_snap(),
                       tmp_dir=_mk_parser_temp(args))
    _pipeline(lconf)
    _copy_results(lconf, args.output)
