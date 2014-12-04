#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import commands
import itertools
import math
import pprint
import re
import sys

from nltk.tokenize import PunktWordTokenizer as tk
from nltk.stem.wordnet import WordNetLemmatizer as lemm

'''
The purpose of this program is to parse a soclog.txt (cleaned up by Philippe) and to generate a CSV file.
For each line, we want to create a C{Turn} object, to which we associate several information items:
    - ID : an integer
    - timestamp: a string resulting from concatenating a set of integers of the
      form: d*d and d*dd, where 'd' is a digit from 0 to 9 and 'd*' is a digit
      from 1 to 9, with ':', to yield d*d:d*d:d*d:d*dd
    - emitter: a string holding the identifier of the speaker of the turn
    - state: a structure holding two sub-structures:
    - resources: a set of feature:value pairs
    - buildup: a set of feature:coordinates pairs, where 'coordinates' is a pair of values
 -- text: the text of the turn

A CSV file with several fields is generated: ID, timestamp, emitter, state:
resources and buildups (2 separate columns), text, annotation. After a
series of annotations, the 'annotation' column will be split in several
sub-columns:
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
    def parse(self, text):
        """
        Only useful for parsing the Server's turns. Unused in practice.
        The method takes a text as input and initializes the private game-related attributes.
        """
        tokens = []
        dumps = [tokens.append(tk().tokenize(text.split(".")[:-1][i].strip(" "))) for i in range(0,len(text.split(".")[:-1]))]
        #tokens = list(itertools.chain(*tokens))
        if self.emitter == "Server":
            for i in range(0,len(tokens)):
                are_several = False
                is_trade = False
                if (tokens[i][0] != "No" or tokens[i][1] != "player") and tokens[i][1] != "rolled":
                    self.__players.append(tokens[i][0])
                    if tokens[i][3] == u"offer":
                        are_several = True
                        is_trade = False
                        self.__actions.append("offer")
                        self.__items.append("what: "+lemm().lemmatize(tokens[i][7]))
                        self.__items.append("for: "+lemm().lemmatize(tokens[i][10]))
                        if tokens[i][6] in ["a", "an"]:
                            self.__quantities.append("1")
                        else:
                            self.__quantities.append(tokens[i][6])
                        if tokens[i][9] in ["a", "an"]:
                            self.__quantities.append("1")
                        else:
                            self.__quantities.append(tokens[i][9])
                    elif tokens[i][1] == u"traded":
                        are_several = True
                        is_trade = True
                        self.__actions.append("trade")
                        self.__players.append("from: "+tokens[i][8])
                        self.__items.append("what: "+lemm().lemmatize(tokens[i][3]))
                        self.__items.append("for: "+lemm().lemmatize(tokens[i][6]))
                        if tokens[i][2] in ["a", "an"]:
                            self.__quantities.append("1")
                        else:
                            self.__quantities.append(tokens[i][2])
                        if tokens[i][5] in ["a", "an"]:
                            self.__quantities.append("1")
                        else:
                            self.__quantities.append(tokens[i][5])                    
                    else:
                        are_several = False
                        is_trade = False
                        self.__actions.append(lemm().lemmatize(tokens[i][1]))
                        self.__items.append(lemm().lemmatize(tokens[i][3]))
                        if tokens[i][2] in ["a", "an"]:
                            self.__quantities.append("1")
                        else:
                            self.__quantities.append(tokens[i][2])
                        if len(tokens[i]) > 4 and tokens[i][4] == ",":
                            are_several = True
                            self.__items.append(lemm().lemmatize(tokens[i][6]))
                            if tokens[i][5] in ["a", "an"]:
                                self.__quantities.append("1")
                            else:
                                self.__quantities.append(tokens[i][5])
                    if are_several == True and is_trade == False:
                        self.annotations.append(", ".join([self.__players[-1], self.__actions[-1], '; '.join(self.__items[-2:]), '; '.join(self.__quantities[-2:])]))
                    if are_several == True and is_trade == True:
                        self.annotations.append(", ".join(['; '.join(self.__players[-2:]), self.__actions[-1], '; '.join(self.__items[-2:]), '; '.join(self.__quantities[-2:])]))
                    if are_several == False and is_trade == False:
                        self.annotations.append(", ".join([self.__players[-1], self.__actions[-1], self.__items[-1], self.__quantities[-1]]))

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
        '''
        if dialogue.turns[i].emitter == "Server":
            dialogue.turns[i].parse(dialogue.turns[i].text)
            __annotation = "; ".join(dialogue.turns[i].annotations[1:])
        else:
            __annotation = "".join(dialogue.turns[i].annotations)
        '''
        csvline = [dialogue.turns[i].ID.encode("utf-8"), dialogue.turns[i].timestamp.encode("utf-8"), dialogue.turns[i].emitter.encode("utf-8"), "; ".join(dialogue.turns[i].state.resources).encode("utf-8"), "; ".join(dialogue.turns[i].state.buildups).encode("utf-8"), dialogue.turns[i].text.encode("utf-8"), __annotation.encode("utf-8"), ' ']
        outcsv.writerow(csvline)
    outcsvfile.close()
    print "Done.\n"
    return [dialogue.size, dialogue.linguistic_size]

if __name__ == "__main__":
    wikitext2csv(sys.argv[1])
