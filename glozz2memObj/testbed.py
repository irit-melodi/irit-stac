#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from corpus_reader import *
from unit_iterator import *

# initializes a corpus reader.
# We need to input the working directory and the annotation type: u or d.

corpus = Corpus_reader(sys.argv[1], sys.argv[2])

# calls the reader iterator, to get a generator which allows us to get game annotations (if sys.argv[2] == 'u') or discourse annotations (if sys.argv[2] == 'd') one by one.

r = corpus.reader()

# iterates on the generator, to get a document-level annotation one by one.
#r.next()
#r.next()
#g = r.next()

#for g in r:
#	print g.Annotator

# we play with each document-level annotation, depending on its type.

#print g.Dialogues[1].Turns[1].Segments[0].Text

#print g[1].Full_Discourse_units[-1]


## Work in progress: iterator for getting all the EDUs in a given corpus !! Doesn't work smoothly for CDUs, since the user needs to check on the unit's type and, if it's a CDU, to further iterate on its sub-units!!

# calls the unit iterator, which provides an object on which several getters can be applied: unit-level, relation-level, schema-level etc.
seg_it = Unit_iterator(corpus)

# call the getter, for EDUs only!! Works well for getting EDUs out of the EDU-level annotation. But for the discourse-level annotation, we only get the shallowest discourse units, be them EDUs or CDUs. So, for the time being, the user needs to check the unit types.

#units = seg_it.unit_getter('Strategic_comment')

relations = seg_it.relation_getter('Acknowledgement')

# play with the generator which contains the discourse units; instead of printing, we can also very well inspect its inner object structure.
#for u in units:
#	print u#[0].Text #(u[0].ID, u[1])

for rel in relations:
	print rel

