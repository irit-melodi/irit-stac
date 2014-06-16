# Author Eric Kow
# License: CeCILL-B (BSD3-ish)

"""
Command line options
"""

from __future__ import print_function
import os
import sys
import tempfile

import educe.pdtb
import educe.util


def read_corpus(args, verbose=True):
    """
    Read the section of the corpus specified in the command line arguments.
    """
    is_interesting = educe.util.mk_is_interesting(args)
    reader = educe.pdtb.Reader(args.corpus)
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
    """
    parser.add_argument('corpus', metavar='DIR', help='corpus dir')
    educe.util.add_corpus_filters(parser, fields=['doc'])


def add_usual_output_args(parser):
    """
    Augment a subcommand argparser with typical output arguments,
    Sometimes your subcommand may require slightly different output
    arguments, in which case, just don't call this function.
    """
    parser.add_argument('--output', '-o', metavar='DIR',
                        help='output directory (default mktemp)')


def mk_output_path(odir, k):
    """
    Path stub (needs extension) given an output directory and a
    PDTB corpus key
    """
    relpath = educe.pdtb.id_to_path(k)
    ofile_dirname = os.path.join(odir, os.path.dirname(relpath))
    ofile_basename = os.path.basename(relpath)
    if not os.path.exists(ofile_dirname):
        os.makedirs(ofile_dirname)
    return os.path.join(ofile_dirname, ofile_basename)
