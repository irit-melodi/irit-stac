#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The program takes as input a CSV file with segmentation information
(i.e. "&" after each segment but the last in each turn) and splits it in several parts, so that:
        - each part completely encloses dialogues,
        - the parts are as evenly split as possible
        - the parts are small (i.e. they open nicely in Glozz)
        - if a player rolls a 7, no splitting is performed.

Hence, each game is split in around 10 parts, but in practice, given the rules above, this comes down to 11 to 12 parts.

Each part contains at least one complete dialogue.
Each part may contain several dialogues, esp. when the dialogues are small (like, 1-5 turns).

The program outputs several CSV files, obtained according to the rules above.
The names of these files are formed by appending '_'<slice number> to the initial CSV file basename, and then appending the extension of the initial CSV file.

Example: for csvfile.soclog.seg.csv as input file name,
        csvfile_1.soclog.seg.csv to csvfile_12.soclog.seg.csv are obtained.

Usage:
>>> ./splitcsv.py <input CSV file name>

'''
import csv, sys, codecs
import math
import os.path

incsvfile = codecs.open(sys.argv[1], 'rt')
csvreader = csv.reader(incsvfile, delimiter='\t')
lcsvreader = list(csvreader)
incsvfile.close()
nb_dialogues = 1 # There always is at least one dialogue in a conversation. Moreover, the last dialogue is not ennded with a dice rolling.
nb_turns = 0

for csvrow in lcsvreader[1:]:
        [curr_turn_id, curr_turn_timestamp, curr_turn_emitter, curr_turn_res, curr_turn_builds, curr_turn_text, curr_turn_annot, curr_turn_comment] = csvrow
        if curr_turn_emitter == 'Server' and 'rolled a' in curr_turn_text: # Dialogue ending
                nb_dialogues += 1
        if curr_turn_emitter != 'Server':
                nb_turns += 1

#print nb_turns
#print nb_dialogues

size_limit = nb_turns / 10

nb_dialogues = 1 # There always is at least one dialogue in a conversation. Moreover, the last dialogue is not ennded with a dice rolling.
nb_turns = 0
curr_csv = 1
discard_lines = []
chunks        = []
current_chunk = []

for csvrow in lcsvreader[1:]:
        [curr_turn_id, curr_turn_timestamp, curr_turn_emitter, curr_turn_res, curr_turn_builds, curr_turn_text, curr_turn_annot, curr_turn_comment] = csvrow
        if nb_turns <= size_limit:
                if discard_lines != []:# and nb_turns == 0:
                        discard_lines.pop()
                        pass
                else:
                        current_chunk.append(csvrow)
                nb_turns += 1
        elif curr_turn_emitter != 'Server' or (curr_turn_emitter == 'Server' and ('trade' in curr_turn_text or 'built' in curr_turn_text)):
                # should continue until the whole dialogue is "absorbed"
                current_chunk.append(csvrow)
        elif curr_turn_emitter == 'Server' and 'rolled a' in curr_turn_text:
                current_chunk.append(csvrow)
                ##
                i = 1
                while lcsvreader[lcsvreader.index(csvrow)+i][2] == 'Server' :
                        current_chunk.append(lcsvreader[lcsvreader.index(csvrow)+i])
                        discard_lines.append(True)
                        i += 1
                ##
                #for i in range(1,4):
                #        if lcsvreader[lcsvreader.index(csvrow)+i][2] == 'Server':
                #                current_chunk.append(lcsvreader[lcsvreader.index(csvrow)+i])
                #                discard_first_line = True
                #        else:
                #                break
                if sum(map(int, curr_turn_text.strip('.').split('rolled a')[1].split('and a'))) == 7:
                        i = 1
                        while lcsvreader[lcsvreader.index(csvrow)+i][2] != 'Server' :
                                current_chunk.append(lcsvreader[lcsvreader.index(csvrow)+i])
                                discard_lines.append(True)
                                i += 1
                else:
                        chunks.append(current_chunk)
                        current_chunk = []
                        curr_csv += 1
                        nb_turns = 0
        else:
                #not_first_dialogue = True
                #old_csvrow = csvrow
                chunks.append(current_chunk)
                current_chunk = []
                curr_csv += 1
                nb_turns = 0

# pre-pending the csv header !
csvheader  = ['ID', 'Timestamp', 'Emitter', 'Resources', 'Buildups', 'Text', 'Annotation', 'Comment']
num_chunks = len(chunks)
chunk_digits = int(math.ceil(math.log10(num_chunks)))
print num_chunks, chunk_digits
def mk_filename(i):
    base   = sys.argv[1].split(".")[0]
    subdoc = str(i).zfill(chunk_digits)
    return base + "_" + subdoc + ".soclog.seg.csv"

csv_counter = 1
for c in chunks: # N files for each game !
        outcsvfile = open(mk_filename(csv_counter),"w")
        outcsv=csv.writer(outcsvfile, delimiter="\t", dialect='excel')
        outcsv.writerow(csvheader)
        for curr_csvline in c:
                outcsv.writerow(curr_csvline)
        outcsvfile.close()
        csv_counter = csv_counter + 1
