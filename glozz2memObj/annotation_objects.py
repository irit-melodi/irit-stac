#!/usr/bin/python
# -*- coding: utf-8 -*-

##### CDU-level stuff

class Discourse_unit(object):
	'''
	Represent a generic discourse unit. Its only attribute is a numeric identifier.
	'''
	def __init__(self, id):
		'''
		Set the unique identifier of the unit.
		@param __ID: unique identifier.
		'''
		self.__ID = id
	@property
	def ID(self):
		'''
		Provide public access to the private __ID attribute.
		'''
		return self.__ID

class Segment(Discourse_unit):
	'''
	Represent a generic segment of text. 
	Its attributes are a numeric identifier and a Span object.
	Inherits the Discourse_unit object.
	'''
	def __init__(self, id, span, textfile):
		'''
		Set the unique identifier and the span of the segment.
		@param __ID: unique identifier.
		@param __Span: Span object instance, specifying the object limits in the text.
		'''
		Discourse_unit.__init__(self, id)
		self.__Span = span
		self.__textfile = textfile
	@property
	def Span(self):
		'''
		Provide public access to the private __Span attribute.
		'''
		return self.__Span
	@Span.setter
	def Span(self, span):
		'''
		Public setter of the private __Span attribute. 
		It checks that the input is a Span object instance.
		'''
		if not isinstance(span, Span):
			raise TypeError("Segment.Span:: Error: must be a Span instance!")
		self.__Span = span
	@Span.deleter
	def Span(self):
		'''
		Publicly forbids deleting the __Span private attribute by any mean.
		'''
		raise TypeError("Segment.Span:: Error: cannot delete property!")
	@property
	def Text(self):
		'''
		Provide public access to the text of the segment.
		'''
		import codecs
		_textfile = codecs.open(self.__textfile, "r", "utf-8")
		_text = _textfile.read()
		_textfile.close()
		del codecs
		return _text[self.__Span.Start_pos:self.__Span.End_pos]

class Discourse_structure(Discourse_unit):
	'''
	Represent a generic discourse structure, that is, a directed hypergraph.
	It contains a set of instances which inherit from the Discourse_unit object.
	These objects are either Discourse_structure or Segment instances.
	Also contains a set of relation instances, between discourse units.
	Inherits the Discourse_unit object.
	'''
	def __init__(self, id, DUs, DRs):
		'''
		Sets the list of discourse units and of discourse relations between these.
		@param __Discourse_units: set of Segment and / or Discourse_structure instances.
		@param __Discourse_relations: set of Relation instances.
		'''
		Discourse_unit.__init__(self, id)
		import copy
		self.__Discourse_units = copy.deepcopy(DUs)
		self.__Discourse_relations = copy.deepcopy(DRs)
		del copy
	@property
	def Discourse_units(self):
		'''
		Public accessor to the __ID attribute of the the discourse units in the discourse structure.
		'''
		DU_IDs = []
		for DU in self.__Discourse_units:
			DU_IDs.append(DU.ID)
		return DU_IDs
	@property
	def Full_Discourse_units(self):
		'''
		Public accessor to the complete, inner structure of the discourse units in the discourse structure.
		'''
		return self.__Discourse_units
	@property
	def Discourse_relation_IDs(self):
		'''
		Public accessor to the __ID attribute of the Relation instances in the discourse structure.
		'''
		DR_ids = []
		for DR in self.__Discourse_relations:
			DR_ids.append(DR.ID)
		return DR_ids
	@property
	def Discourse_relations(self):
		'''
		Public accessor to a shallow view of the Relation instances in the discourse structure.
		Returns a list of tuples, one tuple per Relation instance.
		Each such tuple has the form (label, left argument, right argument).
		'''
		DRs = []
		for DR in self.__Discourse_relations:
			DRs.append((DR.Label, DR.Left_argument, DR.Right_argument))
		return DRs
	@property
	def Full_Discourse_relations(self):
		'''
		Public accessor to the complete, inner structure of the Relation instances in the discourse structure.
		'''
		return self.__Discourse_relations
	@property
	def Span(self):
		'''
		Computes and renders accessible the span of a discourse structure.
		This span is computed in terms of the spans of its "borderline" discourse units.
		'''
		left_start = min(int(du.Span.Start_pos) for du in self.__Discourse_units)
		right_start = max(int(du.Span.End_pos) for du in self.__Discourse_units)
		_span = Span(left_start, right_start)
		return _span

class Complex_segment(Discourse_structure):
	'''
	Represent a complex discourse unit (CDU), which is a discourse structure itself.
	Hence, it inherits the Discourse_structure object.
	It provides an extra-check of the CDU cohesion constraint.
	It also provides the concatenated texts of the constituent discourse units.
	'''
	def __init__(self, id, DUs, DRs):
		'''
		First, it checks that the discourse units are not isolated.
		Then, it initializes a Discourse_structure object.
		@param __Discourse_units: set of objects inheriting the Discourse_unit objects: either Complex_segment or Segment instances.
		@param __Discourse_relations: set of Relation instances.
		'''
		# add cohesion checking:
		rel_args = []
		__dump = [rel_args.append(rel.Left_argument) for rel in DRs if rel.Left_argument not in rel_args]
		__dump = [rel_args.append(rel.Right_argument) for rel in DRs if rel.Right_argument not in rel_args]
		for du in DUs:
			if du.ID not in rel_args:
				print "Warning: Complex segment %(CDU)s has islands: sub-unit %(DU)s disconnected!!" % {'CDU': id, 'DU': du.ID}
		del rel_args
		Discourse_structure.__init__(self, id, DUs, DRs)
	@property
	def Text(self):
		_span_text = { }
		_text = ''
		for _du in self.Full_Discourse_units:
			if isinstance(_du, Segment):
				_span_text[int(_du.Span.End_pos)] = _du.Text
			if isinstance(_du, Complex_segment):
				for _edu in _du.Full_Discourse_units:
					_span_text[int(_edu.Span.End_pos)] = _edu.Text
		_span_text_items = _span_text.items()
		_span_text_items.sort(key = lambda _span_text:_span_text[0])
		for _item in _span_text_items:
			_text += _item[1] + ' '
		return _text

class Relation(object):
	'''
	Represent a discourse relation. More generally, this object is an oriented hypergraph edge.
	It is basically characterized by an identifier, a label, a left argument and a right argument.
	'''
	def __init__(self, id, label, larg, rarg, arg_scope, comments):
		'''
		Set the identifier, the label, the left and right arguments of the relation as private attributes.
		Set the public Arg_scope and Comments attributes.
		@param __ID: unique identifier; private attribute.
		@param __Label: label of the relation; private attribute.
		@param __Left_argument: left argument of the relation; of derived Discourse_unit type; private.
		@param __Right_argument: right argument of the relation; of derived Discourse_unit type; private.
		@param Arg_scope: specifies whether the scope of the relation is known ('Specified') or not ('Unspecified'); public.
		@param Comments: string holding annotator comments regarding this relation; public.
		'''
		self.__ID = id
		self.__Label = label
		self.__Left_argument = larg
		self.__Right_argument = rarg
		self.Arg_scope = arg_scope
		self.Comments = comments
	@property
	def ID(self):
		'''
		Public accessor to the private identifier of the relation.
		'''
		return self.__ID
	@property
	def Label(self):
		'''
		Public accessor to the private __Label attribute of the relation.
		'''
		return self.__Label
	@Label.setter
	def Label(self, newlab):
		'''
		Public setter of the private __Label attribute of the relation.
		Allows one to alter the label of an already existing Relation object.
		'''
		self.__Label = newlab
	@property
	def Left_argument(self):
		'''
		Public accessor to the identifier of the private __Left_argument attribute of the relation.
		Provides a shallow access to the left argument of the relation.
		'''
		return self.__Left_argument.ID
	@property
	def Right_argument(self):
		'''
		Public accessor to the identifier of the private __Left_argument attribute of the relation.
		Provides a shallow access to the left argument of the relation.
		'''
		return self.__Right_argument.ID
	@property
	def Full_Left_argument(self):
		'''
		Public accessor to the inner structure of the __Left_argument attribute of the relation.
		This attribute is a derived Discourse_unit, viz. either a Segment or a Complex_segment.
		'''
		return self.__Left_argument
	@property
	def Full_Right_argument(self):
		'''
		Public accessor to the inner structure of the __Right_argument attribute of the relation.
		This attribute is a derived Discourse_unit, viz. either a Segment or a Complex_segment.
		'''
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
	def __init__(self, id, span, Trades=[], turns=[], players=[], Anaphors=[]):
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
	def __init__(self, id, span, Receivers, surface_act_type, textfile):
		Segment.__init__(self, id, span, textfile)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		del copy
		self.Resources = []
		self.Preferences = []
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Counteroffer(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, textfile):
		Segment.__init__(self, id, span, textfile)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		del copy
		self.Resources = []
		self.Preferences = []
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Accept(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, textfile):
		Segment.__init__(self, id, span, textfile)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		del copy
		self.Resources = []
		self.Preferences = []
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Refusal(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, textfile):
		Segment.__init__(self, id, span, textfile)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		del copy
		self.Resources = []
		self.Preferences = []
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Strategic_comment(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, textfile):
		Segment.__init__(self, id, span, textfile)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		del copy
		self.Resources = []
		self.Preferences = []
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)

class Other(Segment):
	def __init__(self, id, span, Receivers, surface_act_type, textfile):
		Segment.__init__(self, id, span, textfile)
		self.Surface_act_type = surface_act_type
		import copy
		self.Receivers = copy.deepcopy(Receivers)
		del copy
		self.Resources = []
		self.Preferences = []
	def addResource(self, newRes):
		self.Resources.append(newRes)
	def addPreference(self, newPref):
		self.Preferences.append(newPref)
	
class VerbalizedResource(Resource):
	def __init__(self, id, span, status, kind, quantity, textfile):
		Resource.__init__(self, id, kind, quantity)
		self.__Span = span
		self.Status = status
		self.__textfile = textfile
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
	@property
	def Text(self):
		'''
		Provide public access to the text of the resource.
		'''
		import codecs
		_textfile = codecs.open(self.__textfile, "r", "utf-8")
		_text = _textfile.read()
		_textfile.close()
		del codecs
		return _text[self.__Span.Start_pos:self.__Span.End_pos]

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
	def __init__(self, id, span, textfile):
		Segment.__init__(self, id, span, textfile)

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
