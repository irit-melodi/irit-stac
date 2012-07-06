#!/usr/bin/python
# -*- coding: utf-8 -*-

from corpus_reader import *

class Unit_iterator(object):
	'''
	Given a corpus iterator, it retrieves units and relations. 
	To this end, an iterator is created, allowing one to get the
	set of either of:
	-- all units of a specified type in the corpus, 
	-- or all discourse relations of a specified type in the corpus,
	-- or all units which are left arguments, or right arguments,
	   of a discourse relation of a specified type or of any type.
	'''
	def __init__(self, corpus):
		'''
		Initialize the private __Corpus attribute.
		@param: corpus: Corpus_reader instance.
		'''
		self.__Corpus = corpus
	def unit_getter(self, unit_type):
		'''
		Iterator on annotation units, i.e. entities that 
		have a span and hence a text associated to them.
		It retrieves all units of a specified type in 
		a corpus specified when initializing its parent object.
		@param: unit_type: type of the unitsto be retrieved 
			from the corpus.
		'''
		if unit_type == 'edu':
			if self.__Corpus.Annotation_type in ['u', 'p']:
				# get all Offer/Counteroffer/etc units
				_segs = ((seg, rc.Annotator) for rc in self.__Corpus.reader() for dial in rc.Dialogues for turn in dial.Turns for seg in turn.Segments)
				return _segs
			elif self.__Corpus.Annotation_type == 'd':
				# get all Segment units
				# Only gets the shallowest subunits; hence, a check on their type is needed to determine whether they are CDUs or not!
				_segs = ((du, ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for du in ds.Full_Discourse_units)
				return _segs
			else:
				raise TypeError("Error: unknown annotation type!")
		if unit_type in ['Offer', 'Counteroffer', 'Accept', 'Refusal', 'Strategic_comment', 'Other']:
			if self.__Corpus.Annotation_type == 'u':
				_segs = ((seg, rc.Annotator) for rc in self.__Corpus.reader() for dial in rc.Dialogues for turn in dial.Turns for seg in turn.Segments if type(seg).__name__ == unit_type)
				return _segs
			elif self.__Corpus.Annotation_type in ['p', 'd']:
				raise AttributeError("Error: cannot retrieve %(Act)ss from this kind of annotation!" % {'Act': unit_type})
			else:
				raise TypeError("Error: unknown annotation type!")
		elif unit_type == 'res':
			if self.__Corpus.Annotation_type == 'u':
				_res = ((res, rc.Annotator) for rc in self.__Corpus.reader() for dial in rc.Dialogues for turn in dial.Turns for seg in turn.Segments if type(seg).__name__ != 'Segment' for res in seg.Resources)
				return _res
			elif self.__Corpus.Annotation_type in ['d', 'p']:
				raise AttributeError("Error: cannot retrieve Resources from this kind of annotation!")
			else:
				raise TypeError("Error: unknown annotation type!")
		elif unit_type == 'mures':
			if self.__Corpus.Annotation_type == 'u':
				_mures = ((res, rc.Annotator) for rc in self.__Corpus.reader() for dial in rc.Dialogues for turn in dial.Turns for seg in turn.Segments if type(seg).__name__ != 'Segment' for res in seg.Resources if type(res).__name__ == 'Several_resources')
				return _mures
			elif self.__Corpus.Annotation_type in ['d', 'p']:
				raise AttributeError("Error: cannot retrieve Complex resources from this kind of annotation!")
			else:
				raise TypeError("Error: unknown annotation type!")
		elif unit_type == 'pref':
			if self.__Corpus.Annotation_type == 'u':
				_pref = ((pref, rc.Annotator) for rc in self.__Corpus.reader() for dial in rc.Dialogues for turn in dial.Turns for seg in turn.Segments if type(seg).__name__ != 'Segment' for pref in seg.Preferences)
				return _pref
			elif self.__Corpus.Annotation_type in ['d', 'p']:
				raise AttributeError("Error: cannot retrieve Preferences from this kind of annotation!")
			else:
				raise TypeError("Error: unknown annotation type!")
		elif unit_type == 'cdu':
			if self.__Corpus.Annotation_type == 'd':
				_segs = ((du, ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for du in ds.Full_Discourse_units if type(du).__name__ == 'Complex_segment')
				return _segs
			if self.__Corpus.Annotation_type in ['u', 'p']:
				raise AttributeError("Error: cannot retrieve Complex segments from this kind of annotation!")
		else:
			raise TypeError("Error: unknown unit type: %(Utype)s!" % {'Utype': unit_type})

	def relation_getter(self, rel_type = None):
		'''
		Iterator on relations, i.e. entities that 
		have a pair of units associated to them.
		It retrieves all relations of any type 
		or all relations of a specified type 
		in a corpus specified when initializing 
		the parent object of this method.
		@param: rel_type: type of the relations
			to be retrieved from the corpus.
			Can be missing, in which case all
			relations are retrieved.
		'''
		if self.__Corpus.Annotation_type == 'd':
			if rel_type != None:
				_rels = ((rel.Label, (rel.Full_Left_argument, rel.Full_Right_argument), ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for rel in ds.Full_Discourse_relations if rel.Label == rel_type)
			else:
				_rels = ((rel.Label, (rel.Full_Left_argument, rel.Full_Right_argument), ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for rel in ds.Full_Discourse_relations)
			return _rels

	def left_arg_getter(self, rel_type = None):
		'''
		Iterator on units which are left arguments of a relation.
		It retrieves all such units, for relations of any type 
		or for all relations of a specified type 
		in a corpus specified when initializing 
		the parent object of this method.
		@param: rel_type: type of the relations whose left arguments
			are to be retrieved from the corpus.
			Can be missing, in which case left arguments of all
			relations are retrieved.
		'''
		if self.__Corpus.Annotation_type == 'd':
			if rel_type != None:
				_largs = ((rel.Full_Left_argument, ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for rel in ds.Full_Discourse_relations if rel.Label == rel_type)
			else:
				_largs = ((rel.Full_Left_argument, ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for rel in ds.Full_Discourse_relations)
			return _largs

	def right_arg_getter(self, rel_type = None):
		'''
		Iterator on units which are right arguments of a relation.
		It retrieves all such units, for relations of any type 
		or for all relations of a specified type 
		in a corpus specified when initializing 
		the parent object of this method.
		@param: rel_type: type of the relations whose right arguments
			are to be retrieved from the corpus.
			Can be missing, in which case right arguments of all
			relations are retrieved.
		'''
		if self.__Corpus.Annotation_type == 'd':
			if rel_type != None:
				_rargs = ((rel.Full_Right_argument, ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for rel in ds.Full_Discourse_relations if rel.Label == rel_type)
			else:
				_rargs = ((rel.Full_Right_argument, ds.Annotator) for rc in self.__Corpus.reader() for ds in rc for rel in ds.Full_Discourse_relations)
			return _rargs
		

