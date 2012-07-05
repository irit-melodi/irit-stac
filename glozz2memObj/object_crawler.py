#!/usr/bin/python
# -*- coding: utf-8 -*-

from annotation_objects import *
from XML_STAC_parser import XML_STAC_parser
from object_generator import *

class Object_crawler(object):
	def __init__(self, text_file, u_annot_file = None, d_annot_file = None):
		if u_annot_file != None:
			_Edu_parse = XML_STAC_parser().parse_edu_Glozz_XML(u_annot_file, text_file)
		else:
			_Edu_parse = (None, [], [], [], [], [], [])
		if d_annot_file != None:
			_Discourse_parse = XML_STAC_parser().parse_discourse_Glozz_XML(d_annot_file, text_file)
		else:
			_Discourse_parse = ([], [], [], [])
		self.__Object_generator = ObjectGenerator(_Edu_parse, _Discourse_parse)
	def get_edus(self):
		return self.__Object_generator.generate_edu_Game()
	def get_discourse(self):
		return self.__Object_generator.generate_discourse_structures()


