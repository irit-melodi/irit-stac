#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Eric Kow
# License: BSD3

"""
Populate the Trello STAC annotation workflow API
"""

import argparse
import collections
import codecs
import copy
import itertools
import os.path
import subprocess
import sys

from educe import stac, util
from educe.annotation import Span
from educe.stac import postag, corenlp

import trello as tr
import secrets # api-key, etc, not for revision control

board_id='52453e3d9f6437111f001775'

# secrets needs two values
# apikey=... # see https://trello.com/1/appKey/generate#
# token=...  # generate the private token URL via
#            # http://pythonhosted.org/trello/examples.html
#            # then visit in your web browser to approve
#            # and paste in the resulting token

# ---------------------------------------------------------------------
# args
# ---------------------------------------------------------------------

arg_parser = argparse.ArgumentParser(description='Dump EDU text' )
arg_parser.add_argument('idir', metavar='DIR',
                        help='Input directory'
                        )
educe_group = arg_parser.add_argument_group('corpus filtering arguments')
util.add_corpus_filters(educe_group, fields=[ 'doc' ])
args=arg_parser.parse_args()
args.subdoc    = None
args.stage     = 'unannotated'
args.annotator = None
is_interesting=util.mk_is_interesting(args)

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

reader     = stac.Reader(args.idir)
anno_files = reader.filter(reader.files(), is_interesting)

trello  = tr.TrelloApi(secrets.apikey, secrets.token)
board   = trello.boards.get(board_id)
columns = trello.boards.get_list(board_id)
cards   = trello.boards.get_card(board_id)
subdocs = collections.defaultdict(list)
for k in anno_files:
    subdocs[k.doc].append(k.subdoc)
for d in subdocs:
    subdocs[d] = sorted(subdocs[d])

annotated_ = filter(lambda x:x['name'] == 'Annotated', columns)
if not annotated_:
    raise Exception("Can't find the annotated column")
annotated_id=annotated_[0]['id']

# ensure that each document is associated with a card
doc_cards = {}
for c in cards:
    d = c['name']
    if d in subdocs:
        doc_cards[d] = c
for d in subdocs:
    if d not in doc_cards:
        nc = trello.cards.new(d,annotated_id)
        doc_cards[d] = nc

states = [ 'Reviewed', 'Verified', 'Approved' ]
# create checklist items for reviewed/verified/approved
for d in subdocs:
    card_id     = doc_cards[d]['id']
    checklists  = trello.cards.get_checklist(card_id)
    state_lists = {}
    for c in checklists:
        st = c['name']
        if st in states:
            state_lists[st] = c
    for st in states:
        if st not in state_lists:
            c = trello.checklists.new(st, board_id)
            trello.cards.new_checklist(card_id, c['id'])
            state_lists[st] = c

    for st in states:
        clist         = state_lists[st]
        known_subdocs = [ item['name'] for item in clist['checkItems'] ]
        for sd in subdocs[d]:
            if sd not in known_subdocs:
                trello.checklists.new_checkItem(clist['id'], sd)
