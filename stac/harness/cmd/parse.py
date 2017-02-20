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

from attelo.harness.util import (makedirs, call, force_symlink)
import sh

from ..local import (CORENLP_SERVER_DIR, CORENLP_ADDRESS,
                     TAGGER_JAR, LEX_DIR,
                     DIALOGUE_ACT_LEARNER,
                     EVALUATIONS)
from ..pipeline import\
    (StandaloneParser,
     Stage, run_pipeline,
     check_3rd_party,
     dact_features_path,
     dact_model_path,
     decode,
     minicorpus_path,
     minicorpus_doc_path,
     minicorpus_stage_path,
     parsed_bname,
     resource_np_path,
     attelo_result_path,
     seg_path,
     stub_name,
     unannotated_stub_path,
     unannotated_dir_path,
     unseg_path)


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
    lconf.pyt("intake/soclogtocsv.py",
              lconf.soclog,
              "--output", unseg_path(lconf),
              stderr=log)


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
    d_model_path = dact_model_path(lconf, DIALOGUE_ACT_LEARNER)
    d_features_path = dact_features_path(lconf)
    d_vocab_path = d_features_path + '.vocab'

    lconf.pyt("stac/unit_annotations.py",
              corpus_dir,
              lconf.abspath(LEX_DIR),
              "--model", d_model_path,
              "--vocab", d_vocab_path,
              "--labels", d_features_path,
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
    vocab_path = lconf.mpack_paths(test_data=False)[3]
    cmd = ["stac-learning", "extract",
           "--parsing",
           "--vocab", vocab_path,
           corpus_dir,
           lconf.abspath(LEX_DIR),
           lconf.tmp_dir]
    call(cmd, stderr=log)


def _format_decoder_output(lconf, log):
    """
    Convert decoder output to Glozz (for visualisation really)
    and copy it to resultcorpus
    """
    makedirs(minicorpus_doc_path(lconf, result=True))
    # unannotated
    force_symlink(unannotated_dir_path(lconf),
                  unannotated_dir_path(lconf, result=True))

    # parsed, postagged
    for section in ["parsed", "pos-tagged"]:
        force_symlink(minicorpus_stage_path(lconf, section),
                      minicorpus_stage_path(lconf, section,
                                            result=True))

    for econf in lconf.evaluations:
        # units/foo
        src_units_dir = minicorpus_stage_path(lconf, "units")
        tgt_units_dir = minicorpus_stage_path(lconf, "units",
                                              result=True)
        makedirs(tgt_units_dir)
        force_symlink(fp.join(src_units_dir, 'simple-da'),
                      fp.join(tgt_units_dir, parsed_bname(lconf, econf)))

        # discourse
        lconf.pyt("parser/parse-to-glozz",
                  minicorpus_path(lconf),
                  attelo_result_path(lconf, econf),
                  minicorpus_path(lconf, result=True),
                  stderr=log)


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


def _pipeline(lconf):
    """
    All of the parsing process
    """

    stages = CORE_STAGES +\
        [Stage("0700-decoding",
               lambda x, _: decode(x, lconf.evaluations),
               "Decoding"),
         Stage("0750-formatting", _format_decoder_output,
               "Formatting output"),
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
    lconf = StandaloneParser(soclog=args.soclog,
                             tmp_dir=_mk_parser_temp(args))
    _pipeline(lconf)
    _copy_results(lconf, args.output)
