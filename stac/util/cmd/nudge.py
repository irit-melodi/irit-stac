# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Slightly adjust unit annotation boundaries
"""

import copy
import sys

from educe import stac
from educe.annotation import Span

from stac.util.annotate import show_diff
from stac.util.args import\
        add_usual_input_args, add_usual_output_args,\
        read_corpus, get_output_dir, announce_output_dir
from stac.util.doc import narrow_to_span
from stac.util.output import save_document

def _enclosing_turn_span(doc, span):
    """
    Return the span for any turn annotations that enclose this span.
    If none are found, return the span itself
    """
    def is_match(anno):
        "enclosing turn"
        return stac.is_turn(anno) and anno.text_span().encloses(span)
    spans = [span] + [u.text_span() for u in doc.units if is_match(u)]
    return Span(min(x.char_start for x in spans),
                max(x.char_end   for x in spans))

def _is_nudge(offset):
    """
    Return True if a character offset is small enough to be treated as
    a "nudge"
    """
    return abs(offset) <= 1

def _mini_diff(k, old_doc_span, new_doc_span):
    """
    Return lines of text to be printed out, showing how the nudge
    affected the text
    """
    old_doc, old_span = old_doc_span
    new_doc, new_span = new_doc_span
    interesting_span = _enclosing_turn_span(old_doc, old_span)
    mini_old_doc = narrow_to_span(old_doc, interesting_span)
    mini_new_doc = narrow_to_span(new_doc, interesting_span)
    return ["======= NUDGE %s to %s in %s ========" % (old_span, new_span, k),
            "...",
            show_diff(mini_old_doc, mini_new_doc),
            "...",
            ""]

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

NAME = 'nudge'

def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser, doc_subdoc_required=True)
    add_usual_output_args(parser)
    parser.add_argument('start', metavar='INT', type=int,
                        help='text span start')
    parser.add_argument('end', metavar='INT', type=int,
                        help='text span end')
    parser.add_argument('nudge_start', metavar='INT', type=int,
                        help='adjust start [-1 to 1]')
    parser.add_argument('nudge_end', metavar='INT', type=int,
                        help='adjust end   [-1 to 1]')
    parser.add_argument('--allow-shove', action='store_true',
                        help='allow adjustments larger than 1')
    parser.add_argument('--stage', metavar='STAGE',
                        choices=['discourse', 'units', 'unannotated'])
    parser.add_argument('--annotator', metavar='STRING')
    parser.set_defaults(func=main)


# FIXME: there may be a more idiomatic way to express these
def _screen_args(args):
    """
    Check argument consistency rules I don't yet know how to express
    in a cleaner way
    """
    if not args.allow_shove and\
            (not _is_nudge(args.nudge_start) or
             not _is_nudge(args.nudge_end)):
        sys.exit("Use --allow-shove if you really mean to nudge by [%d,%d]"\
                % (args.nudge_start, args.nudge_end))
    if not args.allow_shove and (args.annotator or args.stage):
        sys.exit("Use --allow-shove if you really mean to limit "\
                 + "--stage or --annotator")
    if args.stage:
        if args.stage != 'unannotated' and not args.annotator:
            sys.exit("--annotator is required unless --stage is unannotated")
        elif args.stage == 'unannotated' and args.annotator:
            sys.exit("--annotator is forbidden if --stage is unannotated")


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    _screen_args(args)
    corpus = read_corpus(args, verbose=True)
    output_dir = get_output_dir(args)

    old_span = Span(args.start, args.end)
    new_span = Span(args.start + args.nudge_start,
                    args.end   + args.nudge_end)
    for k in corpus:
        old_doc = corpus[k]
        new_doc = copy.deepcopy(old_doc)
        found = False
        for anno in new_doc.units:
            if anno.span == old_span:
                anno.span = copy.deepcopy(new_span)
                found = True
        if found:
            diffs = _mini_diff(k, (old_doc, old_span), (new_doc, new_span))
            print >> sys.stderr, "\n".join(diffs).encode('utf-8')
        else:
            print >> sys.stderr,\
                    "WARNING: No annotations found for %s in %s" % (old_span, k)
        save_document(output_dir, k, new_doc)
    announce_output_dir(output_dir)
