#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import pprint
import commands,sys
import re,math,itertools

'''
The purpose of this program is to parse a soclog.txt (cleaned up by Philippe) and to generate a CSV file.
For each line, we want to create a C{Turn} object, to which we associate several information items:
	- ID : an integer
	- timestamp: a string resulting from concatenating a set of integers of the form: d*d and d*dd, where 'd' is a digit from 0 to 9 and 'd*' is a digit from 1 to 9, with ':', to yield d*d:d*d:d*d:d*dd
	- emitter: a string holding the identifier of the speaker of the turn
	- state: a structure holding two sub-structures:
	- resources: a set of feature:value pairs
	- buildup: a set of feature:coordinates pairs, where 'coordinates' is a pair of values
 -- text: the text of the turn
A CSV file with several fields is generated: ID, timestamp, emitter, state: resources and buildups (2 separate columns), text, annotation. After a series of annotations, the 'annotation' column will be split in several sub-columns:
	- target
	- surface-level DA (dialogue act)
	- task-specific DA

Usage:
>>> import extract_annot
>>> extract_annot.wikitext2csv(<cleaned-up Soclog filename>)
'''
# We first create the dialogue object, with, for each line: metadata (ID, emitter, state -- resources and buildup), text.

class Dialogue:
	""" This class has two attributes: the number of turns and the list of turns
	"""
	def __init__(self, turns_list):
		linguistic_turns = []
		for turn in turns_list:
			if turn.emitter != "Server":
				linguistic_turns.append(turn)
		self.linguistic_size = str(len(linguistic_turns))
		self.size = str(len(turns_list))
		self.turns = turns_list

class Turn:
	"""This class has five attributes: the ID, timestamp, emitter, state and text
	"""
	def __init__(self, line):
		self.ID = line.split("|")[1]
		self.timestamp = line.split("|")[2]
		self.emitter = line.split("|")[3]
		self.state = State(line.split("|")[4])
		self.text = line.split("|")[5]
		self.__players = []
		self.__actions = []
		self.__items = []
		self.__quantities = []
		self.annotations = [line.split("|")[6]]

class State:
	"""
	Holds the resources and the buildups (called "Developments" in the Guapi).
	"""
	def __init__(self, state_chunk): #state_chunk is actually line.split("|")[4]
		item_list = state_chunk.split(",")
		res_list = []
		build_list = []
		for i in range(0,len(item_list)):
			if re.match(r"[0-9]",item_list[i]):
				build_list.append(item_list[i-1]+","+item_list[i])
			else:
				if "[" not in item_list[i]:
					res_list.append(item_list[i])
		self.resources = res_list[:]
		self.buildups = build_list[:]

def wikitext2csv(filename):
	"""
	Does the actual conversion from cleaned-up Soclogs to CSV files.
	Also returns a list with two elements:
		- the total number of turns.
		- the total number of linguistic turns, i.e. turns excluding those of the Server.
	@param filename: name of the cleaned-up Soclog file.
	@type filename: string.
	@rtype: list of integers: [total number of turns, total number of linguistic turns].
	"""
	print "Processing soclog: "+filename
	dialogue_file = codecs.open(filename, "r", "utf-8")
	lines = dialogue_file.readlines()
	dialogue_file.close()
	turns = []
	for i in range(0,len(lines)):
		if lines[i][0] == "^":
			start_index = i
			break
	for line in lines[start_index + 1:]:
		turn = Turn(line)
		turns.append(turn)
	dialogue = Dialogue(turns)
	#print ">>Total number of turns: "+dialogue.size
	#print ">>Total number of linguistic turns: "+dialogue.linguistic_size
	csvheader = ['ID', 'Timestamp', 'Emitter', 'Resources', 'Buildups', 'Text', 'Annotation', 'Comment']
	import csv
	outcsvfile = open(filename.split("txt")[0]+"csv", "w")
	outcsv=csv.writer(outcsvfile, delimiter="\t", dialect='excel')
	outcsv.writerow(csvheader)
	for i in range(0,int(dialogue.size)):
		__annotation = "".join(dialogue.turns[i].annotations)
		csvline = [dialogue.turns[i].ID.encode("utf-8"), dialogue.turns[i].timestamp.encode("utf-8"), dialogue.turns[i].emitter.encode("utf-8"), "; ".join(dialogue.turns[i].state.resources).encode("utf-8"), "; ".join(dialogue.turns[i].state.buildups).encode("utf-8"), dialogue.turns[i].text.encode("utf-8"), __annotation.encode("utf-8"), ' ']
		outcsv.writerow(csvline)
	outcsvfile.close()
	print "Done.\n"
	return [dialogue.size, dialogue.linguistic_size]

if __name__ == "__main__":
	wikitext2csv(sys.argv[1])
