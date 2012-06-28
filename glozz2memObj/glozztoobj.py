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
	def Discourse_relations(self):
		DRs = []
		for DR in self.__Discourse_relations:
			DRs.append((DR.Label, DR.Left_argument, DR.Right_argument))
		return DRs
	@property
	def Full_Discourse_relations(self):
		return self.__Discourse_relations

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
	def __init__(self, label, larg, rarg):
		self.__Label = label
		self.__Left_argument = larg
		self.__Right_argument = rarg
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
	def __init__(self, players, dialogues):
		import copy
		self.__Players = copy.deepcopy(players)
		self.__Dialogues = copy.deepcopy(dialogues)
		del copy
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
	def __init__(self, id, span, turns, players, Trades, Anaphors):
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
		return self.__Players
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

# Add getters and setters for the attributes with are (lists of) other class instances!

class Trade(object):
	def __init__(self, Gets, Dice_rolling, Exchange):
		import copy
		self.Gets = copy.deepcopy(Gets)
		self.Dice_rolling = copy.deepcopy(Dice_rolling)
		del copy
		self.Exchange = Exchange

class Get(object):
	def __init__(self, player, Resources):
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
		if not isinstance(fres, VerbalizedResource):
			raise TypeError("Exchange.From_resource:: Error: must be a VerbalizedResource instance!")
		self.__From_Resource = fres
	@From_resource.deleter
	def From_resource(self):
		self.__From_resource = None
	@property
	def To_resource(self):
		return self.__To_resource
	@To_resource.setter
	def To_resource(self, tres):
		if not isinstance(tres, VerbalizedResource):
			raise TypeError("Exchange.To_resource:: Error: must be a VerbalizedResource instance!")
		self.__To_Resource = tres
	@To_resource.deleter
	def To_resource(self):
		self.__To_resource = None

class Turn(object):
	def __init__(self, id, span, Segments, emitter, timestamp, shallow_id, state, comments):
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

class Offer(Segment):
	def __init__(self, id, span, receiver, surface_act_type, Resources, Preferences):
		Segment.__init__(self, id, span)
		self.Receiver = receiver
		self.Surface_act_type = surface_act_type
		import copy
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy

class Counteroffer(Segment):
	def __init__(self, id, span, receiver, surface_act_type, Resources, Preferences):
		Segment.__init__(self, id, span)
		self.Receiver = receiver
		self.Surface_act_type = surface_act_type
		import copy
		copy.deepcopy(self.Resources, Resouces)
		copy.deepcopy(self.Preferences, Preferences)
		del copy

class Accept(Segment):
	def __init__(self, id, span, receiver, surface_act_type, Resources, Preferences):
		Segment.__init__(self, id, span)
		self.Receiver = receiver
		self.Surface_act_type = surface_act_type
		import copy
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy

class Refusal(Segment):
	def __init__(self, id, span, receiver, surface_act_type, Resources, Preferences):
		Segment.__init__(self, id, span)
		self.Receiver = receiver
		self.Surface_act_type = surface_act_type
		import copy
		copy.deepcopy(self.Resources, Resouces)
		copy.deepcopy(self.Preferences, Preferences)
		del copy

class Strategic_comment(Segment):
	def __init__(self, id, span, receiver, surface_act_type, Resources, Preferences):
		Segment.__init__(self, id, span)
		self.Receiver = receiver
		self.Surface_act_type = surface_act_type
		import copy
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy

class Other(Segment):
	def __init__(self, id, span, receiver, surface_act_type, Resources, Preferences):
		Segment.__init__(self, id, span)
		self.Receiver = receiver
		self.Surface_act_type = surface_act_type
		import copy
		self.Resources = copy.deepcopy(Resources)
		self.Preferences = copy.deepcopy(Preferences)
		del copy
	
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
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

# Edu part:
sd1 = Span(1, 117)
sd2 = Span(118, 201)

sr1 = Span(140, 144)
sr2 = Span(187, 191)

vr1 = VerbalizedResource(1006, sr1, 'Givable', 'clay', '3')

vr2 = VerbalizedResource(1007, sr2, 'Receivable', 'wood', '?')

d11 = Die_roll('p1', [2, 4])
d12 = Die_roll('p2', [1, 6])

d21 = Die_roll('p1', [1, 3])
d31 = Die_roll('p3', [2, 6])

ex2 = Exchange('p1', 'p3', vr1, vr2)

r111 = Resource(1001, 'clay', '2')
r112 = Resource(1002, 'sheep', '1')
r121 = Resource(1003, 'wheat', '4')
r211 = Resource(1004, 'clay', '3')
r311 = Resource(1005, 'wood', '1')

g11 = Get('p1', [r111, r112])
g12 = Get('p2', [r121])

g21 = Get('p1', [r211])
g31 = Get('p3', [r311])

t1 = Trade([g11, g12], [d11, d12], None)
t2 = Trade([g21], [d21], ex2)
t3 = Trade([g31], [d31], None)

# To complete the initialization of the Turn objects (hence, Segment and State objects).

ss111 = Span(5, 56)
ss112 = Span(57, 78)
ss113 = Span(78, 82)
ss121 = Span(96, 108)
ss122 = Span(109, 117)
ss211 = Span(124, 132)
ss221 = Span(139, 145)
ss222 = Span(146, 161)
ss231 = Span(168, 174)
ss241 = Span(183, 191)
ss242 = Span(192, 201)

st11 = Span(1, 82)
st12 = Span(83, 117)

st21 = Span(118, 132)
st22 = Span(133, 161)
st23 = Span(162, 174)
st24 = Span(175, 201)

vr1111 = vr2
vr1112 = vr1

sevr111 = Several_resources(99111, [vr1111, vr1112], 'OR')

se111 = Offer(9111, ss111, 'p2', 'Question', [sevr111], [])
se112 = Other(9112, ss112, 'p2', 'Assertion', [], [])
se113 = Other(9113, ss113, 'p2', 'Assertion', [], [])

se121 = Accept(9121, ss121, 'p1', 'Assertion', [], [])
se122 = Other(9122, ss122, 'p1', 'Assertion', [], [])

vr2111 = vr1
vr2311 = vr2

sr3 = Span(168, 174)

vr2312 = VerbalizedResource(12312, sr3, 'Possessed', 'wheat', '?')

sp1 = Span(142, 145)

pr2211 = VerbalizedPreference(22211, sp1)

se211 = Strategic_comment(9211, ss211, 'p3', 'Assertion', [vr2111], [])
se221 = Other(9221, ss221, 'p1', 'Assertion', [], [pr2211])
se222 = Other(9222, ss222, 'p1', 'Assertion', [], [])
se231 = Offer(9231, ss231, 'p3', 'Question', [vr2311, vr2312], [])
se241 = Accept(9241, ss241, 'p1', 'Assertion', [], [])
se242 = Other(9242, ss242, 'p1', 'Assertion', [], [])

rs111 = Resource(1011, 'clay', '0')
rs112 = Resource(1012, 'ore', '1')
rs113 = Resource(1013, 'sheep', '2')
rs114 = Resource(1014, 'wheat', '0')
rs115 = Resource(1015, 'wood', '0')

rs121 = Resource(1021, 'clay', '3')
rs122 = Resource(1022, 'ore', '0')
rs123 = Resource(1023, 'sheep', '0')
rs124 = Resource(1024, 'wheat', '1')
rs125 = Resource(1025, 'wood', '0')

rs211 = Resource(2011, 'clay', '0')
rs212 = Resource(2012, 'ore', '3')
rs213 = Resource(2013, 'sheep', '1')
rs214 = Resource(2014, 'wheat', '2')
rs215 = Resource(2015, 'wood', '0')

rs221 = Resource(2021, 'clay', '0')
rs222 = Resource(2022, 'ore', '3')
rs223 = Resource(2023, 'sheep', '2')
rs224 = Resource(2024, 'wheat', '4')
rs225 = Resource(2025, 'wood', '1')

rs231 = Resource(2031, 'clay', '2')
rs232 = Resource(2032, 'ore', '1')
rs233 = Resource(2033, 'sheep', '0')
rs234 = Resource(2034, 'wheat', '0')
rs235 = Resource(2035, 'wood', '2')

rs241 = Resource(2031, 'clay', '2')
rs242 = Resource(2032, 'ore', '1')
rs243 = Resource(2033, 'sheep', '0')
rs244 = Resource(2034, 'wheat', '0')
rs245 = Resource(2035, 'wood', '2')

dev111 = Development(3111, 'roads', '1')
dev121 = Development(3121, 'settlements', '2')
dev211 = Development(3211, 'roads', '2')
dev212 = Development(3212, 'cities', '1')
dev221 = Development(3221, 'cities', '1')
dev222 = Development(3222, 'settlements', '2')
dev231 = Development(3231, 'roads', '2')
dev232 = Development(3232, 'cities', '1')
dev241 = Development(3241, 'settlements', '3')
dev242 = Development(3242, 'cities', '1')

stat11 = State([rs111, rs112, rs113, rs114, rs115], [dev111])
stat12 = State([rs121, rs122, rs123, rs124, rs125], [dev121])
stat21 = State([rs211, rs212, rs213, rs214, rs215], [dev211, dev212])
stat22 = State([rs221, rs222, rs223, rs224, rs225], [dev221, dev222])
stat23 = State([rs231, rs232, rs233, rs234, rs235], [dev231, dev232])
stat24 = State([rs241, rs242, rs243, rs244, rs245], [dev241, dev242])

tu11 = Turn(11, st11, [se111, se112, se113], 'p1', '00:00:00:000', 1, stat11, '')
tu12 = Turn(12, st12, [se121, se122], 'p2', '00:00:00:001', 2, stat12, '')

tu21 = Turn(21, st21, [se211], 'p1', '00:00:00:002', 3, stat21, '')
tu22 = Turn(22, st22, [se221, se222], 'p3', '00:00:00:003', 4, stat22, '')
tu23 = Turn(23, st23, [se231], 'p1', '00:00:00:004', 5, stat23, '')
tu24 = Turn(24, st24, [se241, se242], 'p3', '00:00:00:005', 6, stat24, '')


ar2 = Relation('Anaphora', vr2111, vr2312)

dial1 = Dialogue(1, sd1, [tu11, tu12], ['p1', 'p2'], [t1], [])

dial2 = Dialogue(2, sd2, [tu21, tu22, tu23, tu24], ['p1', 'p3'], [t2, t3], [ar2])

g = Game(['p1', 'p2', 'p3'], [dial1, dial2])

# Discourse part:

rr111 = Relation('Comment', se112, se113)
rr222 = Relation('Narration', se221, se222)

rr22421 = Relation('Continuation', se241, se242)
rr22422 = Relation('Background', se242, se241)

cse1 = Complex_segment(771, [se112, se113], [rr111])
cse21 = Complex_segment(7721, [se221, se222], [rr222])
cse23 = Complex_segment(7723, [se241, se242], [rr22421, rr22422])

rr2222 = Relation('Acknowledgement', se231, cse23)

cse22 = Complex_segment(7722, [se231, cse23], [rr2222])

rr11 = Relation('Elaboration', se111, cse1)
rr12 = Relation('Result', cse1, se121)
rr13 = Relation('Continuation', se121, se122)
rr14 = Relation('Explanation', se111, se122)

rr21 = Relation('Q-Elab', se211, cse21)
rr22 = Relation('Clarification_question', cse21, cse22)
rr23 = Relation('QAP', se211, cse22)

ds1 = Discourse_structure(8881, [se111, cse1, se121, se122], [rr11, rr12, rr13, rr14])

ds2 = Discourse_structure(8882, [se211, cse21, cse22], [rr21, rr22, rr23])

print g.Dialogues[1].Turns[2].State.Developments[0].Amount
print ds2.Full_Discourse_relations[1].Full_Left_argument.Full_Discourse_units[1].Surface_act_type

