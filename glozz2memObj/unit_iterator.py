#!/usr/bin/python
# -*- coding: utf-8 -*-

class Unit_iterator(object):
	def __init__(self, corpus):
		self.__Corpus = corpus
	def unit_getter(self, unit_type):
		if unit_type == 'edu':
			if self.__Corpus.Annotation_type == 'u':
				# get all Offer/Counteroffer/etc units
				_segs = ((seg, dial.ID) for rc in self.__Corpus.reader() for dial in rc.Dialogues for turn in dial.Turns for seg in turn.Segments)
				return _segs
			if self.__Corpus.Annotation_type == 'd':
				# get all Segment units
				# Only gets the shallowest subunits; hence, a check on their type is needed to determine whether they are CDUs or not!
				_segs = ((du, ds.ID) for rc in self.__Corpus.reader() for ds in rc for du in ds.Full_Discourse_units)
				return _segs



