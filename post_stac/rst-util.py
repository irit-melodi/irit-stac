#!/usr/bin/env python

import argparse
import codecs
import collections
import os
import sys
import xml.etree.ElementTree as ET
import cStringIO as StringIO

from educe import rst_dt, glozz
from educe.rst_dt import annotation, sdrt, graph, deptree
import educe.rst_dt.parse

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


def write_glozz(gdoc, path_stub):
    ac_path = path_stub + '.ac'
    aa_path = path_stub + '.aa'

    gdoc_bytes = gdoc.text().encode('utf-8')
    with open(ac_path, 'wb') as ac_f:
        ac_f.write(gdoc_bytes)

    gdoc.hashcode = glozz.hashcode(StringIO.StringIO(gdoc_bytes))
    glozz.write_annotation_file(aa_path, gdoc)


def render(gr, path_stub):
    dot_g = graph.DotGraph(gr)

    dot_path = path_stub + '.dot'
    png_path = path_stub + '.png'
    with codecs.open(dot_path, 'w', encoding='utf-8') as f:
        print >> f, dot_g.to_string()
    os.system('dot -T png -o %s %s' % (png_path, dot_path))

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

Counts = collections.namedtuple('Counts', "multi mono")


def empty_counts():
    return Counts(collections.defaultdict(int),
                  collections.defaultdict(int))


def walk_and_count(tree, counts):
    if tree.node.is_nucleus():
        counts.multi[tree.node.rel.lower()] += 1
    elif tree.node.is_satellite():
        counts.mono[tree.node.rel.lower()] += 1
    for child in tree:
        if not isinstance(child, educe.rst_dt.parse.EDU):
            walk_and_count(child, counts)
    return

def print_counts(counts):
    multi_and_mono = [rel for rel in counts.mono if rel in counts.multi]
    mono_only = [rel for rel in counts.mono if rel not in multi_and_mono]
    multi_only = [rel for rel in counts.multi if rel not in multi_and_mono]

    print ""
    print "Both Mono and multinuclear"
    print "--------------------------"
    for rel in multi_and_mono:
        print "%30s %5d mono, %5d multi" % (rel, counts.mono[rel], counts.multi[rel])


    print "Mononuclear only"
    print "----------------"
    for rel in mono_only:
        print "%30s %5d mono" % (rel, counts.mono[rel])

    print ""
    print "Multinuclear only"
    print "-----------------"
    for rel in multi_only:
        print "%30s %5d multi" % (rel, counts.multi[rel])


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def do_transform(args, corpus):

    bef_dir = os.path.join(args.output, "before")
    aft_dir = os.path.join(args.output, "after")
    if not os.path.exists(bef_dir):
        os.makedirs(bef_dir)
    if not os.path.exists(aft_dir):
        os.makedirs(aft_dir)
    for k in corpus:
        before = corpus[k]
        after = annotation._binarize(before)
        if not annotation.is_binary(after):
            print k.doc,\
                transform.is_binary(before),\
                transform.is_binary(after)
        with open(os.path.join(bef_dir, k.doc), "w") as fout:
            print >> fout, "#", k
            print >> fout, corpus[k]
            print >> fout
        with open(os.path.join(aft_dir, k.doc), "w") as fout:
            print >> fout, "#", k
            print >> fout, annotation.binarize(corpus[k])
            print >> fout


#    with open(os.path.join(args.output, "simple.rst"), "w") as fout:
#        for k in corpus:
#            print >> fout, "#", k
#            print >> fout, transform.SimpleRSTTree.from_rst_tree(corpus[k])
#            print >> fout


def main():
    arg_parser = argparse.ArgumentParser(description='RST toy/example')
    arg_parser.add_argument('input',  metavar='DIR', help='RST directory')
    arg_parser.add_argument('output', metavar='DIR', help='output directory')
    args = arg_parser.parse_args()

    odir = args.output
    if not os.path.exists(odir):
        os.makedirs(odir)

    reader = rst_dt.Reader(args.input)
    anno_files = reader.files()
    corpus = reader.slurp_subcorpus(anno_files, True)
    gcorpus = {}
    #do_transform(args, corpus)

    counts = empty_counts()
    for k in corpus:
        walk_and_count(corpus[k], counts)

    # relations that we will treat as multinuclear
    multinuclearish = [rel for rel, count in counts.multi.items()
                       if count >= counts.mono.get(rel, 0)]
    print "Treating as multi-nuclear: ", multinuclearish

    bin_dir = os.path.join(args.output, "rst-binarised")
    dt_dir = os.path.join(args.output, "rst-to-dt")
    rst2_dir = os.path.join(args.output, "dt-to-rst")
    for subdir in [bin_dir, dt_dir, rst2_dir]:
        if not os.path.exists(subdir):
            os.makedirs(subdir)
    for k in corpus:
        suffix = os.path.splitext(k.doc)[0]
        stree = educe.rst_dt.SimpleRSTTree.from_rst_tree(corpus[k])
        with open(os.path.join(bin_dir, suffix), 'w') as fout:
            fout.write(str(stree))
        dtree = deptree.relaxed_nuclearity_to_deptree(stree)
        with open(os.path.join(dt_dir, suffix), 'w') as fout:
            fout.write(str(dtree))
        stree2 = deptree.relaxed_nuclearity_from_deptree(dtree, multinuclearish)
        with open(os.path.join(rst2_dir, suffix), 'w') as fout:
            fout.write(str(stree2))

main()
