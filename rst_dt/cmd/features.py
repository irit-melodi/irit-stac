# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Extract features
"""

NAME = 'features'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    pass
