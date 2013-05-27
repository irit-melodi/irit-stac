#!/usr/bin/python
# -*- coding: utf-8 -*-

# author: PM
"""
takes as input a csv report on a stac game
and use manually inserted newlines as a clue
to generate multiple smaller files (as glozz can only deal with small files)
usage: 
python split_files.py toto.csv

output toto1.csv, toto2.csv, etc (in same dir as original file)
"""

import sys
import os.path
import csv  # only for use with quoted lines corner case

infile = open(sys.argv[1]).readlines()
base, ext = os.path.splitext(sys.argv[1])

count = 1
header = infile[0].strip()
nb = len(infile)
current = [header]

def awkward(line):
    """
    There is the odd case where an entire row appears to have been
    quoted; what's tricky about these is that text with quotation
    marks in its will be escaped.
    luckily, csvreader in Python reads any iterator, so we can just give
    it a singleton list and write it back out
    """
    reader  = csv.reader([line]) # should just read as a big single-cell row
    try:
        [line2]  = reader.next()
    except ValueError:
        print >> sys.stderr, "Bug: was expecting this line to be interpreted as a single column"
        print >> sys.stderr, line
        raise

    return line2

def chomped(line):
    return line.rstrip('\r\n') # only remove newlines; tabs are significant

for (i,line) in enumerate(infile[1:]):
    line = chomped(line)
    if len(line) > 1 and line[0] == '"' and line[-1] == '"':
        line = chomped(awkward(line))

    if line.strip()=="" or i==nb-2:
        outf = open("%s%02d%s"%(base,count,ext),"w")
        if i==nb-2:
            current.append(line)
        for one in current:
            print >> outf, one
        outf.close()
        current = [header]
        count = count +1
    else:
        current.append(line)
