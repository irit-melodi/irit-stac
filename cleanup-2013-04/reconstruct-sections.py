#!/usr/bin/env python

"""
Given a directory of section files and a soclog.seg.csv with
only segments but no sectioning info, write to stdout
a variant of the soclog.seg.csv with sections

The section files are assumed to start with a header.

This is partly an archeaological exercise.

We don't know where the sectioning information really lives,
(but we have the output in the form of multiple csv files;
was this done by hand perhaps?), but it's certainly enough
for us to reconstruct something our scripts would use.

This doesn't have to know about the format of the files,
other than they are line-delimited
"""

import itertools
import glob
import math
import os
import re
import sys
import argparse
from itertools import chain

# ---------------------------------------------------------------------
# options
# ---------------------------------------------------------------------

arg_parser = argparse.ArgumentParser(description='Reconstruct sectioning of a CSV file')
arg_parser.add_argument('unsectioned', metavar='FILE'
                       , help='file name'
                       , default='soclog.seg.csv file'
                       )
arg_parser.add_argument('sections', metavar='DIR'
                       , action='store'
                       , help='directory of files'
                       )
arg_parser.add_argument('--output','-o', metavar='FILE'
                       , action='store'
                       , help='output file [stdout if not supplied]'
                       )
arg_parser.add_argument('--verbose', '-v', action='store_true')
args=arg_parser.parse_args()

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def cut_file(cuts, f, ostream):
    header = f.next()
    first  = f.next()
    eol    = f.newlines
    ostream.write(header)
    ostream.write(first)
    for line in f:
        if line in cuts:
            ostream.write(eol) # hmm should really detect line ending type
        ostream.write(line)


cuts = set([])
for fname in os.listdir(args.sections):
    with open(os.path.join(args.sections, fname)) as f:
        f.next() # header
        cuts.add(f.next())

with open(args.unsectioned,'U') as f:
    if args.output:
        with open(args.output, 'w') as ostream:
           cut_file(cuts, f, ostream)
    else:
        cut_file(cuts, f, sys.stdout)


