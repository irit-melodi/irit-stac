# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Merge several dialogue level annotations into one
"""

import copy
import sys

from educe.annotation import Span
from educe.glozz import GlozzException

from stac.util.args import\
        add_usual_input_args, add_usual_output_args, anno_id,\
        read_corpus,\
        get_output_dir, announce_output_dir
from stac.util.glozz import\
        anno_id_from_tuple, anno_id_to_tuple,\
        get_turn, is_dialogue
from stac.util.output import save_document

def _get_annotation_with_id(sought_tuple, annotations):
    """
    Given a tuple (author,creation_date), pick out the one annotation
    whose id matches.  There must be exactly one.
    """
    sought = anno_id_from_tuple(sought_tuple)
    candidates = [x for x in annotations if x.local_id() == sought]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        raise Exception('More than one annotation found with id %s' % sought)
    else:
        raise Exception('No annotations found with id %s' % sought)


def _concatenate_features(annotations, feature):
    """
    Concatenate the values for the given features for all the annotations.
    Ignore cases where the feature is unset
    """
    values_ = [x.features.get(feature) for x in annotations]
    values = [x for x in values_ if x]
    if values:
        return " ".join(values)
    else:
        return None


# TODO: this could be rewritten using the enclosure graph
def _dialogues_in_turns(corpus, turn1, turn2):
    """
    Given a pair of turns
    """

    # grab a document from the set (assumption here is that
    # they are all morally the same doc)
    if not corpus.values():
        sys.exit("No documents selected")
    doc = corpus.values()[0]

    starting_turn = get_turn(turn1, doc)
    ending_turn = get_turn(turn2, doc)

    # there's a bit of fuzz for whitespace before/after the
    # turns
    span = Span(starting_turn.text_span().char_start - 1,
                ending_turn.text_span().char_end + 1)

    def is_in_range(anno):
        """
        If the annotation is a dialogue that is covered by the
        turns in question
        """
        return is_dialogue(anno) and span.encloses(anno.span)

    matching_dialogues = filter(is_in_range, doc.annotations())
    return [anno_id_to_tuple(x.local_id()) for x in matching_dialogues]

def _merge_dialogues_in_document(sought, doc):
    """
    Given an iterable of dialogue annotation ids, merge them
    replace the relevant dialogue annotations with a single
    combined one. Take the id (creation date, author,etc)
    from the first of the dialogues.

    NB: modifies the document
    """
    dialogues_ = [_get_annotation_with_id(d, doc.units) for d in sought]
    dialogues = sorted(dialogues_,
                       key=lambda x: x.text_span().char_start)
    combined = copy.deepcopy(dialogues[0])
    combined.span =\
            Span(min(x.text_span().char_start for x in dialogues),
                 max(x.text_span().char_end   for x in dialogues))
    for feat in ['Trades', 'Gets', 'Dice_rolling']:
        combined.features[feat] = _concatenate_features(dialogues, feat)
    for dialogue in dialogues:
        doc.units.remove(dialogue)
    doc.units.append(combined)

# ---------------------------------------------------------------------
# command and args
# ---------------------------------------------------------------------

NAME='merge-dialogue'

def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser, doc_subdoc_required=True,
                         help_suffix='in which to merge')
    add_usual_output_args(parser)
    parser_mutex = parser.add_mutually_exclusive_group(required=True)
    parser_mutex.add_argument('--dialogues',
                              metavar='ANNO_ID', type=anno_id,
                              nargs='+',
                              help='eg. stac_39819045 stac_98871771')
    parser_mutex.add_argument('--turns',
                              metavar='INT', type=int,
                              nargs=2,
                              help='eg. 187 192')
    parser.set_defaults(func=main)

def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """

    if not args.turns and len(args.dialogues) < 2:
        sys.exit("Must specify at least two dialogues")
    output_dir = get_output_dir(args)
    corpus = read_corpus(args, verbose=True)
    if args.turns:
        try:
            sought = _dialogues_in_turns(corpus, args.turns[0], args.turns[1])
            if len(sought) < 2:
                sys.exit("Must specify at least two dialogues")
            print >> sys.stderr,\
                "Merging dialogues %s" % map(anno_id_from_tuple, sought)
        except GlozzException as oops:
            sys.exit(str(oops))
    else:
        sought = args.dialogues
    for k in corpus:
        doc = corpus[k]
        _merge_dialogues_in_document(sought, doc)
        save_document(output_dir, k, doc)
    announce_output_dir(output_dir)
