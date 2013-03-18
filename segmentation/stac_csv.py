"""
STAC CSV format

NB: I never quite figured out how to match the output from
STAC. It's as though we were deliberately wrapping the text
in quotes before passing them to the library to write, which
seems a bit odd...

The format we output instead is a bit more regular though, so
maybe that's good?
"""

# Author: Eric Kow
# License: BSD3

import csv
import sys

stac_csv_fields = ['ID', 'Timestamp', 'Emitter', 'Resources', 'Buildups', 'Text', 'Annotation', 'Comment']
csv.register_dialect('stac', delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)

def mk_plain_writer(outfile):
    return csv.writer(outfile, dialect='stac')

def mk_writer(writer):
    return csv.DictWriter(writer, stac_csv_fields, dialect='stac')
