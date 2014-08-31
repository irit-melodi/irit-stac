# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
useful counts about the corpus
"""

from __future__ import print_function
from os import path as fp

from attelo.harness.util import call
from educe.stac.util.args import get_output_dir, announce_output_dir

from ..local import ANNOTATORS, TRAINING_CORPORA

NAME = 'count'


def config_argparser(psr):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    psr.set_defaults(func=main)
    psr.add_argument("--output", metavar="DIR",
                     help="output directory")


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    corpora = TRAINING_CORPORA +\
        ['data/socl-season2-annotated-only',
         'data/combined-annotated-only',
         'data/combined']  # provisional virtual corpora for counting
    odir = get_output_dir(args)
    for corpus in corpora:
        ofilename = fp.join(odir, fp.basename(corpus) + ".txt")
        with open(ofilename, 'w') as ofile:
            call(["stac-util", "count", corpus,
                  "--annotator", ANNOTATORS],
                 stdout=ofile)
    announce_output_dir(odir)
