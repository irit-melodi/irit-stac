#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Takes a duet of aa/ac files and automatically adds annotations for non-linguistic events, such as trades or dice rollings.
"""

#FIXME problem with the function mk_id() from irit-stac/intake/csvtoglozz.py, called in the function append_unit()

#TODO for now only "units" annotations are added, "discourse" annotations also need to be implemented

#TODO for now the script only takes a duet of aa/ac files for testing purpose, but we want to do this on a complete game



from __future__ import print_function

import xml.etree.ElementTree as ET
import re
import argparse
import codecs
import sys

from csvtoglozz import append_unit, mk_id
from educe.stac.util.prettifyxml import prettify



# ---------------------------------------------------------------------
# "Units" annotations
# ---------------------------------------------------------------------


def add_units(tree, text):
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
    #root = tree.getroot()
    root = tree

    OfferRegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood).')
    TradeRegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+).')
    RejectRegEx = re.compile(r'(.+) rejected trade offer.')
    GetRegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood).')
    MonopolyRegEx = re.compile(r'(.+) monopolized (clay|ore|sheep|wheat|wood).')

    for unit in root:
        if unit.findtext('characterisation/type') == 'NonplayerSegment':
            start = int(unit.find('positioning/start/singlePosition').get('index'))
            end = int(unit.find('positioning/end/singlePosition').get('index'))
            event = text[start+1:end+1] #les fichiers .ac commencent par un espace, donc tous les index sont décalés de 1 pour la lecture

            if OfferRegEx.search(event) != None: #<X> made an offer to trade <M> <R1> for <N> <R2>.
               mo = OfferRegEx.search(event)
               X = mo.group(1)
               M = mo.group(2)
               R1 = mo.group(3)
               N = mo.group(4)
               R2 = mo.group(5)

               unit.find('characterisation/type').text = 'Offer'
               feats = unit.find('characterisation/featureSet')
               f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
               f_elm1.text = 'Question'
               f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
               f_elm2.text = '?'

               left1 = start + len(X) + 24
               append_unit(root, 'Resource', left1, left1 + len(M) + 1 + len(R1),
                           [('Status', 'Givable'), ('Quantity', M), ('Correctness', 'True'), ('Kind', R1)])
               right2 = end - 1
               append_unit(root, 'Resource', right2 - len(R2) - 1 - len(N), right2,
                           [('Status', 'Receivable'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R2)])
               continue


            elif TradeRegEx.search(event) != None: #<X> traded <M> <R1> for <N> <R2> from <Y>.
                mo = TradeRegEx.search(event)
                X = mo.group(1)
                M = mo.group(2)
                R1 = mo.group(3)
                N = mo.group(4)
                R2 = mo.group(5)
                Y = mo.group(6)

                unit.find('characterisation/type').text = 'Accept'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
                f_elm2.text = Y


                """
                Les units de type "Resource" sont tout en bas du fichier XML,
                donc je suppose qu'on peut simplement faire un append et les
                ajouter à la fin. Mais du coup toutes les Resource ne sont pas
                dans l'ordre (d'abord les ressources utilisateurs, ensuite les
                ressources serveur). Je ne sais pas si ça pose problème.
                """
                left1 = start + len(X) + 24
                append_unit(root, 'Resource', left1, left1 + len(M) + 1 + len(R1),
                            [('Status', '?'), ('Quantity', M), ('Correctness', 'True'), ('Kind', R1)])
                right2 = end - len(Y) - 7
                append_unit(root, 'Resource', right2 - len(R2) - 1 - len(N), right2,
                            [('Status', 'Possessed'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R2)])
                continue


            elif RejectRegEx.search(event) != None: #<Y> rejected trade offer.
                mo = RejectRegEx.search(event)
                Y = mo.group(1)

                unit.find('characterisation/type').text = 'Reject'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
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
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
                f_elm2.text = 'All'

                left = start + len(Y) + 6
                right = end - 1
                append_unit(root, 'Resource', left, right,
                            [('Status', 'Possessed'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R)])
                continue


            elif MonopolyRegEx.search(event) != None: #<X> monopolized <R>.
                mo = MonopolyRegEx.search(event)
                X = mo.group(1)
                R = mo.group(2)

                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
                f_elm2.text = 'All'

                right = end - 1
                left = right - len(R)
                append_unit(root, 'Resource', left, right,
                            [('Status', 'Possessed'), ('Quantity', '?'), ('Correctness', 'True'), ('Kind', R)])
                continue

            else:
                unit.find('characterisation/type').text = 'Other'
                feats = unit.find('characterisation/featureSet')
                f_elm1 = ET.SubElement(feats, 'feature', {'name': 'Surface_act'})
                f_elm1.text = 'Assertion'
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
                f_elm2.text = 'All'
                continue

    return root



# ---------------------------------------------------------------------
# "Discourse" annotations
# ---------------------------------------------------------------------



def append_relation(root, utype, id1, id2):
    """
    Append a new relation level annotation to the given root element.
    Note that this generates a new identifier behind the scenes.

    Parameters
    ----------
    root :
        node of the XML tree to which we want to add a "relation" child
    utype : string
        type of the relation we want to create (sequence, continuation, QAP...)
    id1 : string
        id of the first element (EDU or CDU) of the relation
    id2 : string
        id of the second element (EDU or CDU) of the relation
    """
    unit_id, date = mk_id()

    metadata = [('author', 'stac'),
                ('creation-date', str(date)),
                ('lastModifier', 'n/a'),
                ('lastModificationDate', '0')]
    elm_relation = SubElement(root, 'relation', {'id': unit_id})
    elm_metadata = SubElement(elm_relation, 'metadata')
    for key, val in metadata:
        SubElement(elm_metadata, key).text = val
    elm_charact = SubElement(elm_relation, 'characterisation')
    SubElement(elm_charact, 'type').text = utype

    elm_features = SubElement(elm_charact, 'featureSet')
    comments = SubElement(elm_features, 'feature', {'name': 'Comments'})
    comments.text = 'Please write in remarks...'
    argument_scope = SubElement(elm_features, 'feature', {'name': 'Argument_scope'})
    argument_scope.text = 'Please choose...'

    positioning = SubElement(elm_relation, 'positioning')
    edu1 = SubElement(positioning, 'term', {'name': 'id'})
    edu1.text = id2
    edu2 = SubElement(positioning, 'term', {'name': 'id'})
    edu2.text = id2


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
        list of the ids of the EDUs that compose the CDU

    Returns
    -------
    cdu_id : string
        id of the CDU (used to create a relation between this CDU and another element)
    """
    cdu_id, date = mk_id()

    metadata = [('author', 'stac'),
                ('creation-date', str(date)),
                ('lastModifier', 'n/a'),
                ('lastModificationDate', '0')]
    elm_relation = SubElement(root, 'schema', {'id': cdu_id})
    elm_metadata = SubElement(elm_relation, 'metadata')
    for key, val in metadata:
        SubElement(elm_metadata, key).text = val
    elm_charact = SubElement(elm_relation, 'characterisation')
    SubElement(elm_charact, 'type').text = utype # utype = 'Complex_discourse_unit'
    elm_features = SubElement(elm_charact, 'featureSet')

    positioning = SubElement(elm_relation, 'positioning')
    for edu in edus:
        SubElement(positioning, 'embedded-unit', {'id': edu})

    return cdu_id


def add_discourse_annotations(tree, text):
    """
    Add discourse annotations for non-linguistical event
    
    Parameters
    ----------
    tree :
        XML tree extracted from the .aa file to modify
    text : string
        raw text extracted from the .ac file

    Returns
    -------
    root :
        modified XML tree with discourse annotations for non-linguistical events
    """
    
    root = tree

    JoinRegEx = re.compile(r'(.+) joined the game.')
    SitDownRegEx = re.compile(r'(.+) sat down at seat (\d).')
    DiceRegEx = re.compile(r'(.+) rolled a (\d) and a (\d).')
    GetRegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood).')
    NoGetRegEx = re.compile(r'No player gets anything.')

    SoldierRegEx = re.compile(r'(.+) played a soldier card.')
    Discard1RegEx = re.compile(r'(.+) needs to discard.')
    Discard2RegEx = re.compile(r'(.+) discarded (\d+) resources.')
    Robber1RegEx = re.compile(r'(.+) will move the robber.')
    Robber2RegEx = re.compile(r'(.+) moved the robber.')
    Robber3RegEx = re.compile(r'(.+) moved the robber, must choose a victim.')
    StoleRegEx = re.compile(r'(.+) stole a resource from (.+).')

    OfferRegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood).')
    TradeRegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+).')
    RejectRegEx = re.compile(r'(.+) rejected trade offer.')
    CardRegEX = re.compile(r'(.+) played a monopoly card.')
    MonopolyRegEx = re.compile(r'(.+) monopolized (clay|ore|sheep|wheat|wood).')

    """
    For events composed of several segments,
    these lists will keep in memory the ids
    of the segments of the event currently happening.

    The lists are then emptied when the event is finished,
    in order to start the next event.

    For join / sit down events, since they happen at the same time,
    we need a more complex structure than a list, like a dictionnary,
    to identify which "sit down" event is linked to which "join" event.

    For trade / monopoly events, we only need to keep the offer / card drawn in memory,
    so a single string is enough.
    """
    JoinEvents = dict()
    DiceEvent = []
    RobberEvent = []
    TradeEvent = ""
    MonopolyEvent = ""

    for unit in root:
        if unit.findtext('characterisation/type') == 'NonplayerSegment':
            start = int(unit.find('positioning/start/singlePosition').get('index'))
            end = int(unit.find('positioning/end/singlePosition').get('index'))
            event = text[start+1:end+1] #les fichiers .ac commencent par un espace, donc tous les index sont décalés de 1 pour la lecture

            # Join / sit down events

            if JoinRegEx.search(event) != None: #<X> joined the game.
                mo = JoinRegEx.search(event)
                X = mo.group(1)
                JoinEvents[X] = unit.get('id')
                continue

            elif SitDownRegEx.search(event) != None: #<X> sat down at seat <N>.
                mo = JoinRegEx.search(event)
                X = mo.group(1)
                append_relation(root, 'Sequence', JoinEvents[X], unit.get('id'))
                del JoinEvents[X]
                continue

            # Resource distribution events

            elif DiceRegEx.search(event) != None: #<X> rolled a <M1> and a <M2>.
                mo = DiceRegEx.search(event)
                M1 = int(mo.group(2))
                M2 = int(mo.group(3))
                if M1 + M2 != 7: # Resource distribution event
                    if len(DiceEvent) > 0:
                        if len(DiceEvent) == 2: # Resource distribution : 1 player
                            append_relation(root, 'Result', DiceEvent[0], DiceEvent[1])
                        else: # Resource Distribution : 2 or more players
                            cdu = append_schema(root, 'Complex_discourse_unit', DiceEvent[1:])
                            append_relation(root, 'Result', DiceEvent[0], cdu)
                            for i in range(1,len(DiceEvent)-2):
                                append_relation(root, 'Continuation', DiceEvent[i], DiceEvent[i+1])
                        DiceEvent[:] = []
                    DiceEvent.append(unit.get('id'))
                else: # Robber event
                    if RobberEvent != []:
                        raise Exception("add_discourse_annotations : la liste RobberEvent n'a pas été vidée!")
                    RobberEvent.append(unit.get('id'))
                continue

            elif GetRegEx.search(event) != None: #<Y> gets <N> <R>.
                DiceEvent.append(unit.get('id'))
                continue

            elif NoGetRegEx.search(event) != None: #No player gets anything.
                append_relation(root, 'Result', DiceEvent[0], unit.get('id'))
                DiceEvent[:] = []
                continue

            # Robber events

            elif SoldierRegEx.search(event) != None: #<X> played a soldier card.
                if RobberEvent != []:
                    raise Exception("add_discourse_annotations : la liste RobberEvent n'a pas été vidée!")
                RobberEvent.append(unit.get('id'))
                continue

            elif Discard1RegEx.search(event) != None: #<Y> needs to discard.
                RobberEvent.append(unit.get('id'))
                continue

            elif Discard2RegEx.search(event) != None: #<Y> discarded <N> resources.
                RobberEvent.append(unit.get('id'))
                continue

            elif Robber1RegEx.search(event) != None: #<X> will move the robber.
                RobberEvent.append(unit.get('id'))
                continue

            elif Robber2RegEx.search(event) != None: #<X> moved the robber.
                RobberEvent.append(unit.get('id'))
                cdu = append_schema(root, 'Complex_discourse_unit', RobberEvent[1:])
                append_relation(root, 'Result', RobberEvent[0], cdu)
                for i in range(1,len(RobberEvent)-2):
                    append_relation(root, 'Sequence', DiceEvent[i], DiceEvent[i+1])
                RobberEvent[:] = []
                continue

            elif Robber3RegEx.search(event) != None: #<X> moved the robber, must choose a victim.
                RobberEvent.append(unit.get('id'))
                continue

            elif StoleRegEx.search(event) != None: #<X> stole a resource from <Z>.
                RobberEvent.append(unit.get('id'))
                cdu = append_schema(root, 'Complex_discourse_unit', RobberEvent[1:])
                append_relation(root, 'Result', RobberEvent[0], cdu)
                for i in range(1,len(RobberEvent)-2):
                    append_relation(root, 'Sequence', DiceEvent[i], DiceEvent[i+1])
                RobberEvent[:] = []
                continue

            # Trade events
            # HYPOTHESIS : only one offer can be made at a time (not sure if true, needs in/confirmation)

            elif OfferRegEx.search(event) != None: #<X> made an offer to trade <M> <R1> for <N> <R2>.
                if TradeEvent != "":
                    TradeEvent = ""
                TradeEvent = unit.get('id')
                continue

            elif TradeRegEx.search(event) != None: #<X> traded <M> <R1> for <N> <R2> from <Y>.
                append_relation(root, 'Question-answer_pair', TradeEvent, unit.get('id'))
                continue

            elif RejectRegEx.search(event) != None: #<Y> rejected trade offer.
                append_relation(root, 'Question-answer_pair', TradeEvent, unit.get('id'))
                continue

            # Monopoly events

            elif CardRegEx.search(event) != None: #<X> played a monopoly card.
                if MonopolyEvent != "":
                    raise Exception("add_discourse_annotations : la chaîne MonopolyEvent n'a pas été vidée!")
                MonopolyEvent = unit.get('id')
                continue

            elif MonopolyRegEx.search(event) != None: #<X> monopolized <R>.
                append_relation(root, 'Sequence', MonopolyEvent, unit.get('id'))
                MonopolyEvent = ""
                continue


    """
    For resources distributions, we complete the XML tree and empty the list at the next dice roll.
    So for the last turn we may have forgotten to annotate some events.
    """
    if len(DiceEvent) > 0:
        if len(DiceEvent) == 2: # Resource distribution : 1 player
            append_relation(root, 'Result', DiceEvent[0], DiceEvent[1])
        else: # Resource Distribution : 2 or more players
            cdu = append_schema(root, 'Complex_discourse_unit', DiceEvent[1:])
            append_relation(root, 'Result', DiceEvent[0], cdu)
            for i in range(1,len(DiceEvent)-2):
                append_relation(root, 'Continuation', DiceEvent[i], DiceEvent[i+1])
        DiceEvent[:] = []

    return root




# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------



def main():

    #ligne de commande : python nonling_annotations.py test.aa test.ac

    parser = argparse.ArgumentParser()
    
    parser.add_argument('aafile', help = 'file with annotations')
    parser.add_argument('acfile', help = 'file with rawtext')

    args = parser.parse_args()
    aafile = args.aafile
    acfile = args.acfile

    aaf = open(aafile, 'r')
    acf = open(acfile, 'r')

    stringtree = aaf.read()
    tree = ET.fromstring(stringtree)
    text = acf.read()

    root = add_units(tree, text)

    with codecs.open(basename+'-modified.aa', 'w', 'ascii') as out:
        out.write(prettify(root))

    aaf.close()
    acf.close()


if __name__ == '__main__':
    main()
