# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
parse a soclog file
"""

from __future__ import print_function
from os import path as fp
import os
import shutil
import tempfile

import sh


from attelo.harness.util import\
    makedirs, call, force_symlink

from ..local import\
    CORENLP_SERVER_DIR, CORENLP_ADDRESS,\
    TAGGER_JAR, LEX_DIR,\
    EVALUATIONS, ATTELO_CONFIG_FILE
from ..pipeline import\
    (LoopConfig, stac_msg, Stage, run_pipeline,
     check_3rd_party,
     features_path,
     minicorpus_path,
     minicorpus_stage_path,
     parsed_bname,
     resource_np_path,
     attelo_result_path,
     seg_path,
     stub_name,
     unannotated_stub_path,
     unannotated_dir_path,
     unseg_path)
from ..util import\
    (latest_snap,
     snap_model_path, snap_dialogue_act_model_path)


NAME = 'parse'
_DEBUG = 0


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
    with open(turns_path, "w") as turns_file:
        lconf.pyt("txt2csv/extract_turns.py", lconf.soclog,
                  stdout=turns_file)
    lconf.pyt("txt2csv/extract_annot.py", turns_path,
              stdout=log)
    os.rename(turns_path + "csv", unseg_path(lconf))
    os.unlink(turns_path)


def _segment_into_edus(lconf, log):
    """
    segment (csv -> csv)
    """
    lconf.pyt("segmentation/simple-segments",
              "--csv", unseg_path(lconf),
              seg_path(lconf),
              stderr=log)


def _segmented_to_glozz(lconf, log):
    """
    convert the segmented CSV into glozz format
    (because that's what some of our other tools
    expectd)

    Return a corpus directory
    """
    lconf.pyt("intake/csvtoglozz.py",
              "-f", seg_path(lconf),
              "--start", "1000",
              stderr=log,
              cwd=lconf.tmp_dir)

    their_stub = lconf.tmp('segmented')
    unanno_stub = unannotated_stub_path(lconf)
    makedirs(fp.dirname(unanno_stub))
    os.rename(their_stub + '.aa', unanno_stub + '.aa')
    os.rename(their_stub + '.ac', unanno_stub + '.ac')


def _postag(lconf, log):
    """
    Run part of speech tagger on input
    """
    corpus_dir = minicorpus_path(lconf)
    lconf.pyt("run-3rd-party",
              "--ark-tweet-nlp", lconf.abspath(TAGGER_JAR),
              corpus_dir, corpus_dir,
              stderr=log)


def _sentence_parse(lconf, log):
    """
    Run sentence parser on input.
    """
    corpus_dir = minicorpus_path(lconf)
    lconf.pyt("run-3rd-party",
              "--corenlp-server", lconf.abspath(CORENLP_SERVER_DIR),
              "--corenlp-address", CORENLP_ADDRESS,
              # "--corenlp", CORENLP_DIR,
              corpus_dir, corpus_dir,
              stderr=log)


def _unit_annotations(lconf, log):
    """
    Using a previously predicted dialogue act model,
    guess dialogue acts for all the EDUs
    """
    corpus_dir = minicorpus_path(lconf)
    model_path = snap_dialogue_act_model_path(lconf)
    lconf.pyt("stac/unit_annotations.py",
              corpus_dir,
              lconf.abspath(LEX_DIR),
              "--model", model_path,
              "--output", corpus_dir,
              stderr=log)


def _resource_extraction(lconf, log):
    """
    Using a previously predicted dialogue act model,
    guess dialogue acts for all the EDUs
    """
    corpus_dir = minicorpus_path(lconf)
    cmd = ["stac-learning", "resource-nps",
           corpus_dir,
           lconf.abspath(LEX_DIR),
           "--output",
           resource_np_path(lconf)]
    call(cmd, stderr=log)


def _feature_extraction(lconf, log):
    """
    Extract features from our input glozz file
    """
    corpus_dir = minicorpus_path(lconf)
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
        return fp.join(parent, parsed_bname(lconf, econf))

    tmp_parsed_dir = parsed_subpath(lconf.tmp("tmp-parsed"))
    makedirs(tmp_parsed_dir)
    cmd = ["attelo", "decode",
           "-C", lconf.abspath(ATTELO_CONFIG_FILE),
           "-A", snap_model_path(lconf, econf, "attach"),
           "-R", snap_model_path(lconf, econf, "relate"),
           "-d", econf.decoder.decoder,
           "-o", tmp_parsed_dir,
           features_path(lconf),
           features_path(lconf)]
    call(cmd, cwd=tmp_parsed_dir, stderr=log)

    # combine mini csv files from each dialogue into
    # single file for whole input
    parsed_dir = lconf.tmp("parsed")
    makedirs(parsed_dir)

    # units/foo
    src_units_dir = minicorpus_stage_path(lconf, "units")
    tgt_units_dir = minicorpus_stage_path(lconf, "units",
                                          result=True)
    makedirs(tgt_units_dir)
    force_symlink(fp.join(src_units_dir, 'simple-da'),
                  parsed_subpath(tgt_units_dir))
    for section in ["parsed", "pos-tagged"]:
        force_symlink(minicorpus_stage_path(lconf, section),
                      minicorpus_stage_path(lconf, section,
                                            result=True))

    # discourse/foo
    discourse_dir = minicorpus_stage_path(lconf, "discourse",
                                          result=True)
    lconf.pyt("parser/parse-to-glozz",
              unannotated_dir_path(lconf),
              attelo_result_path(lconf, econf, lconf.tmp("tmp-parsed")),
              parsed_subpath(discourse_dir))

    # unannotated
    force_symlink(unannotated_dir_path(lconf),
                  unannotated_dir_path(lconf, result=True))


def _decode(lconf, log, evaluations=None):
    "Decode the input using all the model/learner combos we know"

    evaluations = evaluations or EVALUATIONS
    for econf in evaluations:
        template = "Decoding (dataset: %s, learner: %s, decoder: %s)"
        with stac_msg(template %
                      (lconf.dataset,
                       econf.learner.name,
                       econf.decoder.name)):
            _decode_one(lconf, econf, log)


def _graph(lconf, log):
    "Visualise the parses"

    corpus_dir = minicorpus_path(lconf, result=True)
    cmd = ["stac-util", "graph", corpus_dir,
           "--output", corpus_dir]
    call(cmd, stderr=log)


CORE_STAGES = \
    [Stage("0100-extract_annot", _soclog_to_csv,
           "Converting (soclog -> stac csv)"),
     Stage("0150-segmentation", _segment_into_edus,
           "Segmenting"),
     Stage("0200-csvtoglozz", _segmented_to_glozz,
           "Converting (stac csv -> glozz)"),
     Stage("0300-pos-tagging", _postag,
           "POS tagging"),
     Stage("0400-parsing", _sentence_parse,
           "Sentence parsing (if slow, is starting parser server)"),
     Stage("0500-unit-annotations", _unit_annotations,
           "Unit-level annotation (dialogue acts, addressees)"),
     Stage("0550-resource", _resource_extraction,
           "Resource extraction"),
     Stage("0600-features", _feature_extraction,
           "Feature extraction")]


def _pipeline(lconf, evaluations=None):
    """
    All of the parsing process
    """

    stages = CORE_STAGES +\
        [Stage("0700-decoding",
               lambda x, y: _decode(x, y, evaluations=evaluations),
               None),
         Stage("0800-graphs", _graph, "Drawing graphs")]
    run_pipeline(lconf, stages)


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


def _mk_parser_temp(args):
    """
    Create a temporary directory to save intermediary parser files
    in (may be specified from args but defaults to some mktemp recipe)
    """
    if args.tmpdir is None:
        tmpdir = fp.join(tempfile.mkdtemp(prefix="stac"),
                         stub_name(args.soclog))
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
    svg_files = sh.find(minicorpus_path(lconf, result=True),
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
    check_3rd_party()
    lconf = LoopConfig(soclog=args.soclog,
                       snap_dir=latest_snap(),
                       tmp_dir=_mk_parser_temp(args))
    _pipeline(lconf)
    _copy_results(lconf, args.output)
