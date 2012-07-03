#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Now, we want to parse the GLOZZ annotation into an internal object representation, with the following features:

-- a game is an instance of a "Game" object, with the following attributes:
	-- 'Annotator': string % annotator id; thus, we distinguish one annotation from another
	-- 'Players': list % of strings
	-- 'Dialogues': list % of "Dialogue" instances
-- a "Dialogue" object instance has the following attributes:
	-- 'ID': number
	-- 'Span': "Span" instance
		* a "Span" object has the following attributes:
			-- 'Start_pos': number
			-- 'End_pos': number
	-- 'Turns': list % of "Turn" instances
	-- 'Players': list % of strings
	-- 'Trades': list of "Trade" instances
		* a "Trade" object has the following attributes:
			-- 'Gets': list of "Get" instances
				* a "Get" object has the following attributes
					-- 'Player': string, 
					-- 'Resources': list of "Resource" instances
			-- 'Dice_rolling': list of "Die_roll" instances
				* a "Die_roll" object has the following attributes:
					-- 'Player': string
					-- 'Dice': list % of numbers; here, the list has length 2 
			-- 'Exchange': "Exchange" instance
				* an "Exchange" object has the following attribures:
					-- 'From_player': string
					-- 'To_player': string
					-- 'From_resource': "Resource" instance
					-- 'To_resource': "Resource" instance
	-- 'Anaphors': list % of "Relation" objects, whose 'Label' attribute must be set to 'Anaphora' and whose arguments are "VerbalizedResource" instances, situated in the instances which inherit the "Segment" class 
-- a "Dialogue" object instance contains several "Turn" object instances
-- a "Turn" object instance has the following attributes:
	-- 'ID': number
	-- 'Span': "Span" instance
	-- 'Segments': list % of instances of objects inheriting the "Segment" class
	-- 'Timestamp': timestamp of the turn % hh:mm:ss:mss
	-- 'Shallow_ID': number % ID as given by the Soclogs
	-- 'Emitter': string
	-- 'State': "State" instance
		* a "State" object has the following attributes:
			-- 'Resources': list of "Resource" instances
				* a "Resource" object has the following attributes: 
					-- 'ID': number
					-- 'Kind': string
					-- 'Quantity': string
			-- 'Developments': list of "Development" instances
				* a "Development" object has the following attributes:
					-- 'ID': number
					-- 'Kind': string
					-- 'Amount': number
	-- 'Comments': string
-- a "Turn" instance contains several "Offer/Other/Counteroffer/Strategic_comment/Accept/Refusal" object instances, which are inherited from the "Segment" class
-- such an instance has the following attributes:
	-- 'ID': number % inherited from the "Segment" class
	-- 'Receiver': string
	-- 'Surface_act_type': string
	-- 'Resources': list % of "VerbalizedResource" instances; can be []
	-- 'Preferences': list % of "VerbalizedPreference" instances; can be []
	-- 'Span': "Span" instance % inherited from the "Segment" class
-- such an instance instance contains zero, one or several "VerbalizedResource" object instances
	-- a "VerbalizedResource" object which inherits the "Resource" class and has the following attributes:
		-- 'ID': number % inherited from the "Resource" class
		-- 'Span': "Span" instance 
		-- 'Status': string
		-- 'Kind': string % inherited from the "Resource" class
		-- 'Quantity': string % inherited from the "Resource" class
	**PLUS, perhaps** "Several_resources" objects, which have the following attributes:
	-- 'Resources': tuple % of two "VerbalizedResource" instances
	-- 'Operator': string % in the set: {'AND'; 'OR'}
	-- 'ID': number
-- such an instance instance contains zero, one or several "Preference" object instances
	-- a "Preference" object has the following attributes:
		-- 'ID': number % inherited from the "Segment" class
		-- 'Span': "Span" instance % inherited from the "Segment" class
DISCOURSE:

Each "Game" instance has a global SDRS which, most of the time, is the union of the Dialogue-level SDRSes, except when "Dialogue" SDRSes are linked.

Each "Dialogue" instance has its own vanilla SDRS, which consists of a "Discourse_structure" object instance; each such instance has the following attributes:
	-- 'ID': number % a.k.a. label of the SDRS
	-- 'Discourse_units': list % of instances inheriting the "Discourse_unit" object; such an instance can be either "Complex_segment" or "Segment"; a "Discouse_unit" object has the following attribute:
		-- 'ID': number
		* "Segment" objects have already been described % 
		* a "Complex_segment" object has the following attributes: % it is actually structurally identical to a 'Discourse_structure' object, except that the cohesion constraint is enforced, ie each DU is connected to at least another one and so there is no solitary DU
			-- 'Discourse_units': list % of "Segment" or "Complex_segment" instances
			-- 'Discourse_relations': list % of "Relation" instances, between EDUs and / or CDUs, but *NOT* inside CDUs
	-- 'Discourse_relations': list % of "Relation" instances, between EDUs and / or CDUs, but *NOT* inside CDUs
		* a "Discourse_relation" object has the following attributes:
			-- 'Label': string % relation type, according to SDRT
			-- 'Left_argument': number % left-argument EDU or CDU 'ID'
			-- 'Right_argument': number % right-argument EDU or CDU 'ID'

'''
##### CDU-level stuff

class Discourse_unit(object):
	def __init__(self, id):
		self.__ID = id
	@property
	def ID(self):
		return self.__ID

class Segment(Discourse_unit):
	def __init__(self, id, span):
		Discourse_unit.__init__(self, id)
		self.__Span = span
	@property
	def Span(self):
		return self.__Span
	@Span.setter
	def Span(self, span):
		if not isinstance(span, Span):
			raise TypeError("Segment.Span:: Error: must be a Span instance!")
		self.__Span = span
	@Span.deleter
	def Span(self):
		raise TypeError("Segment.Span:: Error: cannot delete property!")

class Discourse_structure(Discourse_unit):
	def __init__(self, id, DUs, DRs):
		Discourse_unit.__init__(self, id)
		import copy
		self.__Discourse_units = copy.deepcopy(DUs)
		self.__Discourse_relations = copy.deepcopy(DRs)
		del copy
	@property
	def Discourse_units(self):
		DU_IDs = []
		for DU in self.__Discourse_units:
			DU_IDs.append(DU.ID)
		return DU_IDs
	@Discourse_units.deleter
	def Discourse_units(self):
		self.__Discourse_units = []
	@property
	def Full_Discourse_units(self):
		return self.__Discourse_units
	@property
	def Discourse_relation_IDs(self):
		DR_ids = []
		for DR in self.__Discourse_relations:
			DR_ids.append(DR.ID)
		return DR_ids
	@property
	def Discourse_relations(self):
		DRs = []
		for DR in self.__Discourse_relations:
			DRs.append((DR.Label, DR.Left_argument, DR.Right_argument))
		return DRs
	@property
	def Full_Discourse_relations(self):
		return self.__Discourse_relations
	@property
	def Span(self):
		left_start = min(int(du.Span.Start_pos) for du in self.__Discourse_units)
		right_start = max(int(du.Span.End_pos) for du in self.__Discourse_units)

class Complex_segment(Discourse_structure):
	def __init__(self, id, DUs, DRs):
		# add contiguity checking:
		rel_args = []
		__dump = [rel_args.append(rel.Left_argument) for rel in DRs if rel.Left_argument not in rel_args]
		__dump = [rel_args.append(rel.Right_argument) for rel in DRs if rel.Right_argument not in rel_args]
		for du in DUs:
			if du.ID not in rel_args:
				print "Warning: Complex segment %(CDU)s has islands: sub-unit %(DU)s disconnected!!" % {'CDU': id, 'DU': du.ID}
		del rel_args
		Discourse_structure.__init__(self, id, DUs, DRs)

class Relation(object):
	def __init__(self, id, label, larg, rarg, arg_scope, comments):
		self.__ID = id
		self.__Label = label
		self.__Left_argument = larg
		self.__Right_argument = rarg
		self.Arg_scope = arg_scope
		self.Comments = comments
	@property
	def ID(self):
		return self.__ID
	@property
	def Label(self):
		return self.__Label
	@Label.setter
	def Label(self, newlab):
		self.__Label = newlab
	@Label.deleter
	def Label(self):
		self.__Label = ''
	@property
	def Left_argument(self):
		return self.__Left_argument.ID
	@property
	def Right_argument(self):
		return self.__Right_argument.ID
	@property
	def Full_Left_argument(self):
		return self.__Left_argument
	@property
	def Full_Right_argument(self):
		return self.__Right_argument



##### EDU-level stuff
class Game(object):
	def __init__(self, annotator, players, dialogues):
		self.__Annotator = annotator
		import copy
		self.__Players = copy.deepcopy(players)
		self.__Dialogues = copy.deepcopy(dialogues)
		del copy
	@property
	def Annotator(self):
		return self.__Annotator
	@Annotator.setter
	def Annotator(self, newAnnot):
		self.__Annotator = newAnnot
	@property
	def Players(self):
		return self.__Players
	@Players.setter
	def Players(self, liste):
		if not isinstance(liste, list):
			raise TypeError("Game.Players:: Error: must be a list!")
		import copy
		self.__Players = copy.deepcopy(liste)
		del copy
	@Players.deleter
	def Players(self):
		raise TypeError("Game.Players:: Error: cannot delete property!")
	@property
	def Dialogues(self):
		return self.__Dialogues
	@Dialogues.setter
	def Dialogues(self, liste):
		if not isinstance(liste, list):
			raise TypeError("Game.Dialogues:: Error: must be a list!")
		import copy
		self.__Dialogues = copy.deepcopy(liste)
		del copy
	@Dialogues.deleter
	def Dialogues(self):
		raise TypeError("Game.Dialogues:: Error: cannot delete property!")

class Dialogue(object):
	def __init__(self, id, span, Trades, turns=[], players=[], Anaphors=[]):
		self.__ID = id
		self.__Span = span
		import copy
		self.__Turns = copy.deepcopy(turns)
		self.__Players = copy.deepcopy(players)
		for anaphora in Anaphors:
			if type(anaphora).__name__ == 'Relation' and anaphora.Label != "Anaphora":
				raise ValueError("Dialogue.Anaphors:: Error: must be an \"Anaphora\" relation!")
		self.__Anaphors = copy.deepcopy(Anaphors)
		del copy
		self.Trades = Trades
	@property
	def ID(self):
		return self.__ID
	@property
	def Span(self):
		return self.__Span
	@Span.setter
	def Span(self, span):
		if not isinstance(span, Span):
			raise TypeError("Dialogue.Span:: Error: must be a 'Span' object instance!")
		self.__Span = span
	@Span.deleter
	def Span(self):
		raise TypeError("Dialogue.Span:: Error: cannot delete property!")
	@property
	def Turns(self):
		return self.__Turns
	@Turns.setter
	def Turns(self, liste):
		if not isinstance(liste, list):
			raise TypeError("Dialogue.Turns:: Error: must be a list!")
		import copy
		self.__Turns = copy.deepcopy(liste)
		del copy
	@Turns.deleter
	def Turns(self):
		raise TypeError("Dialogue.Turns:: Error: cannot delete property!")
	@property
	def Players(self):
		return list(set(self.__Players))
	@Players.setter
	def Players(self, liste):
		if not isinstance(liste, list):
			raise TypeError("Dialogue.Players:: Error: must be a list!")
		import copy
		self.__Players = copy.deepcopy(liste)
		del copy
	@Players.deleter
	def Players(self):
		raise TypeError("Dialogue.Players:: Error: cannot delete property!")
	@property
	def Anaphors(self):
		return self.__Anaphors
	@Anaphors.setter
	def Anaphors(self, anaphors):
		if not isinstance(anaphors, list):
			raise TypeError("Dialogue.Anaphors:: Error: must be a list!")
		for anaphora in anaphors:
			if type(anaphora).__name__ == 'Relation' and anaphora.Label != "Anaphora":
				raise ValueError("Dialogue.Anaphors:: Error: must be an \"Anaphora\" relation!")
		import copy
		self.__Anaphors = copy.deepcopy(anaphors)
		del copy
	def addTurn(self, newTurn):
		if not isinstance(newTurn, Turn):
			raise TypeError("Dialogue::addTurn: Error: must be of Turn type!")
		self.__Turns.append(newTurn)
	def addPlayer(self, newPlayer):
		if not isinstance(newPlayer, str):
			raise TypeError("Dialogue::addPlayer: Error: must be a string!")
		self.__Players.append(newPlayer)

# Add getters and setters for the attributes with are (lists of) other class instances!

class Trade(object):
	def __init__(self, Gets, Dice_rolling, Exchange):
		import copy
		self.Gets = copy.deepcopy(Gets)
		self.Dice_rolling = copy.deepcopy(Dice_rolling)
		del copy
		self.Exchange = Exchange

class Get(object):
	def __init__(self, player, Resources=[None]):
		self.__Player = player
		import copy
		self.__Resources = copy.deepcopy(Resources)
		del copy
	@property
	def Player(self):
		return self.__Player
	@Player.setter
	def Player(self, player):
		if not isinstance(player, str):
			raise TypeError("Get.Player:: Error: must be a string!")
		self.__Player = player
	@Player.deleter
	def Player(self):
		self.__Player = None
	@property
	def Resources(self):
		return self.__Resources
	@Resources.setter
	def Resources(self, Res):
		if not isinstance(Res, list):
			raise TypeError("Get.Resources:: Error: must be a list!")
		import copy
		self.__Resources = copy.deepcopy(Res)
		del copy
	@Resources.deleter
	def Resources(self):
		self.__Resources = []

class Die_roll(object):
	def __init__(self, player, Dice):
		self.__Player = player
		import copy
		self.__Dice = copy.deepcopy(Dice)
		del copy
	@property
	def Player(self):
		return self.__Player
	@Player.setter
	def Player(self, player):
		if not isinstance(player, str):
			raise TypeError("Die_roll.Player:: Error: must be a str!")
		self.__Player = player
	@Player.deleter
	def Player(self):
		self.__Player = None
	@property
	def Dice(self):
		return self.__Dice
	@Dice.setter
	def Dice(self, dicelist):
		if not isinstance(dicelist, list):
			raise TypeError("Die_roll.Dice:: Error: must be a list!")
		import copy
		self.__Dice = copy.deepcopy(dicelist)
		del copy
	@Dice.deleter
	def Dice(self):
		self.__Dice =  []

class Exchange(object):
	def __init__(self, fromplayer, toplayer, fromres, tores):
		self.__From_player = fromplayer
		self.__To_player = toplayer
		self.__From_resource = fromres
		self.__To_resource = tores
	@property
	def From_player(self):
		return self.__From_player
	@From_player.setter
	def From_player(self, fplayer):
		if not isinstance(fplayer, str):
			raise TypeError("Exchange.From_player:: Error: must be a str!")
		self.__From_player = fplayer
	@From_player.deleter
	def From_player(self):
		self.__From_player = None
	@property
	def To_player(self):
		return self.__To_player
	@To_player.setter
	def To_player(self, tplayer):
		if not isinstance(tplayer, str):
			raise TypeError("Exchange.To_player:: Error: must be a str!")
		self.__To_player = tplayer
	@To_player.deleter
	def To_player(self):
		self.__To_player = None
	@property
	def From_resource(self):
		return self.__From_resource
	@From_resource.setter
	def From_resource(self, fres):
		if not isinstance(fres, Resource):
			raise TypeError("Exchange.From_resource:: Error: must be a Resource instance!")
		self.__From_Resource = fres
	@From_resource.deleter
	def From_resource(self):
		self.__From_resource = None
	@property
	def To_resource(self):
		return self.__To_resource
	@To_resource.setter
	def To_resource(self, tres):
		if not isinstance(tres, Resource):
			raise TypeError("Exchange.To_resource:: Error: must be a Resource instance!")
		self.__To_Resource = tres
	@To_resource.deleter
	def To_resource(self):
		self.__To_resource = None

class Turn(object):
	def __init__(self, id, span, emitter, timestamp, shallow_id, state, comments, Segments=[]):
		self.__ID = id
		self.__Span = span
		import copy
		self.__Segments = copy.deepcopy(Segments)
		del copy
		self.Emitter = emitter
		self.Timestamp = timestamp
		self.Shallow_ID = shallow_id
		self.__State = state
		self.Comments = comments
	@property
	def ID(self):
		return self.__ID
	@property
	def Span(self):
		return self.__Span
	@Span.setter
	def Span(self, span):
		if not isinstance(span, Span):
			raise TypeError("Turn.Span:: Error: must be a Span instance!")
		self.__Span = span
	@Span.deleter
	def Span(self):
		raise TypeError("Turn.Span:: Error: cannot delete property!")
	@property
	def Segments(self):
		return self.__Segments
	@Segments.setter # to do this kind of setter to all list-like attributes!
	def Segments(self, SegsToAdd, SegsToRem):
		if not isinstance(SegsToAdd, list) or not isinstance(SegsToRem, list):
			raise TypeError("Turn.Segments:: Error: both input arguments have to be lists!")
		self.__Segments += SegsToAdd
		self.__Segments = [seg for seg in self.__Segments if seg not in SegsToRem]
	@Segments.deleter
	def Segments(self):
		self.__Segments = []
	@property
	def State(self):
		return self.__State
	@State.setter
	def State(self, state):
		if not isinstance(state, State):
			raise TypeError("Turn.State:: Error: has to be a State instance!")
		self.__State = state
	@State.deleter
	def State(self):
		raise TypeError("Turn.State:: Error: cannot delete property!")
	# I think what follows is legitimate because each Turn can only have one single State instance
	@property
	def Developments(self): # wrapper of the State object; shortcut to the Developments
		return self.__State.Developments
	@property
	def Resources(self): # wrapper of the State object; shortcut to the Resources
		return self.__State.Resources
	def addSegment(self, newSeg):
		if not isinstance(newSeg, Segment):
			raise TypeError("Turn::addSegment: Error: must be of (derived) Segment type!")
		self.__Segments.append(newSeg)

class State(object):
	def __init__(self, Resources, Developments):
		import copy
		self.__Resources = copy.deepcopy(Resources)
		self.__Developments = copy.deepcopy(Developments)
		del copy
	@property
	def Resources(self):
		return self.__Resources
	@Resources.setter
	def Resources(self, newResources):
		if not isinstance(newResources, list):
			raise TypeError("State.Resources:: Error: must be a list!")
		import copy
		self.__Resources = copy.deepcopy(newResources)
		del copy
	@Resources.deleter
	def Resources(self):
		raise TypeError("State.Resources: cannot delete property!")
	@property
	def Developments(self):
		return self.__Developments
	@Developments.setter
	def Developments(self, newDevelopments):
		if not isinstance(newDevelopments, list):
			raise TypeError("State.Developments:: Error: must be a list!")
		import copy
		self.__Developments = copy.deepcopy(newDevelopments)
		del copy
	@Developments.deleter
	def Developments(self):
		raise TypeError("State.Developments: cannot delete property!")

class Item(object):
	def __init__(self, id, kind):
		self.__ID = id
		self.Kind = kind
	@property
	def ID(self):
		return self.__ID
# From the "Item" class both "Resource" and "Development" will inherit

class Resource(Item):
	def __init__(self, id, kind, quantity):
		Item.__init__(self, id, kind)
		self.Quantity = quantity

class Development(Item):
	def __init__(self, id, kind, amount):
		Item.__init__(self, id, kind)
		self.Amount = amount

class Offer(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, Resources=[], Preferences=[]):
		Segment.__init__(self, id, span)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Counteroffer(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, Resources=[], Preferences=[]):
		Segment.__init__(self, id, span)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Accept(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, Resources=[], Preferences=[]):
		Segment.__init__(self, id, span)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Refusal(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, Resources=[], Preferences=[]):
		Segment.__init__(self, id, span)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Strategic_comment(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, Resources=[], Preferences=[]):
		Segment.__init__(self, id, span)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Other(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, Resources=[], Preferences=[]):
		Segment.__init__(self, id, span)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)
	
class VerbalizedResource(Resource):
	def __init__(self, id, span, status, kind, quantity):
		Resource.__init__(self, id, kind, quantity)
		self.__Span = span
		self.Status = status
	@property
	def Span(self):
		return self.__Span
	@Span.setter
	def Span(self, span):
		if not isinstance(span, Span):
			raise TypeError("VerbalizedResource.Span: Error: must be a Span instance!")
		self.__Span = span
	@Span.deleter
	def Span(self):
		raise TypeError("VerbalizedResource.Span: Error: cannot delete property!")

class Several_resources(object):
	def __init__(self, id, Resources, operator):
		self.__ID = id
		import copy
		self.__Resources = copy.deepcopy(Resources)
		del copy
		self.Operator = operator
	@property
	def ID(self):
		return self.__ID
	@property
	def Resources(self):
		return self.__Resources
	@Resources.setter
	def Resources(self, ResToAdd):
		if len(self.__Resources) >= 2:
			raise TypeError("Several_resources:Resources:: Error: cannot have more than two resources inside!")
	@Resources.deleter
	def Resources(self):
		self.__Resources = (None, None)
	@property
	def Span(self):
		Start_pos = min(int(self.__Resources[0].Span.Start_pos), int(self.__Resources[1].Span.Start_pos))
		End_pos = max(int(self.__Resources[0].Span.End_pos), int(self.__Resources[1].Span.End_pos))
		_span = Span(Start_pos, End_pos)
		return _span
		

class VerbalizedPreference(Segment):
	def __init__(self, id, span):
		Segment.__init__(self, id, span)

class Span(object):
	def __init__(self, spos, epos):
		if spos <= epos:
			self.__Start_pos = spos
			self.__End_pos = epos
		else:
			raise ValueError("Span:: Error: starting position after ending position!")
	@property
	def Start_pos(self):
		return self.__Start_pos
	@property
	def End_pos(self):
		return self.__End_pos
# We should be doing it bottom up, from the most detailed classes to the most "enclosing" ones!

import sys, codecs
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring

u_annot_file = "./pilot03_1_stac_u_06062012.aa"
d_annot_file = "./pilot03_1_stac_d_06062012.aa"

u_annot = ElementTree().parse(u_annot_file)
d_annot = ElementTree().parse(d_annot_file)

# EDU-level Glozz parser and internal object initializer:
dialogues = []
turns = []
segments = []
resources = []
preferences = []
players = []
# EDU-level parsing:
# Add "Span" for each unit:
author_printed = False
for i in range(0,len(u_annot)):
	# Selecting Glozz "unit"s:
	if u_annot[i].tag == 'unit':
		# Selecting "unit" metadata: author,...
		if u_annot[i][0].tag == 'metadata':
			if u_annot[i][0][0].tag == 'author' and author_printed == False:
				# For setting the Annotator attribute of Game objects
				annotation_author = u_annot[i][0][0].text
				author_printed = True
		# Selecting "unit" characterisation
		if u_annot[i][1].tag == 'characterisation':
			# Getting "unit" types (Resources, Offers, Turns etc)
			# if u_annot[i].getchildren()[1].getchildren()[0].text == 'Turn' | 'Offer' | etc...
			if u_annot[i][1][0].text == 'Dialogue':
				temp_gets = []
				temp_dice_rolls = []
				temp_exchange = None
				temp_id = u_annot[i].attrib['id'].split('_')[1]
				# Test for features:
				if len(u_annot[i][1][1]) >= 1:
					for j in range(0, len(u_annot[i][1][1])):
						if u_annot[i][1][1][j].attrib['name'] == 'Gets':
							for oneget in u_annot[i][1][1][j].text.split('.')[:-1]:
								temp_who = oneget.split(' gets ')[0].strip(' ')
								if 'nothing' in oneget.split(' gets ')[1]:
									temp_gets.append(Get(temp_who))
								else:
									temp_what = oneget.split(' gets ')[1].split(' ')[1]
									temp_qty = oneget.split(' gets ')[1].split(' ')[0]
									temp_res = Resource(None, temp_what, temp_qty)
									temp_gets.append(Get(temp_who, temp_res))
						elif u_annot[i][1][1][j].attrib['name'] == 'Dice_rolling':
							for oneroll in u_annot[i][1][1][j].text.split('.')[:-1]:
								temp_who = str(oneroll.split(' rolled a ')[0].strip(' '))
								temp_what = [str(oneroll.split(' rolled a ')[1].split(' and a '))[0], str(oneroll.split(' rolled a ')[1].split(' and a '))[1]]
								temp_dice_rolls.append(Die_roll(temp_who, temp_what))
						elif u_annot[i][1][1][j].attrib['name'] == 'Trades':
							if u_annot[i][1][1][j].text != None:
								for onetrade in u_annot[i][1][1][j].text.split('.')[:-1]:
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
				temp_start = int(u_annot[i][2][0][0].attrib['index'])
				temp_end = int(u_annot[i][2][1][0].attrib['index'])
				temp_span = Span(temp_start, temp_end)
				dialogues.append(Dialogue(temp_id, temp_span, temp_trade))
			if u_annot[i][1][0].text == 'Turn':
				temp_id = u_annot[i].attrib['id'].split('_')[1]
				# Test for features:
				temp_res = []
				temp_devs = []
				if len(u_annot[i][1][1]) >= 1:
					for j in range(0, len(u_annot[i][1][1])):
						if u_annot[i][1][1][j].attrib['name'] == 'Identifier':
							temp_shid = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Timestamp':
							temp_timestamp = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Emitter':
							temp_emitter = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Resources':
							# Add parsing for resources
							for res in str(u_annot[i][1][1][j].text).split('; '):
								temp_res.append(Resource(None, res.split('=')[0], res.split('=')[1]))
						elif u_annot[i][1][1][j].attrib['name'] == 'Developments':
							if u_annot[i][1][1][j].text != None:
								for dev in str(u_annot[i][1][1][j].text).split(';  '):
									temp_devs.append(Development(None, dev.split('=')[0], dev.split('=')[1]))
						elif u_annot[i][1][1][j].attrib['name'] == 'Comments':
							temp_comments = str(u_annot[i][1][1][j].text)
				temp_state = State(temp_res, temp_devs)
				temp_start = int(u_annot[i][2][0][0].attrib['index'])
				temp_end = int(u_annot[i][2][1][0].attrib['index'])
				temp_span = Span(temp_start, temp_end)
				players.append(temp_emitter)
				turns.append(Turn(temp_id, temp_span, temp_emitter, temp_timestamp, temp_shid, temp_state, temp_comments))
			if u_annot[i][1][0].text not in ['Turn', 'Dialogue', 'Resource', 'Preference', 'paragraph']:
				temp_edu_type = str(u_annot[i][1][0].text)
				temp_id = u_annot[i].attrib['id'].split('_')[1]
				# Test for features:
				if len(u_annot[i][1][1]) >= 1:
					for j in range(0, len(u_annot[i][1][1])):
						if u_annot[i][1][1][j].attrib['name'] == 'Surface_act':
							temp_sa_type = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Addressee':
							temp_recv = str(u_annot[i][1][1][j].text).split(', ')
				temp_start = int(u_annot[i][2][0][0].attrib['index'])
				temp_end = int(u_annot[i][2][1][0].attrib['index'])
				temp_span = Span(temp_start, temp_end)
				segments.append(eval(temp_edu_type)(temp_id, temp_span, temp_recv, temp_sa_type))
			if u_annot[i][1][0].text == 'Resource':
				temp_id = u_annot[i].attrib['id'].split('_')[1]
				# Test for features:
				if len(u_annot[i][1][1]) >= 1:
					for j in range(0, len(u_annot[i][1][1])):
						if u_annot[i][1][1][j].attrib['name'] == 'Status':
							temp_status = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Kind':
							temp_kind = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Quantity':
							temp_qty = str(u_annot[i][1][1][j].text)
						elif u_annot[i][1][1][j].attrib['name'] == 'Correctness':
							temp_correctness = str(u_annot[i][1][1][j].text)
				temp_start = u_annot[i][2][0][0].attrib['index']
				temp_end = u_annot[i][2][1][0].attrib['index']
				temp_span = Span(temp_start, temp_end)
				resources.append(VerbalizedResource(temp_id, temp_span, temp_status, temp_kind, temp_qty))
			if u_annot[i][1][0].text == 'Preference':
				temp_id = u_annot[i].attrib['id'].split('_')[1]
				temp_start = u_annot[i][2][0][0].attrib['index']
				temp_end = u_annot[i][2][1][0].attrib['index']
				temp_span = Span(temp_start, temp_end)
				preferences.append(VerbalizedPreference(temp_id, temp_span))
	if u_annot[i].tag == 'schema':
		if u_annot[i][1].tag == 'characterisation':
			if u_annot[i][1][0].text == 'Several_resources':
				temp_id = u_annot[i].attrib['id'].split('_')[1]
				temp_oneres_id = u_annot[i][2][0].attrib['id'].split('_')[1]
				temp_otherres_id = u_annot[i][2][1].attrib['id'].split('_')[1]
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
				if len(u_annot[i][1][1]) >= 1:
					for j in range(0, len(u_annot[i][1][1])):
						if u_annot[i][1][1][j].attrib['name'] == 'Operator':
							temp_op = str(u_annot[i][1][1][j].text)
		resources.append(Several_resources(temp_id, [temp_oneres, temp_otherres], temp_op))
				
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

for seg in segments:
	for res in resources:
		if (isinstance(res, VerbalizedResource) or isinstance(res, Several_resources)) and (int(res.Span.Start_pos) >= int(seg.Span.Start_pos) and int(res.Span.End_pos) <= int(seg.Span.End_pos)):
			seg.addResource(res)
	for pref in preferences:
		if isinstance(pref, VerbalizedPreference) and (int(pref.Span.Start_pos) >= int(seg.Span.Start_pos) and int(pref.Span.End_pos) <= int(seg.Span.End_pos)):
			seg.addPreference(pref)
for turn in turns:
	for seg in segments:
		if int(turn.Span.Start_pos) <= int(seg.Span.Start_pos) and int(turn.Span.End_pos) >= int(seg.Span.End_pos):
			turn.addSegment(seg)
for dialog in dialogues:
	for turn in turns:
		if int(turn.Span.Start_pos) >= int(dialog.Span.Start_pos) and int(turn.Span.End_pos) <= int(dialog.Span.End_pos):
			dialog.addTurn(turn)
			dialog.addPlayer(turn.Emitter)

# Now we can finally create the Game object:

game = Game(annotation_author, list(set(players)), dialogues)

del players, dialogues, turns, segments, resources, preferences

print game.Annotator
print len(game.Dialogues)
print game.Dialogues[2].Players
for turn in game.Dialogues[2].Turns:
	if turn.Shallow_ID == '49':
		print turn.Segments[0].Preferences[0].Span
print game.Dialogues[2].Turns[3].Shallow_ID

# Next, we'll create the Discourse_structure object instances, one per Dialogue instance
# Discourse-level Glozz parser:

# List of actual EDUs:
EDUs = []
# List of CDU and relation *ID*s! These lists will allow us to reconstruct, starting from the IDs, the actual Relation and Complex_discourse_unit object instances
# List of tuples (id, [sub-units], [relations])
CDUs = []
# List of tuples (id, type, left_arg, right_arg, arg_scope, comments)
relations = []


author_printed = False
for i in range(0, len(d_annot)):
	# Selecting Glozz "unit"s:
	if d_annot[i].tag == 'unit':
		# Selecting "unit" metadata: author,...
		if d_annot[i][0].tag == 'metadata':
			if d_annot[i][0][0].tag == 'author' and author_printed == False:
				# For setting the Annotator attribute of Game objects
				annotation_author = d_annot[i][0][0].text
				author_printed = True
		# Selecting "unit" characterisation
		if d_annot[i][1].tag == 'characterisation':
			if d_annot[i][1][0].text == 'Segment':
				temp_id = d_annot[i].attrib['id'].split('_')[1]
				temp_start = int(u_annot[i][2][0][0].attrib['index'])
				temp_end = int(u_annot[i][2][1][0].attrib['index'])
				temp_span = Span(temp_start, temp_end)
				EDUs.append(Segment(temp_id, temp_span))
	if d_annot[i].tag == 'relation':
		temp_id = d_annot[i].attrib['id'].split('_')[1]
		if d_annot[i][1].tag == 'characterisation':
			if d_annot[i][1][0].tag == 'type':
				temp_rel_type = d_annot[i][1][0].text
			if d_annot[i][1][1].tag == 'featureSet':
				if d_annot[i][1][1][1].attrib['name'] == 'Argument_scope':
					temp_argscope = d_annot[i][1][1][1].text
				if d_annot[i][1][1][0].attrib['name'] == 'Comments':
					if d_annot[i][1][1][0].text != 'Please write in remarks...':
						temp_comments = d_annot[i][1][1][0].text
					else:
						temp_comments = ''
		if d_annot[i][2].tag == 'positioning':
			if d_annot[i][2][0].tag == 'term':
				temp_larg_id = d_annot[i][2][0].attrib['id'].split('_')[1]
			if d_annot[i][2][1].tag == 'term':
				temp_rarg_id = d_annot[i][2][1].attrib['id'].split('_')[1]
		relations.append((temp_id, temp_rel_type, temp_larg_id, temp_rarg_id, temp_argscope, temp_comments))
	if d_annot[i].tag == 'schema':
		if d_annot[i][1].tag == 'characterisation':
			if d_annot[i][1][0].tag == 'type' and d_annot[i][1][0].text == 'Complex_discourse_unit':
				temp_id = d_annot[i].attrib['id'].split('_')[1]
				if d_annot[i][2].tag == 'positioning':
					temp_du_ids = []
					for du in d_annot[i][2]:
						if du.tag == 'embedded-unit' or du.tag == 'embedded-schema':
							temp_du_ids.append(du.attrib['id'].split('_')[1])
		CDUs.append((temp_id, temp_du_ids))
								

real_CDUs = []
# We first initialize CDUs.
for cdu in CDUs:
	temp_id = cdu[0]
	temp_dus = []
	temp_rels = []
	for one_id in cdu[1]:
		for one_edu in EDUs:
			if one_id == one_edu.ID:
				temp_dus.append(one_edu)
				break
		# Recursion: nested CDUs: only works if non-nested CDUs are found before nested ones in the list, that is, if first non-nested CDUs are created in Glozz, and then nested CDUs are created. Which makes sense from an ergonomic standpoint.
		for one_cdu in real_CDUs:
			if one_id == one_cdu.ID:
				temp_dus.append(one_cdu)
	for one_rel in relations:
		if one_rel[2] in cdu[1] and one_rel[3] in cdu[1]:
			temp_larg = None
			temp_rarg = None
			for one_du in EDUs + real_CDUs:
				if one_rel[2] == one_du.ID:
					temp_larg = one_du
				if one_rel[3] == one_du.ID:
					temp_rarg = one_du
				if None not in [temp_larg, temp_rarg]:
					temp_rels.append(Relation(one_rel[0], one_rel[1], temp_larg, temp_rarg, one_rel[4], one_rel[5]))
					break
	real_CDUs.append(Complex_segment(temp_id, temp_dus, temp_rels))	

for realcdu in real_CDUs:
	if type(realcdu.Full_Discourse_units[-1]).__name__ == 'Complex_segment':
		print realcdu.Full_Discourse_relations[0].Label

# Then, we initialize relations, only the shallowest ones (because those inside CDUs are already there!)
bad_relations = []
for rel in relations:
	for cdu in real_CDUs:
		if rel[0] in cdu.Discourse_relation_IDs:
			bad_relations.append(rel)

real_relations = []
for rel in list(set(relations) - set(bad_relations)):
	temp_id = rel[0]
	temp_label = rel[1]
	temp_argscope = rel[4]
	temp_comment = rel[5]
	temp_larg = None
	temp_rarg = None
	for one_du in EDUs + real_CDUs:
		if rel[2] == one_du.ID:
			temp_larg = one_du
		elif rel[3] == one_du.ID:
			temp_rarg = one_du
		if None not in [temp_larg, temp_rarg]:
			real_relations.append(Relation(temp_id, temp_label, temp_larg, temp_rarg, temp_argscope, temp_comments))
			break

# We now need to initialize the discourse structures, one for each dialogue
# To create as many pairs of (DUs, DRs) tuples as Dialogue units ; each pair will only contain the DUs within a dialogue unit.
# To this end, we will reason on the spans!!



