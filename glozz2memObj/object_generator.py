#!/usr/bin/python
# -*- coding: utf-8 -*-

from annotation_objects import *

class ObjectGenerator(object):
	def __init__(self, (annot_author, dialogues, players, turns, segments, resources, preferences), (ddialogues, discourse_segments, complex_segments, relations)):
		self.__Annotation_author = annot_author
		self.__Dialogues = dialogues
		self.__DDialogues = ddialogues
		self.__Players = players
		self.__Turns = turns
		self.__Complex_segments = complex_segments
		self.__Segments = segments
		self.__Discourse_segments = discourse_segments
		self.__Resources = resources
		self.__Preferences = preferences
		self.__Relations = relations

	def generate_edu_Game(self):
		# Now, we must figure out:
		# which Turn instances belong to which Dialogue instances,
		# which *derived* Segment instances belong to which Turn instances,
		# which VerbalizedResource instances belong to which derived Segment instances,
		# which VerbalizedPreference instances belong to which derived Segment instances,
		# which players take part in which Dialogue instances,
		# and initialize the remaining parameters of Segment, Turn and Dialogue instances accordingly.
		# For these mappings, we basically reason on the Spans.
		# First, we map VerbalizedResource and VerbalizedPreference instances to derived Segment instances. -- OK
		# Then, we map Several_resources instances to derived Segment instances. -- OK
		# For this, we reason on the constituent VerbalizedResource instances: they both must belong to the same derived Segment instance.	
		# Then, we map derived Segment instances to Turn instances. -- OK
		# Then, we map Turn instances to Dialogue instances. -- OK
		# Finally, based on this, we collect the Emitter attributes of the Turn instances and we thus construct the list of players for each Dialogue instance. -- OK
		for seg in self.__Segments:
			for res in self.__Resources:
				if (isinstance(res, VerbalizedResource) or isinstance(res, Several_resources)) and (int(res.Span.Start_pos) >= int(seg.Span.Start_pos) and int(res.Span.End_pos) <= int(seg.Span.End_pos)):
					seg.addResource(res)
			for pref in self.__Preferences:
				if isinstance(pref, VerbalizedPreference) and (int(pref.Span.Start_pos) >= int(seg.Span.Start_pos) and int(pref.Span.End_pos) <= int(seg.Span.End_pos)):
					seg.addPreference(pref)
		for turn in self.__Turns:
			for seg in self.__Segments:
				if int(turn.Span.Start_pos) <= int(seg.Span.Start_pos) and int(turn.Span.End_pos) >= int(seg.Span.End_pos):
					turn.addSegment(seg)
		for dialog in self.__Dialogues:
			for turn in self.__Turns:
				if int(turn.Span.Start_pos) >= int(dialog.Span.Start_pos) and int(turn.Span.End_pos) <= int(dialog.Span.End_pos):
					dialog.addTurn(turn)
					dialog.addPlayer(turn.Emitter)
		# Now we can finally create and return the Game object:
		return Game(self.__Annotation_author, list(set(self.__Players)), self.__Dialogues)

	def generate_discourse_structures(self):
		real_CDUs = []
		# We first initialize CDUs.
		for cdu in self.__Complex_segments:
			temp_id = cdu[0]
			temp_dus = []
			temp_rels = []
			for one_id in cdu[1]:
				for one_edu in self.__Discourse_segments:
					if one_id == one_edu.ID:
						temp_dus.append(one_edu)
						break
				# Recursion: nested CDUs: only works if non-nested CDUs are found before nested ones in the list, that is, if first non-nested CDUs are created in Glozz, and then nested CDUs are created. Which makes sense from an ergonomic standpoint.
				for one_cdu in real_CDUs:
					if one_id == one_cdu.ID:
						temp_dus.append(one_cdu)
			for one_rel in self.__Relations:
				if one_rel[2] in cdu[1] and one_rel[3] in cdu[1]:
					temp_larg = None
					temp_rarg = None
					for one_du in self.__Discourse_segments + real_CDUs:
						if one_rel[2] == one_du.ID:
							temp_larg = one_du
						if one_rel[3] == one_du.ID:
							temp_rarg = one_du
						if None not in [temp_larg, temp_rarg]:
							temp_rels.append(Relation(one_rel[0], one_rel[1], temp_larg, temp_rarg, one_rel[4], one_rel[5]))
							break
			real_CDUs.append(Complex_segment(temp_id, temp_dus, temp_rels))	
		# Then, we initialize relations, only the shallowest ones (because those inside CDUs are already there!)
		bad_relations = []
		for rel in self.__Relations:
			for cdu in real_CDUs:
				if rel[0] in cdu.Discourse_relation_IDs:
					bad_relations.append(rel)
		real_relations = []
		for rel in list(set(self.__Relations) - set(bad_relations)):
			temp_id = rel[0]
			temp_label = rel[1]
			temp_argscope = rel[4]
			temp_comment = rel[5]
			temp_larg = None
			temp_rarg = None
			for one_du in self.__Discourse_segments + real_CDUs:
				if rel[2] == one_du.ID:
					temp_larg = one_du
				elif rel[3] == one_du.ID:
					temp_rarg = one_du
				if None not in [temp_larg, temp_rarg]:
					real_relations.append(Relation(temp_id, temp_label, temp_larg, temp_rarg, temp_argscope, temp_comment))
					break
		# We now need to initialize the discourse structures, one for each dialogue
		# To create as many pairs of (DUs, DRs) tuples as Dialogue units ; each pair will only contain the DUs within a dialogue unit.
		# To this end, we will reason on the spans!!
		discourse_structures = []
		for dial in self.__DDialogues:
			curr_DUs = []
			curr_DRs = []
			curr_ID = dial.ID
			for arg in self.__Discourse_segments + real_CDUs:
				if int(arg.Span.Start_pos) >= int(dial.Span.Start_pos) and int(arg.Span.End_pos) <= int(dial.Span.End_pos):
					curr_DUs.append(arg)
			for rel in real_relations:
				if rel.Full_Left_argument in curr_DUs and rel.Full_Right_argument in curr_DUs:
					curr_DRs.append(rel)
			discourse_structures.append(Discourse_structure(curr_ID, curr_DUs, curr_DRs))
		return discourse_structures

