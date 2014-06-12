# Author Eric Kow
# License: CeCILL-B (BSD3-ish)

"""
Command line options
"""

import argparse
import copy
import os
import sys
import tempfile

import educe.annotation
import educe.stac
import educe.util


def read_corpus(args, verbose=True):
    """
    Read the section of the corpus specified in the command line arguments.
    """
    is_interesting = educe.util.mk_is_interesting(args)
    reader = educe.stac.Reader(args.corpus)
    anno_files = reader.filter(reader.files(), is_interesting)
    return reader.slurp(anno_files, verbose)


def read_corpus_with_unannotated(args, verbose=True):
    """
    Read the section of the corpus specified in the command line arguments.
    """
    is_interesting1 = educe.util.mk_is_interesting(args)
    reader = educe.stac.Reader(args.corpus)
    anno_files1 = reader.filter(reader.files(), is_interesting1)
    # we only want to read the unannotated stuff if we also have other
    # normal interesting matches (useful if annotator is forced)
    if anno_files1:
        args2 = copy.deepcopy(args)
        args2.stage = 'unannotated'
        args2.annotator = None
        is_interesting2 = educe.util.mk_is_interesting(args2)
        is_interesting = lambda x: is_interesting1(x) or is_interesting2(x)
        anno_files = reader.filter(reader.files(), is_interesting)
        return reader.slurp(anno_files, verbose)
    else:
        sys.exit("No matching files")


def get_output_dir(args):
    """
    Return the output directory specified on (or inferred from) the command
    line arguments, *creating it if necessary*.

    We try the following in order:

    1. If `--output` is given explicitly, we'll just use/create that
    2. If the subcommand supports `--overwrite`, and the user specifies it
    on the command line, the output directory may well be the original
    corpus dir (*gulp*! Better use version control!)
    3. OK just make a temporary directory. Later on, you'll probably want
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
    elif "overwrite_input" in args.__dict__ and args.overwrite_input:
        return args.corpus
    else:
        return tempfile.mkdtemp()


def announce_output_dir(output_dir):
    """
    Tell the user where we saved the output
    """
    print >> sys.stderr, "Output files written to", output_dir


def add_commit_args(parser):
    """
    Augment a subcommand argparser with an option to emit a commit
    message for your version control tracking
    """
    parser.add_argument('--no-commit-msg', action='store_true',
                        help='Skip commit message summary')


def add_usual_input_args(parser,
                         doc_subdoc_required=False,
                         help_suffix=None):
    """
    Augment a subcommand argparser with typical input arguments.
    Sometimes your subcommand may require slightly different output
    arguments, in which case, just don't call this function.

    :param doc_subdoc_required force user to supply --doc/--subdoc
           for this subcommand (note you'll need to add stage/anno
           yourself)
    :type doc_subdoc_required bool

    :param help_suffix appended to --doc/--subdoc help strings
    :type help_suffix string
    """
    parser.add_argument('corpus', metavar='DIR', help='corpus dir')
    if doc_subdoc_required:
        doc_help = 'document'
        subdoc_help = 'subdocument'
        if help_suffix:
            doc_help = doc_help + ' ' + help_suffix
            subdoc_help = subdoc_help + ' ' + help_suffix
        parser.add_argument('--doc', metavar='DOC',
                            help=doc_help, required=doc_subdoc_required)
        parser.add_argument('--subdoc', metavar='SUBDOC',
                            help=subdoc_help, required=doc_subdoc_required)
    else:
        educe.util.add_corpus_filters(parser)


def add_usual_output_args(parser):
    """
    Augment a subcommand argparser with typical output arguments,
    Sometimes your subcommand may require slightly different output
    arguments, in which case, just don't call this function.
    """
    parser.add_argument('--output', '-o', metavar='DIR',
                        help='output directory (default mktemp)')
    parser.add_argument('--overwrite-input', action='store_true',
                        help='save results back to input dir')


def anno_id(string):
    """
    Split AUTHOR_DATE string into tuple, complaining if we don't have such a
    string. Used for argparse
    """
    parts = string.split('_')
    if len(parts) != 2:
        msg = "%r is not of form author_date" % string
        raise argparse.ArgumentTypeError(msg)
    return (parts[0], int(parts[1]))


def comma_span(string):
    """
    Split a comma delimited pair of integers into an educe span
    """
    parts = list(map(int, string.split(',')))
    if len(parts) != 2:
        msg = "%r is not of form n,m" % string
        raise argparse.ArgumentTypeError(msg)
    return educe.annotation.Span(parts[0], parts[1])
