# Author Eric Kow
# License: CeCILL-B (BSD3-ish)

"""
Command line options
"""

from __future__ import print_function
import os
import sys
import tempfile

import educe.rst_dt
import educe.util


def read_corpus(args, verbose=True):
    """
    Read the section of the corpus specified in the command line arguments.
    """
    is_interesting = educe.util.mk_is_interesting(args)
    reader = educe.rst_dt.Reader(args.corpus)
    anno_files = reader.filter(reader.files(), is_interesting)
    return reader.slurp(anno_files, verbose)


def get_output_dir(args):
    """
    Return the output directory specified on (or inferred from) the command
    line arguments, *creating it if necessary*.

    We try the following in order:

    1. If `--output` is given explicitly, we'll just use/create that
    2. OK just make a temporary directory. Later on, you'll probably want
    to call `announce_output_dir`.
    """
    if args.output:
        if os.path.isfile(args.output):
            oops = "Sorry, %s already exists and is not a directory" %\
                args.output
            sys.exit(oops)
        elif not os.path.isdir(args.output):
            os.makedirs(args.output)
        return args.output
    else:
        return tempfile.mkdtemp()


def announce_output_dir(output_dir):
    """
    Tell the user where we saved the output
    """
    print("Output files written to", output_dir, file=sys.stderr)


def add_usual_input_args(parser):
    """
    Augment a subcommand argparser with typical input arguments.
    Sometimes your subcommand may require slightly different output
    arguments, in which case, just don't call this function.

    :param doc_subdoc_required force user to supply --doc/--subdoc
           for this subcommand
    :type doc_subdoc_required bool

    :param help_suffix appended to --doc/--subdoc help strings
    :type help_suffix string
    """
    parser.add_argument('corpus', metavar='DIR', help='corpus dir')
    educe.util.add_corpus_filters(parser)


def add_usual_output_args(parser):
    """
    Augment a subcommand argparser with typical output arguments,
    Sometimes your subcommand may require slightly different output
    arguments, in which case, just don't call this function.
    """
    parser.add_argument('--output', '-o', metavar='DIR',
                        help='output directory (default mktemp)')
