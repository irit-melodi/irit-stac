# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
server version of parse (soclog in, ??? out)
"""

from __future__ import print_function
from os import path as fp
import sys
import tempfile
import zmq

from attelo.harness.util import makedirs

from . import parse as p
from ..pipeline import (StandaloneParser,
                        Stage, run_pipeline,
                        check_3rd_party,
                        decode,
                        minicorpus_path,
                        attelo_result_path)


NAME = 'serve'
_DEBUG = 0

# ---------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------


def xml_output_path(lconf):
    "final output of the server"
    return attelo_result_path(lconf, lconf.test_evaluation) + ".settlers-xml"


def _to_xml(lconf, log):
    """
    Convert to Settlers XML format
    """
    lconf.pyt("parser/to_settlers_xml",
              minicorpus_path(lconf),
              attelo_result_path(lconf, lconf.test_evaluation),
              "--output", xml_output_path(lconf),
              stdout=log)


SERVER_STAGES = p.CORE_STAGES +\
    [
        Stage("0700-decoding",
              lambda lcf, _: decode(lcf, [lcf.test_evaluation]),
              "Decoding"),
        Stage("0800-xml", _to_xml,
              "Converting (-> settlers xml)"),
    ]

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
    hconf = StandaloneParser(soclog=soclog,
                             tmp_dir=tmp_dir)
    if hconf.test_evaluation is None:
        sys.exit("Can't run server: you didn't specify a test "
                 "evaluation in the local configuration")
    return hconf


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    check_3rd_party()

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
        run_pipeline(lconf, SERVER_STAGES)
        with open(xml_output_path(lconf), 'rb') as fin:
            socket.send(fin.read())
        if not args.incremental:
            lconf = _reset_parser(args)
