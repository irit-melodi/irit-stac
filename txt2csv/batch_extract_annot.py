#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The purpose of this small program is to:
	- iterate on a set of cleaned-up soclog files;
	- call the program which extracts the CSV files from these cleaned-up soclogs,
	- print out the file names of the documents, along with their number of turns and of 'linguistic' turns, i.e.,
	with the Server's turns excluded.

Usage:
>>> ./batch_extract_annot.py

@note: The program assumes a Linux environment and that all the files start with 'pilot' and end with '.txt'.
Any change of this state of affairs should be done on line 19.
"""
import commands, itertools, collections
import extract_annot

filenames, sizes, linguistic_sizes = [], [], []
for filename in commands.getoutput("ls pilot*.txt").split('\n'):
	dump = extract_annot.wikitext2csv(filename)
	sizes.append(int(dump[0]))
	linguistic_sizes.append(int(dump[1]))
	filenames.append(filename)

print ["Dialogue", "Total number of turns", "Total number of linguistic turns"]

'''To be put in a dedicated module (and class), utils !
'''
files_hash={}
for i in range(0,len(filenames)):
	#print [filenames[i], sizes[i], linguistic_sizes[i]]
	files_hash[zip(filenames, sizes)[i]] = linguistic_sizes[i]
sorted_hash = sorted(files_hash, key=files_hash.get, reverse = True)
for i in range(0,len(sorted_hash)):
	print [sorted_hash[i], files_hash[sorted_hash[i]]]
