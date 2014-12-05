#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=invalid-name
# pylint: enable=invalid-name
# pylint: disable=too-few-public-methods

'''
The purpose of this program is to parse a soclog.txt (cleaned up by Philippe)
and to generate a CSV file.

For each line, we want to create a C{Turn} object, to which we associate
several information items:
    - ID : an integer
    - timestamp: a string resulting from concatenating a set of integers of the
      form: d*d and d*dd, where 'd' is a digit from 0 to 9 and 'd*' is a digit
      from 1 to 9, with ':', to yield d*d:d*d:d*d:d*dd
    - emitter: a string holding the identifier of the speaker of the turn
    - resources: a set of feature:value pairs
    - buildup: a set of feature:coordinates pairs, where 'coordinates' is a
      pair of values
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

from __future__ import print_function
import codecs
import csv
import re
import sys

from educe.stac.util import csv as stac_csv
from educe.stac.util.csv import Turn


# We first create the dialogue object, with, for each line: metadata (ID,
# emitter, state -- resources and buildup), text.


def parse_row(line):
    """
    interpret a row in the intermediary 'wiki' format ::

        String -> Turn
    """
    fields = line.split('|')
    item_list = fields[4].split(",")
    res_list = []
    build_list = []
    # reformat resources and buildouts
    # (this should really be rewritten in a cleaner way)
    # for developments, given a list foo=[1,2,3,4] bar=[5,6,7]
    # we build foo=[1,2; 2,3; 3,4] bar=[5,6; 6,7]
    for i in range(0, len(item_list)):
        if re.match(r"[0-9]", item_list[i]):
            build_list.append(item_list[i-1]+","+item_list[i])
        elif "[" not in item_list[i]:
            res_list.append(item_list[i])

    return Turn(number=fields[1],
                timestamp=fields[2],
                emitter=fields[3],
                res='; '.join(res_list),
                builds='; '.join(build_list),
                rawtext=fields[5],
                annot=fields[6],
                comment=' ')


def wikitext2csv(filename):
    """
    Does the actual conversion from cleaned-up Soclogs to CSV files.
    Also returns a list with two elements:
        - the total number of turns.
        - the total number of linguistic turns, i.e. turns excluding those of
          the Server.

    :param filename: name of the cleaned-up Soclog file.
    :type filename: string.
    """
    ofilename = filename.split("txt")[0]+"csv"
    with codecs.open(filename, 'r', 'utf-8') as dialogue_file:
        dialogue_file.readline() # skip header
        with open(ofilename, 'w') as output_file:
            outcsv = stac_csv.mk_csv_writer(output_file)
            outcsv.writeheader()
            for line in dialogue_file:
                turn = parse_row(line)
                outcsv.writerow(turn.to_dict())


if __name__ == "__main__":
    wikitext2csv(sys.argv[1])
