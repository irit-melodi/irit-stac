# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
print known features
"""

from attelo.harness.util import call

from ..local import LEX_DIR

NAME = 'features'


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
    call(["stac-learning", "features", LEX_DIR])
