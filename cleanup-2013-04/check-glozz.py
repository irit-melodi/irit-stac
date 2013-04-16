#!/usr/bin/env python
# Author: Eric Kow
# License: BSD3

"""
Check that all creation dates in a glozz file are unique.
(Glozz seems to rely on them to distinguish annotations)
"""

import xml.etree.ElementTree as ET
import collections
import sys

def print_repeats(f,descr,xs):
    reps = [ k for k,v in collections.Counter(xs).items() if v > 1 ]
    if len(reps) > 0:
        print "%s has repeated %s: %s" % (f, descr, ' '.join(reps))

for filename in sys.argv[1:]:
    tree    = ET.parse(filename)
    dates   = [ x.text for x in tree.findall('.//creation-date') ]
    ids     = [ x.attrib['id'] for x in tree.findall('.//unit')  ]
    print_repeats(filename,'creation-dates',dates)
    print_repeats(filename,'ids', ids)
