# Author: Eric Kow
# License: CeCILL-B (French BSD3)

"""
Visualise discourse and enclosure graphs
"""

import os.path
import sys
import codecs

from educe import graph
from educe.stac import postag
import educe.corpus
import educe.stac
import educe.stac.graph as stacgraph

from stac.util.args import get_output_dir
from stac.util.output import output_path_stub, mk_parent_dirs
import stac.edu

# slightly different from the stock stac-util version because it
# supports live corpus mode
def _read_corpus(args):
    """
    Read and return the corpus specified by the command line arguments
    """
    is_interesting = educe.util.mk_is_interesting(args)
    if args.live:
        reader = educe.stac.LiveInputReader(args.corpus)
        anno_files = reader.files()
    else:
        reader = educe.stac.Reader(args.corpus)
        anno_files = reader.filter(reader.files(), is_interesting)
    return reader.slurp(anno_files, verbose=True)


def _write_dot_graph(k, odir, dot_graph, part=None, run_graphviz=True):
    """
    Write a dot graph and possibly run graphviz on it
    """
    ofile_basename = output_path_stub(odir, k)
    if part is not None:
        ofile_basename += '_' + str(part)
    dot_file = ofile_basename + '.dot'
    svg_file = ofile_basename + '.svg'
    mk_parent_dirs(dot_file)
    with codecs.open(dot_file, 'w', encoding='utf-8') as dotf:
        print >> dotf, dot_graph.to_string()
    if run_graphviz:
        print >> sys.stderr, "Creating %s" % svg_file
        os.system('dot -T svg -o %s %s' % (svg_file, dot_file))


def _main_rel_graph(args):
    """
    Draw graphs showing relation instances between EDUs
    """
    args.stage = 'discourse|units'
    corpus = _read_corpus(args)
    output_dir = get_output_dir(args)

    if args.live:
        keys = corpus
    else:
        keys = [k for k in corpus if k.stage == 'discourse']

    for k in sorted(keys):
        try:
            gra_ = stacgraph.Graph.from_doc(corpus, k)
            if args.strip_cdus:
                gra = gra_.without_cdus()
            else:
                gra = gra_
            dot_gra = stacgraph.DotGraph(gra)
            if dot_gra.get_nodes():
                _write_dot_graph(k, output_dir, dot_gra,
                                 run_graphviz=args.draw)
                if args.split:
                    ccs = gra.connected_components()
                    for part, nodes in enumerate(ccs, 1):
                        gra2 = gra.copy(nodes)
                        _write_dot_graph(k, output_dir,
                                         stacgraph.DotGraph(gra2),
                                         part=part,
                                         run_graphviz=args.draw)
            else:
                print >> sys.stderr, "Skipping %s (empty graph)" % k
        except graph.DuplicateIdException:
            warning = "WARNING: %s has duplicate annotation ids" % k
            print >> sys.stderr, warning


def _main_enclosure_graph(args):
    """
    Draw graphs showing which annotations' spans include the others
    """
    corpus = _read_corpus(args)
    output_dir = get_output_dir(args)
    keys = corpus
    if args.tokens:
        postags = postag.read_tags(corpus, args.corpus)
    else:
        postags = None

    for k in sorted(keys):
        if postags:
            gra_ = stac.edu.EnclosureGraph(corpus[k], postags[k])
        else:
            gra_ = stac.edu.EnclosureGraph(corpus[k])
        if args.reduce:
            gra_.reduce()
        dot_gra = stac.edu.EnclosureDotGraph(gra_)
        if dot_gra.get_nodes():
            dot_gra.set("ratio","compress")
            _write_dot_graph(k, output_dir, dot_gra,
                             run_graphviz=args.draw)
        else:
            print >> sys.stderr, "Skipping %s (empty graph)" % k

# ---------------------------------------------------------------------
# args
# ---------------------------------------------------------------------

NAME = 'graph'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    # note: not the usual input args
    parser.add_argument('corpus', metavar='DIR', help='corpus dir')
    parser.add_argument('--output', metavar='DIR', required=True,
                        help='output  dir')
    parser.add_argument('--no-draw', action='store_false',
                        dest='draw',
                        default=True,
                        help='Do not actually draw the graph')
    parser.add_argument('--live', action='store_true',
                        help='Input is a flat collection of aa/ac files)')

    # TODO: would be nice to enforce these groups of args mutually excluding
    # but not sure if the library actually supports it
    psr_rel = parser.add_argument_group("relation graphs")
    psr_rel.add_argument('--split', action='store_true',
                         help='Separate file for each connected component')
    psr_rel.add_argument('--strip-cdus', action='store_true',
                         help='Strip away CDUs (substitute w heads)')

    psr_enc = parser.add_argument_group("enclosure graphs")
    psr_enc.add_argument('--enclosure', action='store_true',
                         help='Generate enclosure graphs')
    psr_enc.add_argument('--reduce', action='store_true',
                         help='Reduce enclosure graphs [requires --enclosure]')
    psr_enc.add_argument('--tokens', action='store_true',
                         help='Include pos-tagged tokens')


    educe_group = parser.add_argument_group('corpus filtering arguments')
    educe.util.add_corpus_filters(educe_group,
                                  fields=['doc', 'subdoc', 'annotator'])
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    if args.enclosure:
        _main_enclosure_graph(args)
    else:
        _main_rel_graph(args)

# vim: syntax=python:
