# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Extract features
"""

import codecs
import csv
import os

import stac.csv
from ..args import\
    add_usual_input_args, add_usual_output_args,\
    read_corpus, get_output_dir, announce_output_dir
from ..features import\
    extract_pair_features, read_common_inputs,\
    mk_csv_header, K_CLASS


NAME = 'features'


def mk_csv_writer(header, fstream):
    """
    start off csv writer for a given mode
    """
    csv_quoting = csv.QUOTE_MINIMAL

    writer = stac.csv.Utf8DictWriter(fstream,
                                     header,
                                     quoting=csv_quoting)
    writer.writeheader()
    return writer


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser)
    add_usual_output_args(parser)
    parser.add_argument('--debug', action='store_true',
                        help='Emit fields used for debugging purposes')
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    odir = get_output_dir(args)
    inputs = read_common_inputs(args, read_corpus(args))
    header = mk_csv_header(inputs, [K_CLASS])

    of_bn = os.path.join(odir, os.path.basename(args.corpus))
    relations_file = of_bn + '.relations.csv'
    edu_pairs_file = of_bn + '.edu-pairs.csv'
    with codecs.open(relations_file, 'wb') as r_ofile:
        with codecs.open(edu_pairs_file, 'wb') as p_ofile:
            p_writer = mk_csv_writer(header, p_ofile)
            r_writer = mk_csv_writer(header, r_ofile)
            for p_row, r_row in extract_pair_features(inputs):
                p_writer.writerow(p_row)
                r_writer.writerow(r_row)
    announce_output_dir(odir)
