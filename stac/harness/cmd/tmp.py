# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
(tmp) send soclog file to parser server
"""

from __future__ import print_function
import zmq

NAME = 'tmp'

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
    psr.add_argument("--address",
                     required=True,
                     help="server address")



def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
#pylint: disable=no-member
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
#pylint: enable=no-member
    socket.connect(args.address)
    with open(args.soclog, 'rb') as fin:
        socket.send(fin.read())
    response = socket.recv()
    print(response)
    socket.close()
