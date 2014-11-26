# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
server version of parse (soclog in, ??? out)
"""

from __future__ import print_function
from os import path as fp
import tempfile
import zmq

from attelo.harness.util import\
    makedirs, call
from attelo.harness.config import\
    LearnerConfig, DecoderConfig, EvaluationConfig


from . import parse as p
from ..util import\
    latest_snap,\
    snap_model_path, snap_dialogue_act_model_path,\
    merge_csv
from ..local import\
    _mk_econf_name, ATTELO_CONFIG_FILE

NAME = 'serve'
_DEBUG = 0

# ---------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------


def _result_path(lconf, econf, parent=None):
    """
    Path to directory where we are saving results
    """
    parent = parent or lconf.tmp("parsed")
    return fp.join(parent, p._parsed_bname(lconf, econf))


def _attelo_result_path(lconf, econf, parent=None):
    """
    Path to attelo graph file
    """
    return fp.join(_result_path(lconf, econf, parent),
                   "graph.conll")


def _decode_one(lconf, econf, log):
    """
    Run the decoder on a single config and convert the output
    """
    parsed_dir = _result_path(lconf, econf)
    makedirs(parsed_dir)
    cmd = ["attelo", "decode",
           "-C", lconf.abspath(ATTELO_CONFIG_FILE),
           "-A", snap_model_path(lconf, econf, "attach"),
           "-R", snap_model_path(lconf, econf, "relate"),
           "-d", econf.decoder.decoder,
           "-o", parsed_dir,
           p._features_path(lconf),
           p._features_path(lconf)]
    call(cmd, cwd=parsed_dir, stderr=log)


def _decode(lconf, econf, log):
    "Decode the input using all the model/learner combos we know"

    with p._stac_msg("Decoding (dataset: %s, learner: %s, decoder: %s)" %
                   (lconf.dataset,
                    econf.learner.name,
                    econf.decoder.name)):
        _decode_one(lconf, econf, log)


def _to_xml(lconf, econf, log):
    """
    Convert to Settlers XML format
    """
    lconf.pyt("parser/to_settlers_xml",
              p._minicorpus_path(lconf),
              _attelo_result_path(lconf, econf),
              "--output",
              _attelo_result_path(lconf, econf) + ".settlers-xml")


def _pipeline(lconf, econf):
    """
    All of the parsing process
    """

    logdir = lconf.tmp("logs")

    def _stage(logname, stage_fn, msg):
        """run a parsing stage

        :type stage_fn: lconf -> filepath -> ()
        """
        logpath = fp.join(logdir, logname + ".txt")
        with p._stac_msg(msg or "", quiet=msg is None):
            with open(logpath, 'w') as log:
                stage_fn(lconf, log)

    makedirs(logdir)

    _stage("0100-extract_annot", p._soclog_to_csv,
           "Converting (soclog -> stac csv)")
    _stage("0150-segmentation", p._segment_into_edus,
           "Segmenting")
    _stage("0200-csv2glozz", p._segmented_to_glozz,
           "Converting (stac csv -> glozz)")
    _stage("0300-pos-tagging", p._postag,
           "POS tagging")
    _stage("0400-parsing", p._sentence_parse,
           "Sentence parsing (if slow, is starting parser server)")
    _stage("0500-unit-annotations", p._unit_annotations,
           "Unit-level annotation (dialogue acts, addressees)")
    _stage("0600-features", p._feature_extraction,
           "Feature extraction")
    _stage("0700-decoding",
           lambda x, y: _decode(x, econf, y),
           None)
    _stage("0800-xml",
           lambda x, y: _to_xml(x, econf, y),
           "Converting (conll + corpus -> settlers xml)")


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
    psr.add_argument("--incremental",
                     action='store_true',
                     help="each connection builds up the current "
                     "input; restart parser for new input")
    psr.add_argument("--tmpdir", metavar="DIR",
                     help="put intermediary files here "
                     "(for debugging, default is via mktemp)")
    psr.add_argument("--port",
                     type=int,
                     required=True,
                     help="port to listen on")


def _mk_server_temp(args):
    """
    Create a temporary directory to save intermediary parser files
    in (may be specified from args but defaults to some mktemp recipe)
    """
    if args.tmpdir is None:
        tmp_dir = fp.join(tempfile.mkdtemp(prefix="stac"))
    else:
        tmp_dir = args.tmpdir
    makedirs(tmp_dir)
    return tmp_dir


def _reset_parser(args):
    """
    Reset the parser and return the corresponding loop configuariton
    """
    tmp_dir = _mk_server_temp(args)
    soclog = fp.join(tmp_dir, "soclog")
    open(soclog, 'wb').close()
    return p.LoopConfig(soclog=soclog,
                        snap_dir=latest_snap(),
                        tmp_dir=tmp_dir)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    p._check_3rd_party()

    learner = LearnerConfig.simple("maxent")
    decoder = DecoderConfig.simple("locallyGreedy")
    econf = EvaluationConfig(name=_mk_econf_name(learner, decoder),
                             learner=learner,
                             decoder=decoder)
#pylint: disable=no-member
    context = zmq.Context()
    socket = context.socket(zmq.REP)
#pylint: enable=no-member
    socket.bind("tcp://*:{}".format(args.port))
    lconf = _reset_parser(args)
    while True:
        incoming = socket.recv()
        with open(lconf.soclog, 'ab') as fout:
            print(incoming.strip(), file=fout)
        _pipeline(lconf, econf)
        results_file = _attelo_result_path(lconf, econf) + ".settlers-xml"
        with open(results_file, 'rb') as fin:
            socket.send(fin.read())
        if not args.incremental:
            lconf = _reset_parser(args)
