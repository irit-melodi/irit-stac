#!/usr/bin/python
# -*- coding: utf-8 -*-
# We should be doing it bottom up, from the most detailed classes to the most "enclosing" ones!

from xml.etree.ElementTree import ElementTree
from annotation_objects import *


class XML_STAC_parser(object):
	# EDU-level Glozz parser and internal object initializer:
	# Parse EDU-level XML and return lists
	@staticmethod
	def parse_edu_Glozz_XML(annot_file, text_file):
		dialogues = []
		turns = []
		segments = []
		resources = []
		preferences = []
		players = []
		annot = ElementTree().parse(annot_file)
		# EDU-level parsing:
		# Add "Span" for each unit:
		author_printed = False
		for i in range(0,len(annot)):
			# Selecting Glozz "unit"s:
			if annot[i].tag == 'unit':
				# Selecting "unit" metadata: author,...
				if annot[i][0].tag == 'metadata':
					if annot[i][0][0].tag == 'author' and author_printed == False:
						# For setting the Annotator attribute of Game objects
						annotation_author = annot[i][0][0].text
						author_printed = True
				# Selecting "unit" characterisation
				if annot[i][1].tag == 'characterisation':
					# Getting "unit" types (Resources, Offers, Turns etc)
					# if annot[i].getchildren()[1].getchildren()[0].text == 'Turn' | 'Offer' | etc...
					if annot[i][1][0].text == 'Dialogue':
						temp_gets = []
						temp_dice_rolls = []
						temp_exchange = None
						temp_id = annot[i].attrib['id'].split('_')[1]
						# Test for features:
						if len(annot[i][1][1]) >= 1:
							for j in range(0, len(annot[i][1][1])):
								if annot[i][1][1][j].attrib['name'] == 'Gets':
									for oneget in annot[i][1][1][j].text.split('.')[:-1]:
										temp_who = oneget.split(' gets ')[0].strip(' ')
										if 'nothing' in oneget.split(' gets ')[1]:
											temp_gets.append(Get(temp_who))
										else:
											temp_what = oneget.split(' gets ')[1].split(' ')[1]
											temp_qty = oneget.split(' gets ')[1].split(' ')[0]
											temp_res = Resource(None, temp_what, temp_qty)
											temp_gets.append(Get(temp_who, temp_res))
								elif annot[i][1][1][j].attrib['name'] == 'Dice_rolling':
									for oneroll in annot[i][1][1][j].text.split('.')[:-1]:
										temp_who = str(oneroll.split(' rolled a ')[0].strip(' '))
										temp_what = [str(oneroll.split(' rolled a ')[1].split(' and a '))[0], str(oneroll.split(' rolled a ')[1].split(' and a '))[1]]
										temp_dice_rolls.append(Die_roll(temp_who, temp_what))
								elif annot[i][1][1][j].attrib['name'] == 'Trades':
									if annot[i][1][1][j].text != None:
										for onetrade in annot[i][1][1][j].text.split('.')[:-1]:
											temp_who = str(onetrade.split(' traded ')[0])
											temp_from_whom = str(onetrade.split(' from ')[1].strip('.'))
											temp_what = str(onetrade.split(' traded ')[1].split(' for ')[0].split(' ')[1])
											temp_what_qty = onetrade.split(' traded ')[1].split(' for ')[0].split(' ')[0]
											temp_to_res = Resource(None, temp_what, temp_what_qty)
											temp_what_for = str(onetrade.split(' traded ')[1].split(' for ')[1].split(' ')[1])
											temp_what_for_qty = onetrade.split(' traded ')[1].split(' for ')[1].split(' ')[0]
											temp_from_res = Resource(None, temp_what_for, temp_what_for_qty)
											temp_exchange = Exchange(temp_from_whom, temp_who, temp_from_res, temp_to_res)
						temp_trade = Trade(temp_gets, temp_dice_rolls, temp_exchange)
						temp_start = int(annot[i][2][0][0].attrib['index'])
						temp_end = int(annot[i][2][1][0].attrib['index'])
						temp_span = Span(temp_start, temp_end)
						dialogues.append(Dialogue(temp_id, temp_span, temp_trade))
					if annot[i][1][0].text == 'Turn':
						temp_id = annot[i].attrib['id'].split('_')[1]
						# Test for features:
						temp_res = []
						temp_devs = []
						if len(annot[i][1][1]) >= 1:
							for j in range(0, len(annot[i][1][1])):
								if annot[i][1][1][j].attrib['name'] == 'Identifier':
									temp_shid = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Timestamp':
									temp_timestamp = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Emitter':
									temp_emitter = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Resources':
									# Add parsing for resources
									for res in str(annot[i][1][1][j].text).split('; '):
										temp_res.append(Resource(None, res.split('=')[0], res.split('=')[1]))
								elif annot[i][1][1][j].attrib['name'] == 'Developments':
									if annot[i][1][1][j].text != None:
										for dev in str(annot[i][1][1][j].text).split(';  '):
											temp_devs.append(Development(None, dev.split('=')[0], dev.split('=')[1]))
								elif annot[i][1][1][j].attrib['name'] == 'Comments':
									temp_comments = str(annot[i][1][1][j].text)
						temp_state = State(temp_res, temp_devs)
						temp_start = int(annot[i][2][0][0].attrib['index'])
						temp_end = int(annot[i][2][1][0].attrib['index'])
						temp_span = Span(temp_start, temp_end)
						players.append(temp_emitter)
						turns.append(Turn(temp_id, temp_span, temp_emitter, temp_timestamp, temp_shid, temp_state, temp_comments))
					if annot[i][1][0].text not in ['Turn', 'Dialogue', 'Resource', 'Preference', 'paragraph']:
						temp_edu_type = str(annot[i][1][0].text)
						temp_id = annot[i].attrib['id'].split('_')[1]
						# Test for features:
						if len(annot[i][1][1]) >= 1:
							for j in range(0, len(annot[i][1][1])):
								if annot[i][1][1][j].attrib['name'] == 'Surface_act':
									temp_sa_type = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Addressee':
									temp_recv = str(annot[i][1][1][j].text).split(', ')
						temp_start = int(annot[i][2][0][0].attrib['index'])
						temp_end = int(annot[i][2][1][0].attrib['index'])
						temp_span = Span(temp_start, temp_end)
						segments.append(eval(temp_edu_type)(temp_id, temp_span, temp_recv, temp_sa_type, text_file))
					if annot[i][1][0].text == 'Resource':
						temp_id = annot[i].attrib['id'].split('_')[1]
						# Test for features:
						if len(annot[i][1][1]) >= 1:
							for j in range(0, len(annot[i][1][1])):
								if annot[i][1][1][j].attrib['name'] == 'Status':
									temp_status = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Kind':
									temp_kind = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Quantity':
									temp_qty = str(annot[i][1][1][j].text)
								elif annot[i][1][1][j].attrib['name'] == 'Correctness':
									temp_correctness = str(annot[i][1][1][j].text)
						temp_start = annot[i][2][0][0].attrib['index']
						temp_end = annot[i][2][1][0].attrib['index']
						temp_span = Span(temp_start, temp_end)
						resources.append(VerbalizedResource(temp_id, temp_span, temp_status, temp_kind, temp_qty, text_file))
					if annot[i][1][0].text == 'Preference':
						temp_id = annot[i].attrib['id'].split('_')[1]
						temp_start = annot[i][2][0][0].attrib['index']
						temp_end = annot[i][2][1][0].attrib['index']
						temp_span = Span(temp_start, temp_end)
						preferences.append(VerbalizedPreference(temp_id, temp_span, text_file))
			if annot[i].tag == 'schema':
				if annot[i][1].tag == 'characterisation':
					if annot[i][1][0].text == 'Several_resources':
						temp_id = annot[i].attrib['id'].split('_')[1]
						temp_oneres_id = annot[i][2][0].attrib['id'].split('_')[1]
						temp_otherres_id = annot[i][2][1].attrib['id'].split('_')[1]
						temp_oneres = None
						temp_otherres = None
						for res in resources:
							if temp_oneres_id == res.ID:
								temp_oneres = res
							if temp_otherres_id == res.ID:
								temp_otherres = res
							if temp_oneres != None and temp_otherres != None:
								break
						# Test for features:
						if len(annot[i][1][1]) >= 1:
							for j in range(0, len(annot[i][1][1])):
								if annot[i][1][1][j].attrib['name'] == 'Operator':
									temp_op = str(annot[i][1][1][j].text)
				resources.append(Several_resources(temp_id, [temp_oneres, temp_otherres], temp_op))
		return annotation_author, dialogues, players, turns, segments, resources, preferences
	@staticmethod
	def parse_discourse_Glozz_XML(annot_file, text_file):
		dialogues = []
		# Next, we'll create the Discourse_structure object instances, one per Dialogue instance
		# Discourse-level Glozz parser:
		# List of actual EDUs:
		EDUs = []
		# List of CDU and relation *ID*s! These lists will allow us to reconstruct, starting from the IDs, the actual Relation and Complex_discourse_unit object instances
		# List of tuples (id, [sub-units], [relations])
		CDUs = []
		# List of tuples (id, type, left_arg, right_arg, arg_scope, comments)
		relations = []
		annot = ElementTree().parse(annot_file)
		author_printed = False
		for i in range(0, len(annot)):
			# Selecting Glozz "unit"s:
			if annot[i].tag == 'unit':
				# Selecting "unit" metadata: author,...
				if annot[i][0].tag == 'metadata':
					if annot[i][0][0].tag == 'author' and author_printed == False:
						# For setting the Annotator attribute of Game objects
						annotation_author = annot[i][0][0].text
						author_printed = True
				# Selecting "unit" characterisation
				if annot[i][1].tag == 'characterisation':
					if annot[i][1][0].text == 'Dialogue':
						if annot[i][2].tag == 'positioning':
							temp_id = annot[i].attrib['id'].split('_')[1]
							temp_start = int(annot[i][2][0][0].attrib['index'])
							temp_end = int(annot[i][2][1][0].attrib['index'])
							temp_span = Span(temp_start, temp_end)
							dialogues.append(Dialogue(temp_id, temp_span))
					if annot[i][1][0].text == 'Segment':
						temp_id = annot[i].attrib['id'].split('_')[1]
						if annot[i][2].tag == 'positioning':
							temp_start = int(annot[i][2][0][0].attrib['index'])
							temp_end = int(annot[i][2][1][0].attrib['index'])
							temp_span = Span(temp_start, temp_end)
							EDUs.append(Segment(temp_id, temp_span, text_file))
			if annot[i].tag == 'relation':
				temp_id = annot[i].attrib['id'].split('_')[1]
				if annot[i][1].tag == 'characterisation':
					if annot[i][1][0].tag == 'type':
						temp_rel_type = annot[i][1][0].text
					if annot[i][1][1].tag == 'featureSet':
						if annot[i][1][1][1].attrib['name'] == 'Argument_scope':
							temp_argscope = annot[i][1][1][1].text
						if annot[i][1][1][0].attrib['name'] == 'Comments':
							if annot[i][1][1][0].text != 'Please write in remarks...':
								temp_comments = annot[i][1][1][0].text
							else:
								temp_comments = ''
				if annot[i][2].tag == 'positioning':
					if annot[i][2][0].tag == 'term':
						temp_larg_id = annot[i][2][0].attrib['id'].split('_')[1]
					if annot[i][2][1].tag == 'term':
						temp_rarg_id = annot[i][2][1].attrib['id'].split('_')[1]
				relations.append((temp_id, temp_rel_type, temp_larg_id, temp_rarg_id, temp_argscope, temp_comments))
			if annot[i].tag == 'schema':
				if annot[i][1].tag == 'characterisation':
					if annot[i][1][0].tag == 'type' and annot[i][1][0].text == 'Complex_discourse_unit':
						temp_id = annot[i].attrib['id'].split('_')[1]
						if annot[i][2].tag == 'positioning':
							temp_du_ids = []
							for du in annot[i][2]:
								if du.tag == 'embedded-unit' or du.tag == 'embedded-schema':
									temp_du_ids.append(du.attrib['id'].split('_')[1])
				CDUs.append((temp_id, temp_du_ids))
		return EDUs, CDUs, relations

