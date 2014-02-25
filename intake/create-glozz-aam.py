#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Eric Kow
# License: BSD3

"""
Create an STAC .aam file from a .soclog.csv file.

The empty set is represented by '?' and the whole set is
represented by 'All'

Usage:
    create-glozz-aam.py input.soclog.csv output.aam
"""

import csv
from   itertools import chain
import itertools
import sys
import xml.etree.ElementTree as ET

import stac.csv

# ---------------------------------------------------------------------
# template
# ---------------------------------------------------------------------

anno_surface_acts = [ 'Assertion', 'Question', 'Request' ]
anno_resource_status =\
        [ 'Possessed' , 'Not possessed'
        , 'Givable'   , 'Not givable'
        , 'Receivable', 'Not receivable'
        , '?'
        ]
anno_bargain_status =\
        [ 'Successful'
        , 'Unsuccessful'
        ]
anno_kind = [ '?'
            , 'clay',  'Anything but clay'
            , 'ore' ,  'Anything but ore'
            , 'sheep', 'Anything but sheep'
            , 'wheat', 'Anything but wheat'
            , 'wood' , 'Anything but wood'
            , 'Nothing'
            , 'Anaphoric'
            ]

anno_quantity = ['?'] + map(str,range(0,10))

anno_argument_scope = [ 'Specified', 'Unspecified' ]

anno_correctness = [ 'True', 'False', '?' ]


turn_attrs  = [ 'Timestamp', 'Identifier', 'Emitter', 'Developments', 'Resources' ]
speech_acts = [ 'Accept', 'Refusal', 'Strategic_comment', 'Other', 'Offer', 'Counteroffer' ]
discourse_rel_types =\
        [ 'Question-answer_pair'
        , 'Result'
        , 'Comment'
        , 'Continuation'
        , 'Conditional'
        , 'Explanation'
        , 'Elaboration'
        , 'Q-Elab'
        , 'Clarification_question'
        , 'Contrast'
        , 'Correction'
        , 'Narration'
        , 'Parallel'
        , 'Alternation'
        , 'Acknowledgement'
        , 'Background'
        ]



# ---------------------------------------------------------------------
# template
# ---------------------------------------------------------------------

def mk_feature(name, default='', type='free'):
    feature = ET.Element('feature', name=name)
    value   = ET.Element('value',   type=type, default=default)
    feature.append(value)
    return feature

def mk_value(val):
    elm      = ET.Element('value')
    elm.text = val
    return elm

def mk_comments():
    return mk_feature('Comments',default='Please write in remarks...')

def mk_radio(name, choices):
    elm = ET.Element('feature', name=name)
    pv  = ET.Element('possibleValues', default='Please choose...')
    pv.extend(map(mk_value, choices))
    elm.append(pv)
    return elm

def mk_featureSet(features):
    elm = ET.Element('featureSet')
    elm.extend(features)
    return elm

def mk_type(name, groups, features):
    elm = ET.Element('type', name=name, groups=groups)
    if features is not None:
        elm.append(mk_featureSet(features))
    return elm

def mk_speech_act(name, player_combos):
    feats = [ mk_radio('Addressee',   player_combos)
            , mk_radio('Surface_act', anno_surface_acts)
            ]
    return mk_type(name, 'Complex_discourse_unit', feats)

def mk_discourse_relation(name):
    feats = [ mk_radio('Argument_scope', anno_argument_scope)
            , mk_comments()
            ]
    elm = mk_type(name, 'Discourse', feats)
    elm.attrib['oriented'] = 'true'
    return elm

def create_model(players):
    combos_ = emitter_combinations(players)
    combos  = [ ', '.join(sorted(list(c))) for c in combos_ ]

    root   = ET.Element('annotationModel')
    units  = ET.Element('units')
    relations = ET.Element('relations')
    schemas   = ET.Element('schemas')

    # units
    ty_turn_feats = map(mk_feature, turn_attrs) + [ mk_comments() ]
    ty_turn = mk_type('Turn', 'Bargaining_block', ty_turn_feats)

    ty_segment  = mk_type('Segment', 'Complex_discourse_unit', None)
    ty_resource = mk_type('Resource', 'Several_resources',\
            [ mk_radio('Correctness', anno_correctness)
            , mk_radio('Status',      anno_resource_status)
            , mk_radio('Kind',        anno_kind)
            , mk_radio('Quantity',    anno_quantity)
            ])
    ty_prefs    = mk_type('Preference', 'Preferences', [])

    units.extend([ty_turn, ty_segment])
    units.extend( [mk_speech_act(x, combos) for x in speech_acts] )
    units.extend([ty_resource, ty_prefs])

    # resources
    ty_anaphora = mk_type('Anaphora', 'Several_resources',
            [ mk_radio('Argument_scope', anno_argument_scope)
            , mk_comments()
            ])
    ty_anaphora.attrib['oriented']='true'

    relations.extend([ty_anaphora])
    relations.extend( [ mk_discourse_relation(x) for x in discourse_rel_types] )

    # schemas
    ty_bblock = mk_type('Bargaining_block', 'Blocks',\
            [ mk_radio('Status', anno_bargain_status)
            , mk_radio('Giver',  combos)
            , mk_radio('Taker',  combos)
            ])
    ty_cdus = mk_type('Complex_discourse_unit', 'CDUs', [])
    ty_schema_resources = mk_type('Several_resources','Resources',\
                                  [ mk_radio('Operator', ['AND','OR']) ])

    schemas.extend([ty_bblock, ty_cdus, ty_schema_resources])

    root.extend([units, relations, schemas])
    return root

# in-place prettyprint formatter
# taken from http://effbot.org/zone/element-lib.htm
def indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# ---------------------------------------------------------------------
# reading soclog (csv)
# ---------------------------------------------------------------------

def read_players(filename):
    with open(filename, 'rb') as infile:
        reader = stac.csv.mk_csv_reader(infile)
        players = frozenset([r['Emitter'] for r in reader])
        return (players - frozenset(['Server']))

def emitter_combinations(s):
    """
    emitter_combinations(['a','b','c']) ~~>
        ('?') ('1') ('2') ('3') ('1','2') ('1','3') ('2','3') ('All')

    Note, `~~>` because input is expected to be a frozenset, and
    output is a list of frozensets, ordered by size
    """
    sizes       = range(1,len(s))
    almost_pset = chain.from_iterable(itertools.combinations(s, r) for r in sizes)
    results     = [ ['All'], ['?'] ]
    results.extend(almost_pset)
    return map(frozenset, results)

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

if len(sys.argv) == 3:
    filename_in  = sys.argv[1]
    filename_out = sys.argv[2]
else:
    print >> sys.stderr, "Usage: create-glozz-aam.py input.soclog.csv output.aam"
    sys.exit(1)

players  = read_players(filename_in)
model     = create_model(players)
indent(model) # sigh, imperative
ET.ElementTree(model).write(filename_out, encoding='utf-8', xml_declaration=True)
