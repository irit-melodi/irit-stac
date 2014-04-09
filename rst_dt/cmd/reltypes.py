# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Count mono vs multinuclear relations
"""

from __future__ import print_function
import collections

import educe.rst_dt

from ..args import\
    add_usual_input_args, add_usual_output_args,\
    read_corpus

NAME = 'reltypes'

Counts = collections.namedtuple('Counts', "multi mono")


def empty_counts():
    "Initial counters, ie. all zero"

    return Counts(collections.defaultdict(int),
                  collections.defaultdict(int))


def walk_and_count(tree, counts):
    "Count relation types in tree, incrementing values in `counts`"

    if tree.node.is_nucleus():
        counts.multi[tree.node.rel.lower()] += 1
    elif tree.node.is_satellite():
        counts.mono[tree.node.rel.lower()] += 1
    for child in tree:
        if not isinstance(child, educe.rst_dt.EDU):
            walk_and_count(child, counts)
    return


def print_counts(counts):
    "Summarise relation type counts"

    multi_and_mono = [rel for rel in counts.mono if rel in counts.multi]
    mono_only = [rel for rel in counts.mono if rel not in multi_and_mono]
    multi_only = [rel for rel in counts.multi if rel not in multi_and_mono]

    print("")
    print("Both Mono and multinuclear")
    print("--------------------------")
    for rel in multi_and_mono:
        print("%30s %5d mono, %5d multi" % (rel,
                                            counts.mono[rel],
                                            counts.multi[rel]))

    print("")
    print("Mononuclear only")
    print("----------------")
    for rel in mono_only:
        print("%30s %5d mono" % (rel, counts.mono[rel]))

    print("")
    print("Multinuclear only")
    print("-----------------")
    for rel in multi_only:
        print("%30s %5d multi" % (rel, counts.multi[rel]))


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
    counts = empty_counts()
    corpus = read_corpus(args)
    for k in corpus:
        walk_and_count(corpus[k], counts)
    print_counts(counts)
