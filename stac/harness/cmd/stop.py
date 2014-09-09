# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
stop any servers we have
"""

from __future__ import print_function
from attelo.harness.util import call
import zmq

from ..local import LEX_DIR, CORENLP_ADDRESS

NAME = 'stop'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    parser.set_defaults(func=main)


def main(_):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(CORENLP_ADDRESS)
    socket.send("stop")
    message = socket.recv()
    print("Received reply [%s]" % message)
