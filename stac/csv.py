# Author: Eric Kow
# License: BSD3

"""
STAC project CSV files

STAC uses CSV files for some intermediary steps when initially
preparing data for annotation.  We don't expect these to be
useful outside of that particular context
"""

from __future__ import absolute_import
import csv

csv_headers = [ 'ID'
              , 'Timestamp'
              , 'Emitter'
              , 'Resources'
              , 'Buildups'
              , 'Text'
              , 'Annotation'
              , 'Comment'
              ]
"""
Fields used in intermediary CSV format for preprocessing
"""

csv.register_dialect('stac', csv.excel_tab)

def mk_plain_csv_writer(outfile):
    """
    Just writes records in stac dialect
    """
    return csv.writer(outfile, dialect='stac')

class Utf8DictWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in UTF-8.
    """

    def __init__(self, f, headers, dialect=csv.excel, **kwds):
        b_headers   = [ s.encode('utf-8') for s in headers ]
        self.writer = csv.DictWriter(f, b_headers, dialect=dialect, **kwds)

    def writeheader(self):
        self.writer.writeheader()

    def writerow(self, row):
        def b(x):
            if isinstance(x, basestring):
                return unicode(x).encode('utf-8')
            else:
                return x
        self.writer.writerow(dict([(b(k),b(v)) for k,v in row.items()]))

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

class Utf8DictReader:
    """
    A CSV reader which assumes strings are encoded in UTF-8.
    """

    def __init__(self, f, **kwds):
        self.reader = csv.DictReader(f, **kwds)

    def next(self):
        def u(x):
            if isinstance(x, basestring):
                return unicode(x, 'utf-8')
            else:
                return x

        row = self.reader.next()
        return dict([(u(k), u(v)) for k,v in row.items()])

    def __iter__(self):
        return self

def mk_csv_writer(ofile):
    """
    Writes dictionaries.
    See `csv_headers` for details
    """
    return Utf8DictWriter(ofile, csv_headers, dialect='stac')

def mk_csv_reader(infile):
    """
    Assumes UTF-8 encoded files.
    Reads into dictionaries with Unicode strings.

    See `Utf8DictReader` if you just want a generic UTF-8 dict
    reader, ie. not using the stac dialect
    """
    return Utf8DictReader(infile, dialect='stac')
