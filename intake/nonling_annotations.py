#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automatically adds annotations for non-linguistic events in a game of "Settlers of Catan"
"""

#TODO The script now works on a complete game, but maybe we can make it in a more dynamic and proper way


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

    OfferRegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood)\.')
    TradeRegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    RejectRegEx = re.compile(r'(.+) rejected trade offer\.')

    GetRegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood)\.')
    Get2RegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)\.')
    #It is impossible in "Settlers of Catan" to get more than 2 different types of resources with one roll dice.
    #That's why we actually don't need to bother with complex regular expression since there are in fact just two cases to consider. :)

    MonopolyRegEx = re.compile(r'(.+) monopolized (clay|ore|sheep|wheat|wood)\.')

    for unit in root:
        if unit.findtext('characterisation/type') == 'NonplayerSegment':
            start = int(unit.find('positioning/start/singlePosition').get('index'))
            end = int(unit.find('positioning/end/singlePosition').get('index'))
            event = text[start:end]
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
                append_unit(root, 'Resource',
                            [('Status', 'Givable'), ('Quantity', M), ('Correctness', 'True'), ('Kind', R1)],
                            left1, left1 + len(M) + 1 + len(R1))
                right2 = end - 1
                append_unit(root, 'Resource',
                            [('Status', 'Receivable'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R2)],
                            right2 - len(R2) - 1 - len(N), right2)
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
                append_unit(root, 'Resource',
                            [('Status', '?'), ('Quantity', M), ('Correctness', 'True'), ('Kind', R1)],
                            left1, left1 + len(M) + 1 + len(R1))
                right2 = end - len(Y) - 7
                append_unit(root, 'Resource',
                            [('Status', 'Possessed'), ('Quantity', N), ('Correctness', 'True'), ('Kind', R2)],
                            right2 - len(R2) - 1 - len(N), right2)
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
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
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
                f_elm2 = ET.SubElement(feats, 'feature', {'name': 'Addresse'})
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
    edu1 = ET.SubElement(positioning, 'term', {'id': id1})
    edu2 = ET.SubElement(positioning, 'term', {'id': id2})


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
        id of the CDU created (used later to create a relation between this CDU and another element)
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
        ET.SubElement(positioning, 'embedded-unit', {'id': edu})

    return cdu_id


def add_discourse_annotations(tree, text, JoinEvents, StartEvent, DiceEvent, RobberEvent, TradeEvent, MonopolyEvent):
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

    JoinRegEx = re.compile(r'(.+) joined the game\.')
    SitDownRegEx = re.compile(r'(.+) sat down at seat (\d)\.')

    DiceRegEx = re.compile(r'(.+) rolled a (\d) and a (\d)\.')
    GetRegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood)\.')
    Get2RegEx = re.compile(r'(.+) gets (\d+) (clay|ore|sheep|wheat|wood), (\d+) (clay|ore|sheep|wheat|wood)\.')
    #It is impossible in "Settlers of Catan" to get more than 2 different types of resources with one roll dice.
    #That's why we actually don't need to bother with complex regular expression since there are in fact just two cases to consider. :)
    NoGetRegEx = re.compile(r'No player gets anything\.')

    SoldierRegEx = re.compile(r'(.+) played a soldier card\.')
    Discard1RegEx = re.compile(r'(.+) needs to discard\.')
    Discard2RegEx = re.compile(r'(.+) discarded (\d+) resources\.')
    Robber1RegEx = re.compile(r'(.+) will move the robber\.')
    Robber2RegEx = re.compile(r'(.+) moved the robber\.')
    Robber3RegEx = re.compile(r'(.+) moved the robber, must choose a victim\.')
    StoleRegEx = re.compile(r'(.+) stole a resource from (.+)')
    #So it appears that there is no point at the end of "stole" events
    #and I don't know where that comes from but it took me a while to realise this.

    OfferRegEx = re.compile(r'(.+) made an offer to trade (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood)\.')
    TradeRegEx = re.compile(r'(.+) traded (\d+) (clay|ore|sheep|wheat|wood) for (\d+) (clay|ore|sheep|wheat|wood) from (.+)\.')
    RejectRegEx = re.compile(r'(.+) rejected trade offer\.')
    CardRegEx = re.compile(r'(.+) played a monopoly card\.')
    MonopolyRegEx = re.compile(r'(.+) monopolized (clay|ore|sheep|wheat|wood)\.')

    """
    For events composed of several segments,
    these lists will keep in memory the ids
    of the segments of the event currently happening.

    The lists are then emptied when the event is finished,
    in order to start the next event.

    For join / sit down events, since they happen at the same time,
    we need a more complex structure than a list, like a dictionnary,
    to identify which "sit down" event is linked to which "join" event.

    For trade and monopoly events, we only need to keep the offer / card drawn in memory,
    so a single string is enough.
    """

    for unit in root:
        if unit.findtext('characterisation/type') == 'NonplayerSegment':
            start = int(unit.find('positioning/start/singlePosition').get('index'))
            end = int(unit.find('positioning/end/singlePosition').get('index'))
            event = text[start:end]

            # Join / sit down events

            if JoinRegEx.search(event) != None: #<X> joined the game.
                mo = JoinRegEx.search(event)
                X = mo.group(1)
                JoinEvents[X] = unit.get('id')
                continue

            elif SitDownRegEx.search(event) != None: #<X> sat down at seat <N>.
                mo = SitDownRegEx.search(event)
                X = mo.group(1)
                append_relation(root, 'Sequence', JoinEvents[X], unit.get('id'))
                del JoinEvents[X]
                continue

            # Game started / Board layout set events

            elif event == "Game started.":
                StartEvent = unit.get('id')
                continue

            elif event == "Board layout set.":
                append_relation(root, 'Sequence', StartEvent, unit.get('id'))
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

            elif Get2RegEx.search(event) != None: #<Y> gets <N1> <R1>, <N2> <R2>.
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
                    append_relation(root, 'Sequence', RobberEvent[i], RobberEvent[i+1])
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
                    append_relation(root, 'Sequence', RobberEvent[i], RobberEvent[i+1])
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

    return root, JoinEvents, StartEvent, DiceEvent, RobberEvent, TradeEvent, MonopolyEvent




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

    JoinEvents = dict()
    StartEvent = ""
    DiceEvent = []
    RobberEvent = []
    TradeEvent = ""
    MonopolyEvent = ""

    N = len(os.listdir(UnitsFolder)) / 2

    for i in range(1, N+1):
        a = JoinEvents
        b = StartEvent
        c = DiceEvent
        d = RobberEvent
        e = TradeEvent
        f = MonopolyEvent

        textname = UnitsFolder + Name + '_%02d.ac' % i
        unitsname = UnitsFolder + Name + '_%02d.aa' % i
        discoursename = DiscourseFolder + Name + '_%02d.aa' % i
        textfile = open (textname, 'r')
        unitsfile = open(unitsname, 'r')
        discoursefile = open (discoursename, 'r')

        text = textfile.read()
        stringtree_units = unitsfile.read()
        units_tree = ET.fromstring(stringtree_units)
        stringtree_discourse = discoursefile.read()
        discourse_tree = ET.fromstring(stringtree_discourse)

        units_root = add_units_annotations(units_tree, text)
        discourse_root, JoinEvents, StartEvent, DiceEvent, RobberEvent, TradeEvent, MonopolyEvent = add_discourse_annotations(
                    discourse_tree, text, a, b, c, d, e, f)
        
        """
        basename_units = unitsname[0:len(unitsname)-3]
        basename_discourse = discoursename[0:len(discoursename)-3]
        with codecs.open(basename_units + '-modified.aa', 'w', 'ascii') as out:
            out.write(prettify(units_root))
        with codecs.open(basename_discourse + '-modified.aa', 'w', 'ascii') as out:
            out.write(prettify(discourse_root))
        """

        with codecs.open(unitsname, 'w', 'ascii') as out:
            out.write(prettify(units_root))
        with codecs.open(discoursename, 'w', 'ascii') as out:
            out.write(prettify(discourse_root))

        textfile.close()
        unitsfile.close()
        discoursefile.close()




    """
    #ligne de commande : python nonling_annotations.py test_units.aa test_discourse.aa test.ac

    init_mk_id()

    parser = argparse.ArgumentParser()

    parser.add_argument('aaUfile', help = 'file with units annotations')
    parser.add_argument('aaDfile', help = 'file with discourse annotations')
    parser.add_argument('acfile', help = 'file with rawtext')

    aaUfile = args.aaUfile
    aaDfile = args.aaDfile
    acfile = args.acfile


    aauf = open(aaUfile, 'r')
    aadf = open(aaDfile, 'r')
    acf = open(acfile, 'r')

    stringtree_units = aauf.read()
    units_tree = ET.fromstring(stringtree_units)
    stringtree_discourse = aadf.read()
    discourse_tree = ET.fromstring(stringtree_discourse)
    text = acf.read()

    units_root = add_units_annotations(units_tree, text)
    discourse_root = add_discourse_annotations(discourse_tree, text)

    basename_units = aaUfile.split(".")[0]
    basename_discourse = aaDfile.split(".")[0]

    with codecs.open(basename_units+'-modified.aa', 'w', 'ascii') as out:
        out.write(prettify(units_root))
    with codecs.open(basename_discourse+'-modified.aa', 'w', 'ascii') as out:
        out.write(prettify(discourse_root))

    aauf.close()
    aadf.close()
    acf.close()
    """


if __name__ == '__main__':
    main()
