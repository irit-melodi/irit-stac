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


infile = open(sys.argv[1]).readlines()
base, ext = os.path.splitext(sys.argv[1])

count = 1
header = infile[0].strip()
nb = len(infile)
current = [header]

for (i,line) in enumerate(infile[1:]):
    if line.strip()=="" or i==nb-2:
        outf = open("%s%d%s"%(base,count,ext),"w")
        if i==nb-2:
            current.append(line.strip())
        for one in current:
            print >> outf, one
        outf.close()
        current = [header]
        count = count +1
    else:
        current.append(line.strip())
