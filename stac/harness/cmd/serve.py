# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
server version of parse (soclog in, ??? out)
"""

from __future__ import print_function
from functools import wraps
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
    snap_model_path
from ..local import\
    _mk_econf_name, ATTELO_CONFIG_FILE
from ..pipeline import\
    (Stage, run_pipeline, check_3rd_party,
     features_path,
     minicorpus_path,
     result_path, attelo_result_path)

NAME = 'serve'
_DEBUG = 0

# ---------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------


def _decode_one(lconf, econf, log):
    """
    Run the decoder on a single config and convert the output
    """
    parsed_dir = result_path(lconf, econf)
    makedirs(parsed_dir)
    cmd = ["attelo", "decode",
           "-C", lconf.abspath(ATTELO_CONFIG_FILE),
           "-A", snap_model_path(lconf, econf, "attach"),
           "-R", snap_model_path(lconf, econf, "relate"),
           "-d", econf.decoder.decoder,
           "-o", parsed_dir,
           features_path(lconf),
           features_path(lconf)]
    call(cmd, cwd=parsed_dir, stderr=log)


def _to_xml(lconf, econf, log):
    """
    Convert to Settlers XML format
    """
    lconf.pyt("parser/to_settlers_xml",
              minicorpus_path(lconf),
              attelo_result_path(lconf, econf),
              "--output",
              attelo_result_path(lconf, econf) + ".settlers-xml",
              stdout=log)


def _pipeline(lconf, econf):
    """
    All of the parsing process
    """
    def with_econf(function):
        "inject the evaluation conf into a pipeline stage"
        @wraps(function)
        def wrapper(lcf, log):
            "run with econf"
            return function(lcf, econf, log)
        return wrapper

    decode_msg = "Decoding (dataset: %s, learner: %s, decoder: %s)" %\
        (lconf.dataset, econf.learner.name, econf.decoder.name)
    stages = p.CORE_STAGES +\
        [Stage("0700-decoding", with_econf(_decode_one),
               decode_msg),
         Stage("0800-xml", with_econf(_to_xml),
               "Converting (conll + corpus -> settlers xml)")]
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
    check_3rd_party()

    learner = LearnerConfig.simple("maxent")
    decoder = DecoderConfig.simple("locallyGreedy")
    econf = EvaluationConfig(name=_mk_econf_name(learner, decoder),
                             learner=learner,
                             decoder=decoder)
# pylint: disable=no-member
    context = zmq.Context()
    socket = context.socket(zmq.REP)
# pylint: enable=no-member
    socket.bind("tcp://*:{}".format(args.port))
    lconf = _reset_parser(args)
    while True:
        incoming = socket.recv()
        with open(lconf.soclog, 'ab') as fout:
            print(incoming.strip(), file=fout)
        _pipeline(lconf, econf)
        results_file = attelo_result_path(lconf, econf) + ".settlers-xml"
        with open(results_file, 'rb') as fin:
            socket.send(fin.read())
        if not args.incremental:
            lconf = _reset_parser(args)
