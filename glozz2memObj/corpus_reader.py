#!/usr/bin/python
# -*- coding: utf-8 -*-
from object_crawler import *

# Provide an iterator here, on the annotations
# Starting from a given directory, navigate through its structure and crawl for:
# (basename.ac, basename_author_u_date.aa, basename_author_d_date.aa)
# for each such tuple generate an Object_crawler instance and initialize an iterator (aka Python generator) on Game objects (EDU-level) and 
# lists of Discourse_structure objects (discourse-level).
# From there on, we can just iterate :
# 'p' stands for "preannotation", hence basename.aa, which only contains the pre-annotations.

from object_crawler import *

class Corpus_reader(object):
	'''
	Given a directory path and an annotation type, it creates an iterator 
	on the set of files found in the directory.
	The set of files is represented as a tuple (text file, annotation file), 
	where 'annotation file' is parameterized according to the annotation type.
	'''
	def __init__(self, dir, anntype):
		'''
		Initialize the absolute path of the directory and the annotation type.
		@param: dir: used to initialize the private __Path attribute.
		@param: anntype: used to initialize the private __Annotation_type attribute.
			Can be either one of: 'p' for a pre-annotation, 'u' for an EDU-level
			annotation, or 'd' for a discourse-level one.
		'''
		import os
		self.__Path = os.path.abspath(dir)
		del os
		self.__Annotation_type = anntype
	@property
	def Annotation_type(self):
		'''
		Public accessor to the private __Annotation_type attribute.
		'''
		return self.__Annotation_type
	def reader(self):
		'''
		Instance method which actually creates the corpus iterator.
		It uses the Path and the Annotation type to iterate on (text, annotation) tuples.
		According to the annotation type, 'annotation' can be either one of: 
		preannotation (à la STAC), EDU-level annotation, discourse-level annotation.
		Then, according to the annotation type, either one of two iterators is created:
		-- for pre-annotations or EDU-level annotations, an iterator on Game objects is created.
		-- for discourse-level annotations, an iterator on lists of Discourse_structure objects is created;
		   for each discourse annotated document, such a list is retrievable. Such a list contains one 
		   Discourse_structure object per Dialogue (object).
		'''
		if self.__Annotation_type not in ['u', 'd', 'p']:
			raise TypeError("Unknown annotation type!")
		tb = annb = []
		import commands, os
		tb = commands.getoutput("ls " + self.__Path + "/*.ac").split('\n')
		if self.__Annotation_type == 'p':
			annb = commands.getoutput("find " + self.__Path + " \( ! -iname '*_[ud]_*' \) -print | grep '.aa'").split('\n')
		else:
			annb = commands.getoutput("ls " + self.__Path + "/*_"+ self.__Annotation_type +"_*.aa").split('\n')
		del commands
		import itertools
		for (text_file, annot_file) in itertools.izip_longest(tb, annb):
			if text_file != None: 
				tstem = os.path.basename(text_file).replace('__', '_').split('.')[0]
			else:
				tstem = ''
			if annot_file != None: 
				if self.__Annotation_type != 'p':
					annstem = os.path.basename(annot_file).replace('__', '_').rsplit('_', 3)[0]
				if self.__Annotation_type == 'p':
					annstem = os.path.basename(annot_file).replace('__', '_').split('.')[0]
			else:
				annstem = ''
			if tstem == annstem:
				if self.__Annotation_type in ['u', 'p']:
					object_annot = Object_crawler(text_file, annot_file)
					_game = object_annot.get_edus()
					yield _game
				if self.__Annotation_type == 'd':
					object_annot = Object_crawler(text_file, None, annot_file)
					_discourse_structures = object_annot.get_discourse()
					yield _discourse_structures
			else:
				raise IOError("Error: Problem accessing annotation for document %(annot)s" % {'annot': text_file})

