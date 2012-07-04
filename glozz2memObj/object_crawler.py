#!/usr/bin/python
# -*- coding: utf-8 -*-
# We should be doing it bottom up, from the most detailed classes to the most "enclosing" ones!

from annotation_objects import *
from XML_STAC_parser import XML_STAC_parser
from object_generator import *

class Object_crawler(object):
	def __init__(self, u_annot_file, d_annot_file, text_file):
		_Edu_parse = XML_STAC_parser().parse_edu_Glozz_XML(u_annot_file, text_file)
		_Discourse_parse = XML_STAC_parser().parse_discourse_Glozz_XML(d_annot_file, text_file)
		self.__Object_generator = ObjectGenerator(_Edu_parse, _Discourse_parse)
	def get_edus(self):
		return self.__Object_generator.generate_edu_Game()
	def get_discourse(self):
		return self.__Object_generator.generate_discourse_structures()


