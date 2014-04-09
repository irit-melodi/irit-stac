# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Convert to dependency tree representation
"""

from __future__ import print_function
import os

import educe.rst_dt
from educe.rst_dt import deptree

from ..args import\
    add_usual_input_args, add_usual_output_args,\
    read_corpus, get_output_dir, announce_output_dir
from .reltypes import\
    empty_counts, walk_and_count

NAME = 'deptree'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser)
    add_usual_output_args(parser)
    parser.set_defaults(func=main)


def convert(corpus, multinuclear, odir):
    """
    Convert every RST tree in the corpus to a dependency tree
    (and back, but simplified using a set of relation types
    that will be systematically treated as multinuclear)
    """
    bin_dir = os.path.join(odir, "rst-binarised")
    dt_dir = os.path.join(odir, "rst-to-dt")
    rst2_dir = os.path.join(odir, "dt-to-rst")
    for subdir in [bin_dir, dt_dir, rst2_dir]:
        if not os.path.exists(subdir):
            os.makedirs(subdir)

    for k in corpus:
        suffix = os.path.splitext(k.doc)[0]

        stree = educe.rst_dt.SimpleRSTTree.from_rst_tree(corpus[k])
        with open(os.path.join(bin_dir, suffix), 'w') as fout:
            fout.write(str(stree))

        dtree = deptree.relaxed_nuclearity_to_deptree(stree)
        with open(os.path.join(dt_dir, suffix), 'w') as fout:
            fout.write(str(dtree))

        stree2 = deptree.relaxed_nuclearity_from_deptree(dtree,
                                                         multinuclear)
        with open(os.path.join(rst2_dir, suffix), 'w') as fout:
            fout.write(str(stree2))


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    odir = get_output_dir(args)
    corpus = read_corpus(args)

    counts = empty_counts()
    for k in corpus:
        walk_and_count(corpus[k], counts)

    # relations that we will treat as multinuclear
    multinuclearish = [rel for rel, count in counts.multi.items()
                       if count >= counts.mono.get(rel, 0)]

    convert(corpus, multinuclearish, odir)
    announce_output_dir(odir)
