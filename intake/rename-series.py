#!/usr/bin/env python

"""
Rename a numbered sequence of files in a way that is friendlier to new
conventions

1. We pad the digits with zeros to highest order of magnitude
   so that naive lexicographical ordering works

2. We move the digits before any extensions

As an example

   f.foo1.ext f.foo2.ext .. f.foo342.ext

becomes

   f_001.foo.ext f_002.foo.ext f_003.foo.ext

Input should be a template, so for the above example:

   rename-series f.foo.ext

"""

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

arg_parser = argparse.ArgumentParser(description='Rename sequence of files.')
arg_parser.add_argument('pattern', metavar='FILENAME'
                       , help='file name pattern'
                       )
arg_parser.add_argument('--verbose', '-v', action='store_true')
arg_parser.add_argument('--dry-run', '-n', action='store_true')
args=arg_parser.parse_args()

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

(pattern_bname, pattern_ext) = os.path.splitext(args.pattern)
pattern_glob   = pattern_bname + '[0-9]*' + pattern_ext
pattern_pieces = pattern_bname.split(os.extsep)

output_prefix = pattern_pieces[0]
output_ext    = os.extsep.join(pattern_pieces[1:]) + pattern_ext

files = list(glob.glob(pattern_glob))
size   = len(files)
if size > 0:
    digits = int(math.ceil(math.log10(size)))
else:
    digits = 0

if args.verbose:
    output_template = '%s_%s.%s' % (output_prefix, 'X' * digits, output_ext)
    msgs =\
        [ 'Pattern   %s [%d matches]' % (pattern_glob, size)
        , 'Saving to %s [%d digits]'  % (output_template, digits)
        ]
    print >> sys.stderr, "\n".join(msgs)

def new_name(f):
    strip_len = len(pattern_bname)
    suffix    = os.path.splitext(f)[0][strip_len:]
    return '%s_%s.%s' % (output_prefix, suffix.zfill(digits), output_ext)

for f in files:
    f2 = new_name(f)
    if args.dry_run or args.verbose:
        print >> sys.stderr, "%s\t-> %s" % (f,f2)

    if not args.dry_run:
        os.rename(f, f2)

if args.dry_run:
    print >> sys.stderr, "Dry run, so did not actually do anything"
