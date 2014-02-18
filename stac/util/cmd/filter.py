# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Return a subset of the annotations
"""

import re
import sys

from stac.util.args import\
    add_usual_input_args, add_usual_output_args,\
    read_corpus,\
    get_output_dir, announce_output_dir,\
    anno_id
from stac.util.glozz import anno_id_to_tuple
from stac.util.output import save_document

NAME = 'filter'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser)
    add_usual_output_args(parser)
    parser.add_argument('--type', metavar='PY_REGEX',
                        help='desired type (hint: negation via ^(?!foo)')
    parser.add_argument('--not-id', metavar='ANNO_ID', type=anno_id,
                        help='id to delete')
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    output_dir = get_output_dir(args)
    corpus = read_corpus(args, verbose=True)
    preds = []
    if args.type:
        rgx = re.compile(args.type)

        def pred_type(anno):
            "Annotation is of the desired type"
            match = re.search(rgx, anno.type)
            return match is not None and match.span() != (0, 0)

        preds.append(pred_type)
    if args.not_id:
        def pred_not_id(anno):
            "Annotation ID is not the unwanted one"
            return anno_id_to_tuple(anno.local_id()) != args.not_id
        preds.append(pred_not_id)
    if preds:
        pred = lambda x: all([pred(x) for pred in preds])
    else:
        sys.exit("No filters specified, aborting")

    for k in corpus:
        doc = corpus[k]
        doc.units = filter(pred, doc.units)
        doc.relations = filter(pred, doc.relations)
        doc.schemas = filter(pred, doc.schemas)
        save_document(output_dir, k, doc)
    announce_output_dir(output_dir)
