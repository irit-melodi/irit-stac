# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Print internal representation
"""

from __future__ import print_function

from ..args import\
    add_usual_input_args,\
    read_corpus

NAME = 'dump'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser)
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    corpus = read_corpus(args)
    for k in sorted(corpus):
        print("--------------------" * 3)
        print("doc:", k.doc)
        print("--------------------" * 3)
        print()
        for rel in corpus[k]:
            print(unicode(rel).encode('utf-8'))
            print()
