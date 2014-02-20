# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Put subcommand help text here
"""

import copy
import sys

from educe.annotation import Span
import educe.stac

from stac.util.annotate import show_diff
from stac.util.args import\
    add_usual_input_args, add_usual_output_args,\
    get_output_dir, announce_output_dir
from stac.util.doc import compute_renames, move_portion
from stac.util.output import save_document


def is_target(args):
    """
    Corpus filter to pick out the part we want to move to
    """
    def is_match(k):
        "is a target entry"
        return k.doc == args.doc and k.subdoc == args.target
    return is_match


def is_requested(args):
    """
    Corpus filter to pick out the part we want to move from
    """
    def is_match(k):
        "is a source entry"
        return k.doc == args.doc and k.subdoc == args.subdoc
    return is_match


def read_source_corpus(args):
    """
    Read the part of the corpus that we want to move from
    """
    reader = educe.stac.Reader(args.corpus)
    src_files = reader.filter(reader.files(), is_requested(args))
    return reader.slurp(src_files)


def read_target_corpus(args):
    """
    Read the part of the corpus that we want to move to
    """
    reader = educe.stac.Reader(args.corpus)
    tgt_files = reader.filter(reader.files(), is_target(args))
    return reader.slurp(tgt_files)

# ---------------------------------------------------------------------
# command and options
# ---------------------------------------------------------------------

NAME = 'move'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser, doc_subdoc_required=True,
                         help_suffix='to move from')
    add_usual_output_args(parser)
    parser.add_argument('start', metavar='INT', type=int,
                        help='Text span start')
    parser.add_argument('end', metavar='INT', type=int,
                        help='Text span end')
    parser.add_argument('target', metavar='SUBDOC')
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    output_dir = get_output_dir(args)
    if args.start != 0:
        sys.exit("Sorry, only know how to deal with start=0 at the moment")

    src_corpus = read_source_corpus(args)
    tgt_corpus = read_target_corpus(args)

    portion = Span(args.start, args.end)

    renames = compute_renames(tgt_corpus, src_corpus)
    for src_k in src_corpus:
        tgt_k = copy.copy(src_k)
        tgt_k.subdoc = args.target
        if tgt_k not in tgt_corpus:
            sys.exit("Uh-oh! we don't have %s in the corpus" % tgt_k)
        else:
            src_doc = src_corpus[src_k]
            tgt_doc = tgt_corpus[tgt_k]
            new_src_doc, new_tgt_doc =\
                move_portion(renames, src_doc, tgt_doc, portion)
            diffs = ["======= TO %s   ========" % tgt_k,
                     show_diff(tgt_doc, new_tgt_doc),
                     "^------ FROM %s" % src_k,
                     show_diff(src_doc, new_src_doc),
                     ""]
            print >> sys.stderr, "\n".join(diffs)
            save_document(output_dir, src_k, new_src_doc)
            save_document(output_dir, tgt_k, new_tgt_doc)

    announce_output_dir(output_dir)
