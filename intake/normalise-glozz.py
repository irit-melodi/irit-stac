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

class NormSettings(object):
    def __init__(self, mode, start):
        self.mode  = mode
        self.start = start

default_settings = NormSettings('count', 1)

def mk_new_dates(dates, settings=default_settings):
    start        = settings.start
    unique_dates = nub(dates)

    if settings.mode == 'zero':
        return { str(v):'0' for v in unique_dates    }
    if settings.mode == 'negonly':
        # only normalise negative dates (in count mode)
        pos_dates = filter(lambda x:x >= 0, unique_dates)
        neg_dates = filter(lambda x:x <  0, unique_dates)
        pos_dict = { str(v):str(v)  for v in pos_dates }
        neg_dict = { str(v):str(-i) for i,v in enumerate(neg_dates, start) }
        return dict(pos_dict.items() + neg_dict.items())
    else:
        return { str(v):str(i) for i,v in enumerate(unique_dates, start) }


def tidy(filename, output, mode=None):
    tree    = ET.parse(filename)

    date_elems = tree.findall('.//creation-date')
    unit_elems = tree.findall('.//*[@id]')

    dates     = [ int(x.text.strip()) for x in date_elems ]
    unit_ids  = [ x.attrib['id'] for x in unit_elems ]

    new_dates = mk_new_dates(dates, mode)

    def adjust_id(x):
        xparts = x.rsplit('_', 1)
        date2  = new_dates[xparts[-1]]
        return '_'.join(xparts[:-1] + [date2])

    new_ids = { x:adjust_id(x) for x in unit_ids }

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
arg_parser.add_argument('--mode', choices=[ 'count', 'zero', 'negonly' ],
                        help='Normalisation mode'
                       )
arg_parser.add_argument('--start', type=int, default=1, help='start indices from')

arg_parser.add_argument('--verbose', '-v', action='store_true')
args=arg_parser.parse_args()

if not os.path.exists(args.output): os.mkdir(args.output)

settings = NormSettings(args.mode, args.start)

for f in args.input:
    f2 = os.path.join(args.output, os.path.basename(f))
    tidy(f, f2, settings)
