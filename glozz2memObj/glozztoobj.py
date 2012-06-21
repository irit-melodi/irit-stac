#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Now, we want to parse the GLOZZ annotation into an internal object representation, with the following features:

-- a game is an instance of a "Game" object, with the following attributes:
	-- 'Players': list % of strings
	-- 'Dialogues': list % of Dialogue.IDs
-- a "Game" object instance contains several "Dialogue" object instances
-- a "Dialogue" object instance has the following attributes:
	-- 'ID': number
	-- 'Span': "Span" instance
		* a "Span" object has the following attributes:
			-- 'Start_pos': number
			-- 'End_pos': number
	-- 'Turns': list % of Turn.IDs
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
-- a "Dialogue" object instance contains several "Turn" object instances
-- a "Turn" object instance has the following attributes:
	-- 'ID': number
	-- 'Span': "Span" instance
	-- 'Segments': list % of Segment.IDs
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
-- a "Turn" instance contains several "Segment" object instances
-- a "Segment" instance has the following attributes:
	-- 'ID': number
	-- 'Receiver': string
	-- 'Surface_act_type': string
	-- 'Resources': list % of Resource.IDs; can be []
	-- 'Preferences': list % of Preference.IDs; can be []
	-- 'Span': "Span" instance
-- a "Segment" instance contains zero, one or several "Resource" object instances
	-- an "VerbalizedResource" object which inherits the "Resource" class and has the following attributes:
		-- 'ID': number
		-- 'Span': "Span" instance
		-- 'Status': string
		-- 'Kind': string
		-- 'Quantity': string
-- a "Segment" instance contains zero, one or several "Preference" object instances
	-- a "Preference" object has the following attributes:
		-- 'ID': number
		-- 'Span': "Span" instance
'''
class Game(object):
	def __init__(self, players, dialogues):
		import copy
		copy.deepcopy(self.__Players, players)
		copy.deepcopy(self.__Dialogues, dialogues)
		del copy
	@property
	def Players(self):
		return self.__Players
	@Players.setter
	def Players(self, liste):
		if not isinstance(liste, list):
			raise TypeError("Game.Players:: Error: must be a list!")
		import copy
		copy.deepcopy(self.__Players, liste)
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
		copy.deepcopy(self.__Dialogues, liste)
		del copy
	@Dialogues.deleter
	def Dialogues(self):
		raise TypeError("Game.Dialogues:: Error: cannot delete property!")

class Dialogue(object):
	def __init__(self, id, span, turns, players, Trades):
		self.__ID = id
		self.__Span = span
		import copy
		copy.deepcopy(self.__Turns, turns)
		copy.deepcopy(self.__Players, players) 
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
		copy.deepcopy(self.__Turns, liste)
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
		copy.deepcopy(self.__Players, liste)
		del copy
	@Players.deleter
	def Players(self):
		raise TypeError("Dialogue.Players:: Error: cannot delete property!")

# Add getters and setters for the attributes with are (lists of) other class instances!

class Trade(object):
	def __init__(self, Gets, Dice_rolling, Exchange):
		import copy
		copy.deepcopy(self.Gets, Gets)
		copy.deepcopy(self.Dice_rolling, Dice_rolling)
		del copy
		self.Exchange = Exchange

class Get(object):
	def __init__(self, player, Resources):
		self.__Player = player
		import copy
		copy.deepcopy(self.__Resources, Resources)
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
		copy.deepcopy(self.__Resources, Res)
		del copy
	@Resources.deleter
	def Resources(self):
		self.__Resources = []

class Die_roll(object):
	def __init__(self, player, Dice):
		self.__Player = player
		import copy
		copy.deepcopy(self.__Dice, Dice)
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
		copy.deepcopy(self.__Dice, dicelist)
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
	@From_resource.deleter
	def To_resource(self):
		self.__To_resource = None

class Turn(object):
	def __init__(self, id, span, Segments, emitter, state, comments):
		self.__ID = id
		self.__Span = span
		import copy
		copy.deepcopy(self.__Segments, Segments)
		del copy
		self.Emitter = emitter
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
		raise TypeError("Turn.State:: Error: cannot delete property!")
	# I think what follows is legitimate because each Turn can only have one single State instance
	@property
	def Developments(self): # wrapper of the State object; shortcut to the Developments
		return self.__State.Developments
	@property
	def Resources(self): # wrapper of the State object; shortcut to the Resources
		return self.__State.Resources
		
# We should be doing it bottom up, from the most detailed classes to the most "enclosing" ones!

import sys, codecs
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
