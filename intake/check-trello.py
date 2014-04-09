#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Eric Kow
# License: BSD3

"""
Populate the Trello STAC annotation workflow API
"""

import collections

import trello as tr
import secrets  # api-key, etc, not for revision control

BOARD_ID = '52453e3d9f6437111f001775'

# secrets needs two values
# apikey=... # see https://trello.com/1/appKey/generate#
# token=...  # generate the private token URL via
#            # http://pythonhosted.org/trello/examples.html
#            # then visit in your web browser to approve
#            # and paste in the resulting token

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------


def card_info(card, names):
    "string representing things we want to know about the card"
    members = ", ".join(names[k] for k in card["idMembers"])
    return card["name"] + (": " + members if members else "")


def main():
    "main"
    trello = tr.TrelloApi(secrets.apikey, secrets.token)
    columns = trello.boards.get_list(BOARD_ID)
    cards = trello.boards.get_card(BOARD_ID)
    owned = collections.defaultdict(list)
    names = {}
    for member in trello.boards.get_member(BOARD_ID):
        names[member["id"]] = member["fullName"]
    for card in cards:
        columnId = card["idList"]
        game = card_info(card, names)
        owned[columnId].append(game)
    for column in columns:
        columnName = column["name"]
        columnId = column["id"]
        print columnName
        print "-" * len(columnName)
        print "\n".join(owned[columnId])
        print

main()
