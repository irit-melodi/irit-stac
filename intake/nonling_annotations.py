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

from csvtoglozz import append_unit
from educe.stac.util.prettifyxml import prettify


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
        modified XML tree with units non-linguistical event annotations
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
