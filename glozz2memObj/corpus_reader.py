#!/usr/bin/python
# -*- coding: utf-8 -*-
from object_crawler import *

# Provide an iterator here, on the annotations
# Starting from a given directory, navigate through its structure and crawl for:
# (basename.ac, basename_author_u_date.aa, basename_author_d_date.aa)
# for each such tuple generate an Object_crawler instance and initialize an iterator (aka Python generator) on Game objects (EDU-level) and 
# lists of Discourse_structure objects (discourse-level).
# From there on, we can just iterate :

from object_crawler import *

class Corpus_reader(object):
	def __init__(self, dir, anntype):
		import os
		self.__Path = os.path.abspath(dir)
		del os
		self.__Annotation_type = anntype
	@property
	def Annotation_type(self):
		return self.__Annotation_type
	def reader(self):
		if self.__Annotation_type not in ['u', 'd']:
			raise TypeError("Unknown annotation type!")
		tb = annb = []
		import commands, os
		tb = commands.getoutput("ls " + self.__Path + "/*.ac").split('\n')
		annb = commands.getoutput("ls " + self.__Path + "/*_"+ self.__Annotation_type +"_*.aa").split('\n')
		del commands
		import itertools
		for (text_file, annot_file) in itertools.izip_longest(tb, annb):
			if text_file != None: 
				tstem = os.path.basename(text_file).replace('__', '_').split('.')[0]
			else:
				tstem = ''
			if annot_file != None: 
				annstem = os.path.basename(annot_file).replace('__', '_').rsplit('_', 3)[0]
			else:
				annstem = ''
			if tstem == annstem:
				if self.__Annotation_type == 'u':
					object_annot = Object_crawler(text_file, annot_file)
					_game = object_annot.get_edus()
					yield _game
				if self.__Annotation_type == 'd':
					object_annot = Object_crawler(text_file, None, annot_file)
					_discourse_structures = object_annot.get_discourse()
					yield _discourse_structures
			else:
				raise IOError("Error: Problem accessing annotation for document %(annot)s" % {'annot': text_file})

