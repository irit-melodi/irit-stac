#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The program takes (optionally segmented) CSV files as inputs, processes the
segment information (the "&"s) if applicable, and outputs an (.ac, .aa) pair of
Glozz files.

The output files contain:
    - the .ac file will contain the text attributes of the dialogue turns
      (without the '&', one turn on a line).
    - the .aa file will contain:
        - a pre-annotation in terms of:
            - dialogue information:
                - cut at dice rollings;
                - trades,
                - dice rollings,
                - resource gettings.
            - turn information:
                - borders (implicit)
                - Identifier
                - Timestamp
                - Emitter
                - Resources
                - Developments
            - segment (UDE) information:
                - borders (implicit)
                - Shallow dialogue act: Question | Request | Assertion
                - Task dialogue act: Offer | Counteroffer | Accept | Refusal |
                                     Strategic_comment | Other

Usage:
>>> ./csvtoglozz.py -f <CSV file name>

@note: The output file names are formed by appending the .ac and .aa extensions
to the input CSV file basename.
Example: for an input filename like document1.soclog.seg.csv, the pair
(document1.ac, document1.aa) is generated.
@note: The program supports filenames with empty spaces in them.
@note: Glozz is 0-indexed (but our .ac files systematically start with a space)
'''

from __future__ import print_function
from xml.etree.ElementTree import Element, SubElement, Comment
from collections import namedtuple
from itertools import islice, takewhile
import argparse
import codecs
import csv
import datetime
import itertools
import re
import sys
import time

from educe.stac.util.prettifyxml import prettify
from educe.stac.util.stac_csv_format import Turn


class Span(namedtuple('Span', 'left right')):
    """
    Simple l/r pair
    """


class Events(namedtuple('Events',
                        ['rolls',
                         'resources',
                         'trades'])):
    """
    High-level representation of a sequence of events
    reported by the server
    """
    pass


# ---------------------------------------------------------------------
# timestamps
# ---------------------------------------------------------------------

def mk_id(author=None):
    """
    Pair containing a brand new id and (false) creation-date

    Parameters
    ----------
    author: string, optional
        If no author is given, use 'stac'.
    """
    if author is None:
        author = 'stac'
    mk_id.counter += 1
    fake_timestamp = mk_id.starting_time + mk_id.counter
    the_id = '_'.join([author, str(fake_timestamp)])
    return (the_id, fake_timestamp)


def init_mk_id(start=None):
    """
    Initalise our glozz id/timestamp generator
    Should be called once.
    """
    # not sure why this is preferable to time.time()
    # inherited it from the old version of the code
    now = time.mktime(datetime.datetime.now().timetuple())
    mk_id.starting_time = int(now) if start is None else start
    mk_id.counter = 0

# ---------------------------------------------------------------------
# parsing annotations
# ---------------------------------------------------------------------


def edu_spans(text, pieces):
    """
    Return a list of tuples representing the spans from one segment
    to another
    """
    spans = []
    next_seg_left = len(text)
    for tseg in pieces:
        tseg_l = tseg.lstrip()
        tseg_lr = tseg_l.rstrip()
        padding_left = len(tseg) - len(tseg_l)
        padding_right = len(tseg_l) - len(tseg_lr)
        tmp_seg_left = next_seg_left + padding_left
        tmp_seg_right = tmp_seg_left + len(tseg_lr)
        next_seg_left = tmp_seg_right + padding_right
        spans.append(Span(tmp_seg_left, tmp_seg_right))
    return spans


def parse_builds(builds):
    """
    Parse builds string from csv and return as a somewhat friendlier
    string that would go in the .aa file
    """
    res = []
    builds = builds.strip()  # implies YUCK => return ""
    if builds:
        for item in builds.split("];"):
            if ']' not in item:
                item += ']'
            key, val = tuple(item.split("="))
            count = len(set(eval(val.replace("; ", ","))))
            res.append("{key}={count}".format(key=key, count=count))
    return "; ".join(res)


def parse_resources(resources):
    """
    Parse resources string from csv and return a somewhat friendlier
    string that would go in the .aa file
    """
    return resources.split("; unknown=")[0]


def read_events(previous, current, turns):
    """
    Given two indices and a list of turns ::

        previous cutoff
        ...
        ...  <-- look for last trade here
        ...
        current turn
        ... (server turns...) <-- stop when no more server turns
        ...
        ...

    Return: rolls and resources from the current turn to the
    next player turn; and the last trade we see between the
    previous and current turn

    NB: this both looks behind (for prior trades), and ahead
    for upcoming server turns
    """

    def is_server(turn):
        "if a csv row corresponds to a server turn"
        return turn.emitter in ['Server', 'UI']

    # server messages before/after the current row
    after = [x.rawtext for x in
             takewhile(is_server, islice(turns, current, None))]
    before = [x.rawtext for x in
              turns[previous:current] if is_server(x)]

    trades = [x for x in before if 'traded' in x]

    # FIXME: I don't understand why we only collect the last trade
    # what's the motivation behind this? there are certainly cases
    # where we have more than one prior trade
    #
    # I think this this is a bug. It might be motivated by an idea
    # that you only have one trade in a negotiation or a dice-roll,
    # but there's two reasons why this can't be:
    #
    # * a player may trade with more than person in their turn
    # * we may have more than one dice roll in a dialogue
    #
    # But fixing this could be a bit tricky because
    #
    # - a dialogue is triggered by a dice roll
    # - its trades come before the trigger
    # - the dice rolls and resource distributions come
    #   at or after the trigger
    #
    # The triggers establish a cap on how far back we search
    # for trades; in addition to returning all trades up to the
    # the previous trigger, we should make sure that the
    # before/after view is consistent
    return Events(rolls=[x for x in after if 'rolled a' in x],
                  resources=[x for x in after if 'gets' in x],
                  trades=trades[-1] if trades else None)


# ---------------------------------------------------------------------
# building output
# ---------------------------------------------------------------------

def append_span(parent, left, right):
    """
    Append a positioning element to its parent
    (part of a span)
    """
    def single(elm, name, idx):
        "single position"
        sub = SubElement(elm, name)
        SubElement(sub, 'singlePosition', {'index': str(idx)})

    elm = SubElement(parent, 'positioning')
    single(elm, 'start', left)
    single(elm, 'end', right)


def append_unit(root, utype, features, left, right, author=None):
    """
    Append a new unit level annotation to the given root element.
    Note that this generates a new identifier behind the scenes.

    Parameters
    ----------
    author: string, optional
        If None, 'stac' is used (default value).
    """
    if author is None:
        author = 'stac'
    unit_id, date = mk_id(author=author)
    if right < left:
        raise Exception("Span with right boundary less than left")

    metadata = [('author', author),
                ('creation-date', str(date)),
                ('lastModifier', 'n/a'),
                ('lastModificationDate', '0')]
    elm_unit = SubElement(root, 'unit', {'id': unit_id})
    elm_metadata = SubElement(elm_unit, 'metadata')
    for key, val in metadata:
        SubElement(elm_metadata, key).text = val
    elm_charact = SubElement(elm_unit, 'characterisation')
    SubElement(elm_charact, 'type').text = utype

    elm_features = SubElement(elm_charact, 'featureSet')
    for key, val in features:
        f_elm = SubElement(elm_features, 'feature', {'name': key})
        f_elm.text = val

    append_span(elm_unit, left, right)


def append_edu(root, span, is_player):
    """
    Append annotations for the given edu to the root
    """
    utype = 'Segment' if is_player else 'NonplayerSegment'
    append_unit(root,
                utype=utype,
                left=span.left,
                right=span.right,
                features=[])


def append_turn(root, curr_turn, span, is_player):
    """
    Append annotations for the given turn to the root
    """
    append_unit(root,
                utype='paragraph',
                left=span.left,
                right=span.right,
                features=[])

    feats = [('Identifier', curr_turn.number),
             ('Timestamp', curr_turn.timestamp),
             ('Emitter', curr_turn.emitter),
             ('Resources', parse_resources(curr_turn.res)),
             ('Developments', parse_builds(curr_turn.builds)),
             ('Comments', 'Please write in remarks...')]

    utype = 'Turn' if is_player else 'NonplayerTurn'
    append_unit(root, utype=utype,
                left=span.left,
                right=span.right,
                features=feats)


def append_dialogue(root, event, span):
    """
    Append annotations for the given dialogue to the root
    """

    if event is not None:
        rolls = " ".join(event.rolls)
        # extra space for backwards diffability
        resources = (" " + " ".join(event.resources)
                     if event.resources else "")
        trades = event.trades
        features = [('Dice_rolling', rolls),
                    ('Gets', resources),
                    ('Trades', trades)]
    else:
        features = []
    append_unit(root,
                utype='Dialogue',
                left=span.left,
                right=span.right,
                features=features)


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------


# pylint: disable=star-args
def read_row(row):
    """
    Either the contents of the row or None if it's server content
    """
    if len(row) >= 6 and len(row) < 8:
        padding = [''] * (8 - len(row))
        the_row = row + padding
    else:
        the_row = row
    return Turn(*the_row)
# pylint: enable=star-args


def read_rows(csvrows):
    """
    From a csvrows to Turn objects (generator)
    """
    for i in range(0, len(csvrows)):
        row = csvrows[i]
        try:
            yield read_row(row)
        except Exception:
            print("Error on row %d: %s" % (i + 1, row),
                  file=sys.stderr)
            raise


def utf8_csv_reader(utf8_data, **kwargs):
    """
    Read utf-8 encoded CSV data as Unicode strings.

    The issue here is that the Python csv library seems to work on bytestrings.
    To work with arbitrary Unicode files, they do this thing where they encode
    the Unicode into UTF-8 on read (yes, encode), and decode it back.  This
    seems rather silly to do if you already know the encoding is UTF-8 and you
    just want the Unicode behind it.
    """
    csv_reader = csv.reader(utf8_data, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def save_output(basename, dialoguetext, root):
    """Save output to a pair of files with a given name prefix.

    The pair of files has extensions .ac (for text) and .aa (for
    annotations).

    Parameters
    ----------
    basename : string
        Basename for files.
    dialoguetext : string
        Text that supports the annotation.
    root : xml.etree.Element
        XML representation of the annotation on `dialoguetext`.
    """
    with codecs.open(basename+".ac", "w", "utf-8") as out:
        out.write(dialoguetext)
    with codecs.open(basename+".aa", "w", "ascii") as out:
        out.write(prettify(root))


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------


def process_turn(root, dialoguetext, turn, is_player):
    """
    Process a single turn and append any resulting annotations to the
    root element.

    Return the augmented text
    """
    prefix = " : ".join([turn.number, turn.emitter, ""])
    dialoguetext += prefix
    if is_player:
        # split on '&'
        # NEW except if it is escaped (preceded by '\'); then delete the
        # escaping character to restore the original text
        # this pattern uses "negative lookbehind" (?<!...),
        # see doc of the `re` module
        turn_segments = [x for x in re.split('(?<![\\\])&', turn.rawtext)
                         if len(x) > 0]
        turn_segments = [x.replace('\&', '&') for x in turn_segments]
    else:
        pre_segments = [x for x in turn.rawtext.split('. ')]
        if pre_segments:
            turn_segments = [x + '. ' for x in pre_segments[:-1]]
            turn_segments.append(pre_segments[-1])
        else:
            turn_segments = pre_segments
        turn_text = '. '.join(turn_segments)

    turn_text = ''.join(turn_segments)
    seg_spans = edu_spans(dialoguetext, turn_segments)

    # .ac buffer
    dialoguetext += turn_text + " "
    # .aa typographic annotations

    if dialoguetext.index(turn_text) != 0:
        typstart = (len(dialoguetext) -
                    len(turn_text) -
                    len(prefix) -
                    1)
    else:
        typstart = 0
    typend = len(dialoguetext) - 1

    # .aa actual pre-annotations (Turn ID, Timestamp, Emitter)
    append_turn(root, turn, Span(typstart, typend), is_player)
    for span in seg_spans:
        append_edu(root, span, is_player)

    return dialoguetext


def process_turns(turns, gen):
    """
    Process a list of Turns and return a pair of:

    * text
    * standoff annotations (an XML element)

    Parameters
    ----------
    turns :
    gen : int
        Generation for which to generate turns from the soclog.
    """
    root = Element('annotations',
                   # to remove, but here for diff compatibility for now
                   {'version':'1.0', 'encoding':'UTF-8', 'standalone':'no'}
                   )
    root.append(Comment('Generated by csvtoglozz.py'))

    dialoguetext = " "  # for the .ac file
    prev_dialogue = None
    i_old = 0

    turn_to_roll_idc = [i for i, turn in enumerate(turns)
                        if ("turn to roll the dice" in
                            turn.rawtext)]

    for i, turn in enumerate(turns):
        # right boundary of dialogue
        if gen < 3:
            # ling versions of the corpus

            # player turns
            if turn.emitter not in ["Server", "UI"]:
                dialoguetext = process_turn(root, dialoguetext, turn,
                                            is_player=True)
                continue

            # cut immediately after
            # (MM 2016-06-14: seems to be immediately before)
            # "X rolled a M and a N"
            if "rolled a" in turn.rawtext:
                # hence, a dialogue is between the beginning and such a
                # text (minus server's turns), or between such a text
                # + 1 and another such text (minus server's turns).
                span = Span(left=prev_dialogue.right if prev_dialogue else 0,
                            right=len(dialoguetext) - 1)
                prev_dialogue = span

                if span.left == span.right:
                    i_old = i
                    # ignore consecutive dice rolls
                else:
                    event = read_events(i_old, i, turns)
                    i_old = i
                    # Generate the actual annotation !
                    append_dialogue(root, event, span)

        else:
            # situated versions

            # * current turn
            emit_cur = turn.emitter
            txt_cur = turn.rawtext
            # * previous turn
            if i > 0:
                turn_prev = turns[i - 1]
                emit_prev = turn_prev.emitter
                txt_prev = turn_prev.rawtext

            # if a player just won the game, split here
            if (i > 0
                and emit_prev == 'Server'
                and 'has won the game' in txt_prev):
                # group subsequent messages as a new turn
                span = Span(left=(prev_dialogue.right
                                  if prev_dialogue else 0),
                            right=len(dialoguetext) - 1)
                prev_dialogue = span
                if span.left == span.right:
                    i_old = i
                    # ignore consecutive dice rolls (??)
                else:
                    event = read_events(i_old, i, turns)
                    i_old = i
                    # Generate the actual annotation !
                    append_dialogue(root, event, span)

            # player turns
            if turn.emitter not in ["Server", "UI"]:
                dialoguetext = process_turn(root, dialoguetext, turn,
                                            is_player=True)
                continue

            # currently, all dialogue splits are triggered by a message
            # from Server or UI
            # different cases:
            elif emit_cur == 'Server':
                if "turn to roll the dice" in txt_cur:
                    # "It's Y's turn to roll the dice." if the previous
                    # turn was "X ended their turn."
                    # FIXME rewrite with a regex
                    # the current implementation does [5:] to skip the
                    # leading "It's " (yerk)
                    player_cur = txt_cur.strip().split(
                        "'s turn to roll the dice.")[0][5:]
                    # check previous turn (for non-initial turn only)
                    if i > 0:
                        if "ended their turn" in txt_prev:
                            # FIXME rewrite with a regex
                            player_prev = txt_prev.strip().split(
                                " ended their turn.")[0]
                            if player_prev != player_cur:
                                # the current turn starts a new game turn
                                span = Span(left=(prev_dialogue.right
                                                  if prev_dialogue else 0),
                                            right=len(dialoguetext) - 1)
                                prev_dialogue = span
                                if span.left == span.right:
                                    i_old = i
                                    # ignore consecutive dice rolls (??)
                                else:
                                    event = read_events(i_old, i, turns)
                                    i_old = i
                                    # Generate the actual annotation !
                                    append_dialogue(root, event, span)

                        elif (i == turn_to_roll_idc[0]
                              and "built a road" in txt_prev):
                            # first standard game turn, following the
                            # initial setup phase when each player
                            # builds a settlement and a road, twice
                            player_prev = txt_prev.split(
                                " built a road.")[0]
                            if player_prev == player_cur:
                                # the current turn starts a new game turn
                                span = Span(left=(prev_dialogue.right
                                                  if prev_dialogue else 0),
                                            right=len(dialoguetext) - 1)
                                prev_dialogue = span
                                if span.left == span.right:
                                    i_old = i
                                    # ignore consecutive dice rolls (??)
                                else:
                                    event = read_events(i_old, i, turns)
                                    i_old = i
                                    # Generate the actual annotation !
                                    append_dialogue(root, event, span)
            elif emit_cur == 'UI':
                if "Game started." in txt_cur:
                    # the current turn starts a new game turn
                    span = Span(left=(prev_dialogue.right
                                      if prev_dialogue else 0),
                                right=len(dialoguetext) - 1)
                    prev_dialogue = span
                    if span.left == span.right:
                        i_old = i
                        # ignore consecutive dice rolls (??)
                    else:
                        event = read_events(i_old, i, turns)
                        i_old = i
                        # Generate the actual annotation !
                        append_dialogue(root, event, span)

        # server turns
        if (gen >= 3 and
            " you" not in turn.rawtext):
            dialoguetext = process_turn(root, dialoguetext, turn,
                                        is_player=False)

    # last dialogue : only if it doesn't end in a Server's statement !!
    if ((prev_dialogue is None or
         prev_dialogue.right != len(dialoguetext) - 1)):

        span = Span(left=prev_dialogue.right if prev_dialogue else 0,
                    right=len(dialoguetext))
        append_dialogue(root, None, span)

    return dialoguetext, root


def parse_args():
    "parse command line arguments"
    parser = argparse.ArgumentParser(description="from STAC internal CSV "
                                     "to Glozz file pair")
    parser.add_argument('-f', '--file',
                        required=True,
                        help="specify input file")
    parser.add_argument('--start',
                        type=int,
                        help="starting timestamp (default: current time)")
    parser.add_argument('--gen', metavar='N', type=int, default=1,
                        help='generation of turns to include (1, 2, 3)')
    return parser.parse_args()


def main():
    "parse command line and handle file"
    args = parse_args()
    init_mk_id(args.start)
    filename = args.file
    with open(filename, 'rb') as incsvfile:  # bytestring
        csvreader = utf8_csv_reader(incsvfile, delimiter='\t')
        csvreader.next()  # skip header row
        turns = list(read_rows(list(csvreader)))
        txt, xml = process_turns(turns, args.gen)

    save_output(filename.split(".")[0], txt, xml)


if __name__ == '__main__':
    main()
