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
	-- 'Text_span': string
-- a "Segment" instance contains zero, one or several "Resource" object instances
	-- a "Resource" object has the following attributes:
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
		
# We should be doing it bottom up, from the most detailed classes to the most "enclosing" ones!


import csv, sys, codecs
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime, time
from prettifyxml import prettify

root = Element('annotations', {'version':'1.0', 'encoding':'UTF-8', 'standalone':'no'})
root.append(Comment('Generated by csvtoglozz.py'))

incsvfile = codecs.open(sys.argv[1], 'rt')
csvreader = csv.reader(incsvfile, delimiter='\t')
firstcsvrow = csvreader.next()
dialoguetext = ' ' # for the .ac file
i=0
nb_dialogues = 0
dialog_leftborders = []
dialog_rightborders = []
csvrows = []
r_old = 0
for csvrow in csvreader:
	csvrows.append(csvrow)
for r in range(0,len(csvrows)):
	i += 1
	if csvrows[r] != firstcsvrow:
		[curr_turn_id, curr_turn_timestamp, curr_turn_emitter, curr_turn_res, curr_turn_builds, curr_turn_text, curr_turn_annot, curr_turn_comment] = csvrows[r]
	if curr_turn_emitter != "Server":
		dialoguetext +=curr_turn_id+' : '+curr_turn_emitter+' : '
		seg_leftborders = [len(dialoguetext)-1]
		seg_rightborders = [] # For dealing with ampersands which stand for segments' right borders
		# .ac buffer
		dialoguetext +=curr_turn_text+' '
		#dialog_leftborders = [0]
		#dialog_rightborders = [len(dialoguetext)-1]
		nosegs = 1
		for d in dialoguetext:
			if d == '&':
				nosegs += 1
				seg_rightborders.append(dialoguetext.index(d))
				if len(seg_rightborders) >= 1:
					seg_leftborders.append(seg_rightborders[-1])
				dialoguetext = dialoguetext[:dialoguetext.index(d)]+dialoguetext[dialoguetext.index(d)+1:]
		seg_rightborders.append(len(dialoguetext)-1)
		for t in curr_turn_text:
			if t == '&':
				curr_turn_text = curr_turn_text[:curr_turn_text.index(t)]+curr_turn_text[curr_turn_text.index(t)+1:]
		# .aa typographic annotations
		typunit = SubElement(root, 'unit', {'id':'stac_'+str(-i)})
		typmetadata = SubElement(typunit, 'metadata')
		typauthor = SubElement(typmetadata, 'author')
		typauthor.text='stac'
		typcreation_date = SubElement(typmetadata, 'creation-date')
		typcreation_date.text = str(-i)
		typlast_modif = SubElement(typmetadata, 'lastModifier')
		typlast_modif.text = 'n/a'
		typlast_modif_date = SubElement(typmetadata, 'lastModificationDate')
		typlast_modif_date.text = '0'
		typcharact = SubElement(typunit, 'characterisation')
		typeltype = SubElement(typcharact, 'type')
		typeltype.text = 'paragraph'
		typelfset = SubElement(typcharact, 'featureSet')
		typpos = SubElement(typunit, 'positioning')
		typstartpos = SubElement(typpos, 'start')
		if dialoguetext.index(curr_turn_text) != 0:
			typactualstpos = SubElement(typstartpos, 'singlePosition', {'index':str(len(dialoguetext)-len(curr_turn_text)-len(curr_turn_id)-len(curr_turn_emitter)-1-6)})
		else:
			typactualstpos = SubElement(typstartpos, 'singlePosition', {'index':str(0)})
		typendpos = SubElement(typpos, 'end')
		typactualendpos = SubElement(typendpos, 'singlePosition', {'index':str(len(dialoguetext)-1)})
		# .aa actual pre-annotations (Turn ID, Timestamp, Emitter)
		# a "Dialogue" Unit should be added, that is, Turns between Server's contributions containing "rolled"
		unit = SubElement(root, 'unit', {'id':'stac_'+str(int(time.mktime(datetime.datetime.now().timetuple())+i))})
		metadata = SubElement(unit, 'metadata')
		author = SubElement(metadata, 'author')
		author.text='stac'
		creation_date = SubElement(metadata, 'creation-date')
		creation_date.text = str(int(time.mktime(datetime.datetime.now().timetuple())+i))
		last_modif = SubElement(metadata, 'lastModifier')
		last_modif.text = 'n/a'
		last_modif_date = SubElement(metadata, 'lastModificationDate')
		last_modif_date.text = '0'
		charact = SubElement(unit, 'characterisation')
		eltype = SubElement(charact, 'type')
		eltype.text = 'Turn'
		elfset = SubElement(charact, 'featureSet')
		elfID = SubElement(elfset, 'feature', {'name':'Identifier'})
		elfID.text = curr_turn_id
		elfTimestamp = SubElement(elfset, 'feature', {'name':'Timestamp'})
		elfTimestamp.text = curr_turn_timestamp
		elfEmitter = SubElement(elfset, 'feature', {'name':'Emitter'})
		elfEmitter.text = curr_turn_emitter
		elfResources = SubElement(elfset, 'feature', {'name':'Resources'})
		elfResources.text = curr_turn_res.split("; unknown=")[0]
		elfBuildups = SubElement(elfset, 'feature', {'name':'Developments'})
		# To parse and (re)present in a suitable manner !
		curr_parsed_turn_builds = ""
		if len(curr_turn_builds) > 0:
			for item in curr_turn_builds.split("];"):
				if ']' not in item:
					item += ']'
				curr_parsed_turn_builds += item.split("=")[0]
				curr_parsed_turn_builds += "="
				curr_parsed_turn_builds += str(len(set(eval(item.split("=")[1].replace("; ", ",")))))
				curr_parsed_turn_builds += "; "
		curr_parsed_turn_builds = curr_parsed_turn_builds.strip("; ")
		#print curr_parsed_turn_builds
		elfBuildups.text = curr_parsed_turn_builds
		elfComments = SubElement(elfset, 'feature', {'name':'Comments'})
		elfComments.text = 'Please write in remarks...'
		pos = SubElement(unit, 'positioning')
		startpos = SubElement(pos, 'start')
		if dialoguetext.index(curr_turn_text) != 0:
			actualstpos = SubElement(startpos, 'singlePosition', {'index':str(len(dialoguetext)-len(curr_turn_text)-len(curr_turn_id)-len(curr_turn_emitter)-1-6)})
		else:
			actualstpos = SubElement(startpos, 'singlePosition', {'index':str(0)})
		endpos = SubElement(pos, 'end')
		actualendpos = SubElement(endpos, 'singlePosition', {'index':str(len(dialoguetext)-1)})
		# Segments information
		print seg_leftborders
		print seg_rightborders
		print nosegs
		print csvrows[r]
		print "##"
		if len(seg_leftborders) == len(seg_rightborders):
			for k in range(0,len(seg_leftborders)):
				segment = SubElement(root, 'unit', {'id':'stac_'+str(int(time.mktime(datetime.datetime.now().timetuple())+10000+k))})
				smetadata = SubElement(segment, 'metadata')
				sauthor = SubElement(smetadata, 'author')
				sauthor.text='stac'
				screation_date = SubElement(smetadata, 'creation-date')
				screation_date.text = str(int(time.mktime(datetime.datetime.now().timetuple())+10000*i+k))
				slast_modif = SubElement(smetadata, 'lastModifier')
				slast_modif.text = 'n/a'
				slast_modif_date = SubElement(smetadata, 'lastModificationDate')
				slast_modif_date.text = '0'
				scharact = SubElement(segment, 'characterisation')
				seltype = SubElement(scharact, 'type')
				seltype.text = 'Segment'
				selfset = SubElement(scharact, 'featureSet')
				spos = SubElement(segment, 'positioning')
				sstartpos = SubElement(spos, 'start')
				sactualstpos = SubElement(sstartpos, 'singlePosition', {'index':str(seg_leftborders[k]+1)})
				sendpos = SubElement(spos, 'end')
				sactualendpos = SubElement(sendpos, 'singlePosition', {'index':str(seg_rightborders[k])})
	if curr_turn_emitter == "Server" and "rolled a" in curr_turn_text: # dialogue right boundary
	# hence, a dialogue is between the beginning and such a text (minus server's turns), or between such a text + 1 and another such text (minus server's turns).
		dice_rollings = []
		gets = []
		trades = ''
		#trades = []
		for rr in range(r+1,len(csvrows)):
			if csvrows[rr][2] == 'Server':
				if 'rolled a' in csvrows[rr][5]:
					# append to Dice_rolling feature values
					dice_rollings.append(csvrows[rr][5])
				if 'gets' in csvrows[rr][5]:
					# append to Gets feature values
					gets.append(csvrows[rr][5])
			else:
				break
		print "r_old : " + str(r_old)
		for rrr in range(r, r_old-1, -1):
			if csvrows[rrr][2] == 'Server' and 'traded' in csvrows[rrr][5]:
				# append to Trades feature values
				trades = csvrows[rrr][5]
				break
#		print nb_dialogues
		print dialog_leftborders
		print dialog_rightborders
		r_old = r
		if nb_dialogues == 0:
			dialog_leftborders = [0]
			dialog_rightborders = [len(dialoguetext)-1]
		else:
			dialog_leftborders.append(dialog_rightborders[-1])
			dialog_rightborders.append(len(dialoguetext)-1)
		nb_dialogues += 1
		# Generate the actual annotation !
		if dialog_leftborders[-1] != dialog_rightborders[-1]:
			dialogue = SubElement(root, 'unit', {'id':'stac_'+str(int(time.mktime(datetime.datetime.now().timetuple())+100000+nb_dialogues))})
			dmetadata = SubElement(dialogue, 'metadata')
			dauthor = SubElement(dmetadata, 'author')
			dauthor.text='stac'
			dcreation_date = SubElement(dmetadata, 'creation-date')
			dcreation_date.text = str(int(time.mktime(datetime.datetime.now().timetuple())+100000*i+nb_dialogues))
			dlast_modif = SubElement(dmetadata, 'lastModifier')
			dlast_modif.text = 'n/a'
			dlast_modif_date = SubElement(dmetadata, 'lastModificationDate')
			dlast_modif_date.text = '0'
			dcharact = SubElement(dialogue, 'characterisation')
			deltype = SubElement(dcharact, 'type')
			deltype.text = 'Dialogue'
			delfset = SubElement(dcharact, 'featureSet')
			delfDiceroll = SubElement(delfset, 'feature', {'name':'Dice_rolling'})
			delfDiceroll.text = curr_turn_text
			# extra rollings
			if len(dice_rollings) >= 1:
				for roll in range(0,len(dice_rollings)):
					delfDiceroll.text += ' '+dice_rollings[roll]
			delfGets = SubElement(delfset, 'feature', {'name':'Gets'})
			delfGets.text = ''
			# extra gets
			if len(gets) >= 1:
				for get in range(0,len(gets)):
					delfGets.text += ' '+gets[get]
			delfTrades = SubElement(delfset, 'feature', {'name':'Trades'})
			delfTrades.text = ''
			# extra trades
			#if len(trades) >= 1:
			#	for trade in range(0,len(trades)):
			#		delfTrades.text += ' '+trades[trade]
			delfTrades.text = trades
			dpos = SubElement(dialogue, 'positioning')
			dstartpos = SubElement(dpos, 'start')
			dactualstpos = SubElement(dstartpos, 'singlePosition', {'index':str(dialog_leftborders[-1])})
			dendpos = SubElement(dpos, 'end')
			dactualendpos = SubElement(dendpos, 'singlePosition', {'index':str(dialog_rightborders[-1])})
# last dialogue : only if it doesn't end in a Server's statement !!

if len(dialog_rightborders) == 0 or dialog_rightborders[-1] != len(dialoguetext)-1:
	dialogue = SubElement(root, 'unit', {'id':'stac_'+str(int(time.mktime(datetime.datetime.now().timetuple())+100000+nb_dialogues+1))})
	dmetadata = SubElement(dialogue, 'metadata')
	dauthor = SubElement(dmetadata, 'author')
	dauthor.text='stac'
	dcreation_date = SubElement(dmetadata, 'creation-date')
	dcreation_date.text = str(int(time.mktime(datetime.datetime.now().timetuple())+100000*i+nb_dialogues+1))
	dlast_modif = SubElement(dmetadata, 'lastModifier')
	dlast_modif.text = 'n/a'
	dlast_modif_date = SubElement(dmetadata, 'lastModificationDate')
	dlast_modif_date.text = '0'
	dcharact = SubElement(dialogue, 'characterisation')
	deltype = SubElement(dcharact, 'type')
	deltype.text = 'Dialogue'
	delfset = SubElement(dcharact, 'featureSet')
	dpos = SubElement(dialogue, 'positioning')
	dstartpos = SubElement(dpos, 'start')
	if len(dialog_leftborders) >= 1:
		dactualstpos = SubElement(dstartpos, 'singlePosition', {'index':str(dialog_leftborders[-1])})
	else:
		dactualstpos = SubElement(dstartpos, 'singlePosition', {'index':str(0)})
	dendpos = SubElement(dpos, 'end')
	dactualendpos = SubElement(dendpos, 'singlePosition', {'index':str(len(dialoguetext))})
for b in range(0,len(dialog_leftborders)):
	print ">>>>>>>>>>>"
	print dialoguetext[dialog_leftborders[b]:dialog_rightborders[b]]
	print "<<<<<<<<<<<"
outtxtfile = codecs.open(sys.argv[1].split(".")[0]+".ac", "w")
outtxtfile.write(dialoguetext)
outtxtfile.close()
outxmlfile = codecs.open(sys.argv[1].split(".")[0]+".aa", "w", "ascii")
outxmlfile.write(prettify(root))
outxmlfile.close()
