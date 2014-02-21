# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Read and write back without changing anything else; potentially reformats XML
(for version control diffs)
"""

import copy

from stac.edu import sorted_first_widest
from stac.util.args import\
    add_usual_input_args,\
    read_corpus,\
    get_output_dir, announce_output_dir
from stac.util.output import save_document


def _sans_modified_by(anno):
    """
    Strip the lastModifier and lastModificationDate annotations inserted
    by Glozz. These would constitute diff-noise (see `_diff_friendly`
    for details).
    """
    anno2 = copy.deepcopy(anno)
    anno2.metadata['lastModifier'] = 'n/a'
    anno2.metadata['lastModificationDate'] = 0
    return anno2


def _diff_friendly(annos):
    """
    Return a copy of annotations, tweaked and given some arbitrary canonical
    order. The background here is that you might want to do a visual diff
    between the human authored annotations, and automated modifications you
    requested, but in order for that to work we have to to eliminate spurious
    diffs that would obscure the interesting bits.
    """
    return sorted_first_widest(map(_sans_modified_by, annos))

# ---------------------------------------------------------------------
# command and args
# ---------------------------------------------------------------------

NAME = 'rewrite'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    parser_mutex = parser.add_mutually_exclusive_group()
    add_usual_input_args(parser)
    # we want to forbid --diff-friendly --overwrite-input
    # but allow --diff-friendly --output
    parser_mutex.add_argument('--diff-friendly', action='store_true',
                              help='Normalise for diffing')
    parser_mutex.add_argument('--overwrite-input', action='store_true',
                              help='save results back to input dir')
    parser.add_argument('--output', '-o', metavar='DIR',
                        help='output directory (default mktemp)')
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    corpus = read_corpus(args, verbose=True)
    output_dir = get_output_dir(args)
    for k in corpus:
        doc = corpus[k]
        if args.diff_friendly:
            doc.units = _diff_friendly(doc.units)
            doc.relations = _diff_friendly(doc.relations)
            doc.schemas = _diff_friendly(doc.schemas)
        save_document(output_dir, k, doc)
    announce_output_dir(output_dir)
