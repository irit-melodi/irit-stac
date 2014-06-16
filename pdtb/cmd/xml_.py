# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Convert to our PDTBX format
"""

from __future__ import print_function

import educe.pdtb.xml_ as pdtbx

from ..args import\
    add_usual_input_args, add_usual_output_args,\
    get_output_dir, mk_output_path,\
    announce_output_dir,\
    read_corpus

NAME = 'xml'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser)
    add_usual_output_args(parser)
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    corpus = read_corpus(args)
    output_dir = get_output_dir(args)
    for k in sorted(corpus):
        opath = mk_output_path(output_dir, k) + '.pdtbx'
        pdtbx.write_pdtbx_file(opath, corpus[k])
        #readback = pdtbx.read_pdtbx_file(opath)
        #assert(corpus[k] == readback)
    announce_output_dir(output_dir)
