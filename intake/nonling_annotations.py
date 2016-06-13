#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automatically adds annotations for non-linguistic events in a game of "Settlers of Catan"
"""

from __future__ import print_function

import xml.etree.ElementTree as ET
import re
import argparse
import codecs
import sys
import os

from csvtoglozz import append_unit, init_mk_id, mk_id
from educe.stac.util.prettifyxml import prettify



# ---------------------------------------------------------------------
# "Units" annotations
# ---------------------------------------------------------------------


def add_units_annotations(tree, text):
    """
    Add units annotations for non-linguistical event
    
    Parameters
    ----------
    tree :
        XML tree extracted from the .aa file to modify
    text : string
        raw text extracted from the .ac file

    Returns
    -------
    root :
        modified XML tree with units annotations for non-linguistical event
    """
    root = tree

    #So I know this is like the ugliest possible way to solve a problem
    #but those offer/trade events can be really tricky
    #and for the moment I really see no other way than
    #considering every possibilities in a exhaustive way...

    Offer11RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer12RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer21RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer13RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer22RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer31RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer14RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer23RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer32RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')
    Offer41RegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood)( from the bank or a port)?\.')

    FromRegEx = re.compile(r'from (.+)')

    Trade11RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade12RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade21RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade13RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade22RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade31RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade14RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade23RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade32RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    Trade41RegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    
    #That's the moment I hope I didn't make any typo...

    RejectRegEx = re.compile(r'(.+) rejected trade offer\.')

    GetRegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood)\.')
    Get2RegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)\.')
    #It is impossible in "Settlers of Catan" to get more than 2 different types of resources with one roll dice.
    #That's why we actually don't need to bother with complex regular expression since there are in fact just two cases to consider. :)

    MonopolyRegEx = re.compile(r'(.+) monopolized (clay|ore|sheep|wheat|wood)\.')


    Trader = ''

    def parseOffer(mo, i, j, start, end, unit, root):
        X = mo.group(1)
        unit.find('characterisation/type').text = 'Offer'
        feats = unit.find('characterisation/featureSet')
        f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
        f_elm1.text = 'Assertion'
        f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
        f_elm2.text = '?'
        #maybe we can shorten this function and make a single loop
        for index in range(1, i+1):
            N = mo.group(2*index)
            R = mo.group(2*index+1)
            if index == 1:
                left = start + len(X) + 24
                right = left + len(N) + 1 + len(R)
            else:
                left = right + 2
                right = left + len(N) + 1 + len(R)
            append_unit(root, 'Resource',
                        [('Status', 'Givable'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R)],
                        left, right)
        for index in range(i+1, i+j+1):
            N = mo.group(2*index)
            R = mo.group(2*index+1)
            if index == i+1:
                left = right + 5
                right = left + len(N) + 1 + len(R)
            else:
                left = right + 2
                right = left + len(N) + 1 + len(R)
            append_unit(root, 'Resource',
                            [('Status', 'Receivable'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R)],
                            left, right)

    def parseTrade(mo, i, j, start, end, unit, root):
        X = mo.group(1)
        Y = mo.group(2*(i+j+1))
        unit.find('characterisation/type').text = 'Accept'
        feats = unit.find('characterisation/featureSet')
        f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
        f_elm1.text = 'Assertion'
        f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
        if Y == 'the bank' or Y == 'a port':
            f_elm2.text = 'All'
        else:
            f_elm2.text = Y
        #maybe we can shorten this function and make a single loop
        for index in range(1, i+1):
            N = mo.group(2*index)
            R = mo.group(2*index+1)
            if index == 1:
                left = start + len(X) + 8
                right = left + len(N) + 1 + len(R)
            else:
                left = right + 2
                right = left + len(N) + 1 + len(R)
            append_unit(root, 'Resource',
                        [('Status', '?'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R)],
                        left, right)
        for index in range(i+1, i+j+1):
            N = mo.group(2*index)
            R = mo.group(2*index+1)
            if index == i+1:
                left = right + 5
                right = left + len(N) + 1 + len(R)
            else:
                left = right + 2
                right = left + len(N) + 1 + len(R)
            append_unit(root, 'Resource',
                        [('Status', 'Possessed'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R)],
                        left, right)
            
    for unit in root:
        if unit.findtext('characterisation/type') == 'NonplayerSegment':
            start = int(unit.find('positioning/start/singlePosition').get('index'))
            end = int(unit.find('positioning/end/singlePosition').get('index'))
            event = text[start:end]

            if Offer11RegEx.search(event) != None: #<X> made an offer to trade <N1> <R1> for <N2> <R2>.
                mo = Offer11RegEx.search(event)
                parseOffer(mo, 1, 1, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer12RegEx.search(event) != None:
                mo = Offer12RegEx.search(event)
                parseOffer(mo, 1, 2, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer21RegEx.search(event) != None:
                mo = Offer21RegEx.search(event)
                parseOffer(mo, 2, 1, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer13RegEx.search(event) != None:
                mo = Offer13RegEx.search(event)
                parseOffer(mo, 1, 3, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer22RegEx.search(event) != None:
                mo = Offer22RegEx.search(event)
                parseOffer(mo, 2, 2, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer31RegEx.search(event) != None:
                mo = Offer31RegEx.search(event)
                parseOffer(mo, 3, 1, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer14RegEx.search(event) != None:
                mo = Offer14RegEx.search(event)
                parseOffer(mo, 1, 4, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer23RegEx.search(event) != None:
                mo = Offer23RegEx.search(event)
                parseOffer(mo, 2, 3, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer32RegEx.search(event) != None:
                mo = Offer32RegEx.search(event)
                parseOffer(mo, 3, 2, start, end, unit, root)
                Trader = mo.group(1)
                continue
            elif Offer41RegEx.search(event) != None:
                mo = Offer41RegEx.search(event)
                parseOffer(mo, 4, 1, start, end, unit, root)
                Trader = mo.group(1)
                continue


            elif Trade11RegEx.search(event) != None: #<X> traded <N1> <R1> for <N2> <R2> from <Y>.
                parseTrade(Trade11RegEx.search(event), 1, 1, start, end, unit, root)
                continue
            elif Trade12RegEx.search(event) != None:
                parseTrade(Trade12RegEx.search(event), 1, 2, start, end, unit, root)
                continue
            elif Trade21RegEx.search(event) != None:
                parseTrade(Trade21RegEx.search(event), 2, 1, start, end, unit, root)
                continue
            elif Trade13RegEx.search(event) != None:
                parseTrade(Trade13RegEx.search(event), 1, 3, start, end, unit, root)
                continue
            elif Trade22RegEx.search(event) != None:
                parseTrade(Trade22RegEx.search(event), 2, 2, start, end, unit, root)
                continue
            elif Trade31RegEx.search(event) != None:
                parseTrade(Trade31RegEx.search(event), 3, 1, start, end, unit, root)
                continue
            elif Trade14RegEx.search(event) != None:
                parseTrade(Trade14RegEx.search(event), 1, 4, start, end, unit, root)
                continue
            elif Trade23RegEx.search(event) != None:
                parseTrade(Trade23RegEx.search(event), 2, 3, start, end, unit, root)
                continue
            elif Trade32RegEx.search(event) != None:
                parseTrade(Trade32RegEx.search(event), 3, 2, start, end, unit, root)
                continue
            elif Trade41RegEx.search(event) != None:
                parseTrade(Trade41RegEx.search(event), 4, 1, start, end, unit, root)
                continue


            elif RejectRegEx.search(event) != None: #<Y> rejected trade offer.
                mo = RejectRegEx.search(event)
                Y = mo.group(1)

                unit.find('characterisation/type').text = 'Refusal'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
                if Trader != '':
                    f_elm2.text = Trader
                else:
                    f_elm2.text = 'All'
                continue

            elif event == "You can't make that trade.":
                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
                if Trader != '':
                    f_elm2.text = Trader
                else:
                    f_elm2.text = 'All'
                continue


            elif GetRegEx.search(event) != None: #<Y> gets <N> <R>.
                mo = GetRegEx.search(event)
                Y = mo.group(1)
                N = mo.group(2)
                R = mo.group(3)

                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
                f_elm2.text = 'All'

                left = start + len(Y) + 6
                right = end - 1
                append_unit(root, 'Resource',
                            [('Status', 'Possessed'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R)],
                            left, right)
                continue

            elif Get2RegEx.search(event) != None: #<Y> gets <N1> <R1>, <N2> <R2>.
                mo = Get2RegEx.search(event)
                Y = mo.group(1)
                N1 = mo.group(2)
                R1 = mo.group(3)
                N2 = mo.group(2)
                R2 = mo.group(3)

                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
                f_elm2.text = 'All'

                left1 = start + len(Y) + 6
                right1 = left1 + len(N1) + 1 + len(R1)
                append_unit(root, 'Resource',
                            [('Status', 'Possessed'), ('Quantity', N1), ('Correctness', 'True'), ('Kind', R1)],
                            left1, right1)
                left2 = right1 + 2
                right2 = left2 + len(N2) + 1 + len(R2)
                append_unit(root, 'Resource',
                            [('Status', 'Possessed'), ('Quantity', N2), ('Correctness', 'True'), ('Kind', R2)],
                            left2, right2)
                continue


            elif MonopolyRegEx.search(event) != None: #<X> monopolized <R>.
                mo = MonopolyRegEx.search(event)
                X = mo.group(1)
                R = mo.group(2)

                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
                f_elm2.text = 'All'

                right = end - 1
                left = right - len(R)
                append_unit(root, 'Resource',
                            [('Status', 'Possessed'), ('Quantity', '?'), ('Correctness', 'True'), ('Kind', R)],
                            left, right,)
                continue

            else:
                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addressee'})
                f_elm2.text = 'All'
                continue

    return root



# ---------------------------------------------------------------------
# "Discourse" annotations
# ---------------------------------------------------------------------



def append_relation(root, utype, global_id1, global_id2):
    """
    Append a new relation level annotation to the given root element.
    Note that this generates a new identifier behind the scenes.

    Parameters
    ----------
    root :
        node of the XML tree to which we want to add a "relation" child
    utype : string
        type of the relation we want to create (sequence, continuation, QAP...)
    global_id1 : string
        global id of the first element (EDU or CDU) of the relation
    global_id2 : string
        global id of the second element (EDU or CDU) of the relation
    """
    unit_id, date = mk_id()

    id1 = global_id1.split('_')
    id2 = global_id2.split('_')

    subdoc1 = id1[1]
    subdoc2 = id2[1]

    if subdoc1 == subdoc2:
        local_id1 = '_'.join([id1[-2], id1[-1]])
        local_id2 = '_'.join([id2[-2], id2[-1]])

        metadata = [('author', 'stac'),
                    ('creation-date', str(date)),
                    ('lastModifier', 'n/a'),
                    ('lastModificationDate', '0')]
        elm_relation = ET.SubElement(root, 'relation', {'id': unit_id})
        elm_metadata = ET.SubElement(elm_relation, 'metadata')
        for key, val in metadata:
            ET.SubElement(elm_metadata, key).text = val
        elm_charact = ET.SubElement(elm_relation, 'characterisation')
        ET.SubElement(elm_charact, 'type').text = utype

        elm_features = ET.SubElement(elm_charact, 'featureSet')
        comments = ET.SubElement(elm_features, 'feature', {'name': 'Comments'})
        comments.text = 'Please write in remarks...'
        argument_scope = ET.SubElement(elm_features, 'feature', {'name': 'Argument_scope'})
        argument_scope.text = 'Please choose...'

        positioning = ET.SubElement(elm_relation, 'positioning')
        edu1 = ET.SubElement(positioning, 'term', {'id': local_id1})
        edu2 = ET.SubElement(positioning, 'term', {'id': local_id2})

        return []

    else:
        err1 = "Implicit relation from subdoc %s to subdoc %s :" % (subdoc1, subdoc2)
        print(err1)
        err2 = "%s ------ %s -----> %s" % (global_id1, utype, global_id2)
        print(err2)
        return [err1, err2]


class Events:
    def __init__(self):
        self.Join = dict()
        self.Start = ""
        self.Building = dict()
        self.Roll = ""
        self.Dice = []
        self.Robber = []
        self.Trade = []
        self.Monopoly = ""


def append_schema(root, utype, edus):
    """
    Append a new schema level annotation to the given root element.
    Note that this generates a new identifier behind the scenes.

    Parameters
    ----------
    root :
        node of the XML tree to which we want to add a "schema" child
    utype : string
        type of the schema we want to create. Usually, a "Complex_discourse_unit"
    edus :
        list of the global ids of the EDUs that compose the CDU

    Returns
    -------
    cdu_id : string
        local id of the CDU created (used later to create a relation between this CDU and another element)
    """
    cdu_id, date = mk_id()

    metadata = [('author', 'stac'),
                ('creation-date', str(date)),
                ('lastModifier', 'n/a'),
                ('lastModificationDate', '0')]
    elm_schema = ET.SubElement(root, 'schema', {'id': cdu_id})
    elm_metadata = ET.SubElement(elm_schema, 'metadata')
    for key, val in metadata:
        ET.SubElement(elm_metadata, key).text = val
    elm_charact = ET.SubElement(elm_schema, 'characterisation')
    ET.SubElement(elm_charact, 'type').text = utype # utype = 'Complex_discourse_unit'
    elm_features = ET.SubElement(elm_charact, 'featureSet')

    positioning = ET.SubElement(elm_schema, 'positioning')
    for edu in edus:
        edusplit = edu.split('_')
        local_id = '_'.join([edusplit[-2], edusplit[-1]])
        ET.SubElement(positioning, 'embedded-unit', {'id': local_id})

    return cdu_id


def add_discourse_annotations(tree, text, e, subdoc):
    """
    Add discourse annotations for non-linguistical event
    
    Parameters
    ----------
    tree :
        XML tree extracted from the .aa file to modify
    text : string
        raw text extracted from the .ac file
    e : Events
        set of global ids for events currently happenning
    subdoc : string
        name of the subdoc currently annotated : GameName_XX (ex : pilot02_09)

    Returns
    -------
    root :
        modified XML tree with discourse annotations for non-linguistical events
    events : Events
        set of global ids for events currently happenning
    errors : string list
        list of error messages
    """

    root = tree
    events = e
    errors = []

    JoinRegEx = re.compile(r'(.+) joined the game\.')
    SitDownRegEx = re.compile(r'(.+) sat down at seat (\d)\.')

    TurnToBuildRegEx = re.compile(r"It's (.+)'s turn to build a (road|settlement)\.")
    BuiltRegEx = re.compile(r'(.+) built a (road|settlement)\.')

    TurnToRollRegEx = re.compile(r"It's (.+)'s turn to roll the dice\.")
    DiceRegEx = re.compile(r'(.+) rolled a (\d) and a (\d)\.')
    GetRegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood)\.')
    Get2RegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)\.')
    #It is impossible in "Settlers of Catan" to get more than 2 different types of resources with one roll dice.
    #That's why we actually don't need to bother with complex regular expression since there are in fact just two cases to consider. :)
    NoGetRegEx = re.compile(r'No player gets anything\.')

    SoldierRegEx = re.compile(r'(.+) played a Soldier card\.')
    Discard1RegEx = re.compile(r'(.+) needs to discard\.')
    Discard2RegEx = re.compile(r'(.+) discarded (\d+) resources\.')
    Robber1RegEx = re.compile(r'(.+) will move the robber\.')
    Robber2RegEx = re.compile(r'(.+) moved the robber\.')
    Robber3RegEx = re.compile(r'(.+) moved the robber, must choose a victim\.')
    StoleRegEx = re.compile(r'(.+) stole a resource from (.+)')

    #For discourse annotations, we can afford to use a single regex for every offer/trade events
    #since we don't need to parse every resource that is exchanged.
    OfferRegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood)(, (\d+) (clay|ore|sheep|wheat|wood))* for (\d+) (clay|ore|sheep|wheat|wood)(, (\d+) (clay|ore|sheep|wheat|wood))*( from the bank or a port)?\.')
    FromRegEx = re.compile(r'from (.+)')
    CantRegEx = re.compile(r"You can't make that trade\.")
    TradeRegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood)(, (\d+) (clay|ore|sheep|wheat|wood))* for (\d+) (clay|ore|sheep|wheat|wood)(, (\d+) (clay|ore|sheep|wheat|wood))* from (.+)\.')
    RejectRegEx = re.compile(r'(.+) rejected trade offer\.')

    CardRegEx = re.compile(r'(.+) played a Monopoly card\.')
    MonopolyRegEx = re.compile(r'(.+) monopolized (clay|ore|sheep|wheat|wood)\.')

    for unit in root:
        if unit.findtext('characterisation/type') == 'NonplayerSegment':

            start = int(unit.find('positioning/start/singlePosition').get('index'))
            end = int(unit.find('positioning/end/singlePosition').get('index'))
            event = text[start:end]

            global_id = '_'.join([subdoc, unit.get('id')])

            # Join / sit down events

            if JoinRegEx.search(event) != None: #<X> joined the game.
                mo = JoinRegEx.search(event)
                X = mo.group(1)
                events.Join[X] = global_id
                continue

            elif SitDownRegEx.search(event) != None: #<X> sat down at seat <N>.
                mo = SitDownRegEx.search(event)
                X = mo.group(1)
                if events.Join.has_key(X):
                    errors.extend(append_relation(root, 'Sequence', events.Join[X], global_id))
                    del events.Join[X]
                continue

            # Game started / Board layout set events

            elif event == "Game started.":
                events.Start = global_id
                continue

            elif event == "Board layout set.":
                if events.Start != '':
                    errors.extend(append_relation(root, 'Sequence', events.Start, global_id))
                    events.Start = ''
                continue

            # Building events

            elif TurnToBuildRegEx.search(event) != None: #It's <X>'s turn to build a <C>.
                mo = TurnToBuildRegEx.search(event)
                X = mo.group(1)
                C = mo.group(2)
                events.Building[(X,C)] = global_id
                if events.Building.has_key(('','')):
                    errors.extend(append_relation(root, 'Result', events.Building[('','')], global_id))
                    del events.Building[('','')]
                continue

            elif BuiltRegEx.search(event) != None: #<X> built a <C>.
                mo = BuiltRegEx.search(event)
                X = mo.group(1)
                C = mo.group(2)
                if events.Building.has_key((X,C)):
                    errors.extend(append_relation(root, 'Result', events.Building[(X,C)], global_id))
                    del events.Building[(X,C)]
                    events.Building[('','')] = global_id
                elif events.Building.has_key(('','')):
                    del events.Building[('','')]
                continue
                

            # Resource distribution events

            elif TurnToRollRegEx.search(event) != None: #It's <X>'s turn to roll the dice.
                events.Roll = global_id
                continue

            elif DiceRegEx.search(event) != None: #<X> rolled a <M1> and a <M2>.
                mo = DiceRegEx.search(event)
                M1 = int(mo.group(2))
                M2 = int(mo.group(3))
                if M1 + M2 != 7: # Resource distribution event
                    # Since we don't know when finishes a resource distribution,
                    # the trick is to compute a resource distribution when the next one starts.
                    # So here we first need to compute the preceding resource distribution.
                    if len(events.Dice) > 0:
                        if len(events.Dice) == 2: # Resource distribution : 1 player
                            errors.extend(append_relation(root, 'Result', events.Dice[0], events.Dice[1]))
                        else: # Resource Distribution : 2 or more players
                            cdu_dice = append_schema(root, 'Complex_discourse_unit', events.Dice[1:])
                            global_cdu_dice = '_'.join([subdoc, cdu_dice])
                            errors.extend(append_relation(root, 'Result', events.Dice[0], global_cdu_dice))
                            for i in range(1,len(events.Dice)-1):
                                errors.extend(append_relation(root, 'Continuation', events.Dice[i], events.Dice[i+1]))
                        events.Dice[:] = []
                    events.Dice.append(global_id)
                else: # M1 + M2 == 7 : Robber event
                    if events.Robber != []:
                        raise Exception("add_discourse_annotations : la liste RobberEvent n'a pas été vidée!")
                    events.Robber.append(global_id)
                if events.Roll != '':
                    errors.extend(append_relation(root, 'Result', events.Roll, global_id))
                    events.Roll = ''
                continue

            elif GetRegEx.search(event) != None: #<Y> gets <N> <R>.
                events.Dice.append(global_id)
                continue

            elif Get2RegEx.search(event) != None: #<Y> gets <N1> <R1>, <N2> <R2>.
                events.Dice.append(global_id)
                continue

            elif NoGetRegEx.search(event) != None: #No player gets anything.
                errors.extend(append_relation(root, 'Result', events.Dice[0], global_id))
                events.Dice[:] = []
                continue

            # Robber events

            elif SoldierRegEx.search(event) != None: #<X> played a Soldier card.
                if events.Robber != []:
                    raise Exception("add_discourse_annotations : la liste RobberEvent n'a pas été vidée!")
                events.Robber.append(global_id)
                continue

            elif Discard1RegEx.search(event) != None: #<Y> needs to discard.
                events.Robber.append(global_id)
                continue

            elif Discard2RegEx.search(event) != None: #<Y> discarded <N> resources.
                events.Robber.append(global_id)
                continue

            elif Robber1RegEx.search(event) != None: #<X> will move the robber.
                events.Robber.append(global_id)
                continue

            elif Robber2RegEx.search(event) != None: #<X> moved the robber.
                events.Robber.append(global_id)
                cdu_robber = append_schema(root, 'Complex_discourse_unit', events.Robber[1:])
                global_cdu_robber = '_'.join([subdoc, cdu_robber])
                errors.extend(append_relation(root, 'Result', events.Robber[0], global_cdu_robber))
                for i in range(1,len(events.Robber)-1):
                    errors.extend(append_relation(root, 'Sequence', events.Robber[i], events.Robber[i+1]))
                events.Robber[:] = []
                continue

            elif Robber3RegEx.search(event) != None: #<X> moved the robber, must choose a victim.
                events.Robber.append(global_id)
                continue

            elif StoleRegEx.search(event) != None: #<X> stole a resource from <Z>.
                events.Robber.append(global_id)
                cdu_robber = append_schema(root, 'Complex_discourse_unit', events.Robber[1:])
                global_cdu_robber = '_'.join([subdoc, cdu_robber])
                errors.extend(append_relation(root, 'Result', events.Robber[0], global_cdu_robber))
                for i in range(1,len(events.Robber)-1):
                    errors.extend(append_relation(root, 'Sequence', events.Robber[i], events.Robber[i+1]))
                events.Robber[:] = []
                continue

            # Trade events

            elif OfferRegEx.search(event) != None: #<X> made an offer to trade <M> <R1> for <N> <R2>.
                events.Trade[:] = []
                events.Trade.append(global_id)
                continue

            elif event == '...':
                events.Trade.append(global_id)
                continue

            elif FromRegEx.search(event) != None and TradeRegEx.search(event) == None: #from <X>
                events.Trade.append(global_id)
                errors.extend(append_relation(root, 'Elaboration', events.Trade[0], events.Trade[1]))
                errors.extend(append_relation(root, 'Continuation', events.Trade[1], global_id))
                cdu_offer = append_schema(root, 'Complex_discourse_unit', events.Trade)
                global_cdu_offer = '_'.join([subdoc, cdu_offer])
                events.Trade[0] = global_cdu_offer
                continue

            elif CantRegEx.search(event) != None: #You can't make that trade.
                errors.extend(append_relation(root, 'Question-answer_pair', events.Trade[0], global_id))
                events.Trade[:] = []
                continue

            elif TradeRegEx.search(event) != None: #<X> traded <M> <R1> for <N> <R2> from <Y>.
                errors.extend(append_relation(root, 'Question-answer_pair', events.Trade[0], global_id))
                events.Trade[:] = []
                continue

            elif RejectRegEx.search(event) != None: #<Y> rejected trade offer.
                errors.extend(append_relation(root, 'Question-answer_pair', events.Trade[0], global_id))
                events.Trade[:] = []
                continue

            # Monopoly events

            elif CardRegEx.search(event) != None: #<X> played a Monopoly card.
                if events.Monopoly != "":
                    raise Exception("add_discourse_annotations : la chaîne MonopolyEvent n'a pas été vidée!")
                events.Monopoly = global_id
                continue

            elif MonopolyRegEx.search(event) != None: #<X> monopolized <R>.
                errors.extend(append_relation(root, 'Sequence', events.Monopoly, global_id))
                events.Monopoly = ""
                continue


    """
    For resources distributions, we complete the XML tree and empty the list at the next dice roll.
    So for the last turn we may have forgotten to annotate some events.
    """
    if len(events.Dice) > 0:
        if len(events.Dice) == 2: # Resource distribution : 1 player
            errors.extend(append_relation(root, 'Result', events.Dice[0], events.Dice[1]))
        else: # Resource Distribution : 2 or more players
            cdu_dice = append_schema(root, 'Complex_discourse_unit', events.Dice[1:])
            global_cdu_dice = '_'.join([subdoc, cdu_dice])
            errors.extend(append_relation(root, 'Result', events.Dice[0], global_cdu_dice))
            for i in range(1,len(events.Dice)-1):
                errors.extend(append_relation(root, 'Continuation', events.Dice[i], events.Dice[i+1]))
        events.Dice[:] = []

    return root, events, errors




# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------



def main():

    #ligne de commande : python nonling_annotations.py ../../data/pilot_nonling/test/pilot14/ SILVER

    init_mk_id()

    parser = argparse.ArgumentParser()

    parser.add_argument('Folder', help = 'folder where the files to annotate are')
    parser.add_argument('Metal', help = 'version of the game you want to annotate : BRONZE, SILVER, or GOLD (or other)')

    args = parser.parse_args()
    Folder = args.Folder
    Metal = args.Metal
    Name = Folder.split('/')[-2]
    
    UnitsFolder = Folder + 'units/' + Metal + '/'
    DiscourseFolder = Folder + 'discourse/' + Metal + '/'

    N = len(os.listdir(UnitsFolder)) / 2
    
    Implicit_Relations = []
    events = Events()

    for i in range(1, N+1):
        e = events

        subdoc = Name + '_%02d' % i

        textname = Folder + 'unannotated/' + subdoc + '.ac'
        unitsname = UnitsFolder + subdoc + '.aa'
        discoursename = DiscourseFolder + subdoc + '.aa'
        textfile = open(textname, 'r')
        unitsfile = open(unitsname, 'r')
        discoursefile = open(discoursename, 'r')

        text = textfile.read()
        stringtree_units = unitsfile.read()
        units_tree = ET.fromstring(stringtree_units)
        stringtree_discourse = discoursefile.read()
        discourse_tree = ET.fromstring(stringtree_discourse)

        units_root = add_units_annotations(units_tree, text)
        discourse_root, events, errors = add_discourse_annotations(discourse_tree, text, e, subdoc)

        Implicit_Relations.extend(errors)

        with codecs.open(unitsname, 'w', 'ascii') as out:
            out.write(prettify(units_root))
        with codecs.open(discoursename, 'w', 'ascii') as out:
            out.write(prettify(discourse_root))

        textfile.close()
        unitsfile.close()
        discoursefile.close()

    if Implicit_Relations != []:
        error_report = '\n'.join(Implicit_Relations)
        filename = Folder + 'Implicit_Relations.txt'
        with codecs.open(filename, 'w', 'ascii') as out:
            out.write(error_report)


if __name__ == '__main__':
    main()
