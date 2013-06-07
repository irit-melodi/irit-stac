#!/usr/bin/env python
# Author: Eric Kow
# License: BSD3

"""
Normalise ids, timestamps and whitespace in a Glozz XML file
"""

import argparse
import xml.etree.ElementTree as ET
import collections
import os
import sys

from prettifyxml import prettify

def nub(xs):
    """
    First occurrence of each list member
    """
    ys = []
    for x in xs:
        if x not in ys: ys.append(x)
    return ys

def tidy(filename, output):
    tree    = ET.parse(filename)

    date_elems = tree.findall('.//creation-date')
    unit_elems = tree.findall('.//*[@id]')

    dates     = [ int(x.text.strip()) for x in date_elems ]
    unit_ids  = [ x.attrib['id'] for x in unit_elems ]

    new_ids  ={ v:str(i)      for i,v in enumerate(nub(unit_ids)) }
    new_dates={ str(v):str(i) for i,v in enumerate(nub(dates))    }

    for x in date_elems:
        old    = str(x.text.strip())
        x.text = new_dates[old]
    for x in unit_elems:
        old = x.attrib['id']
        x.attrib['id'] = new_ids[old]

    with open(output, 'w') as ofile:
        ofile.write(prettify(tree.getroot()))

# ---------------------------------------------------------------------
# options
# ---------------------------------------------------------------------

arg_parser = argparse.ArgumentParser(description='Normalise a Glozz XML file; not for production use!')
arg_parser.add_argument('input', metavar='FILES'
                       , nargs = '+'
                       )
arg_parser.add_argument('--output', metavar='DIR'
                       , action='store'
                       , required=True
                       , help='Output directory'
                       )
arg_parser.add_argument('--verbose', '-v', action='store_true')
args=arg_parser.parse_args()

if not os.path.exists(args.output): os.mkdir(args.output)

for f in args.input:
    f2 = os.path.join(args.output, os.path.basename(f))
    tidy(f, f2)
