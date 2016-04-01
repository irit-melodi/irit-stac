#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert soclog files (from STACSettlers/JSettlers) to an internal CSV
format used by the STAC project.

This CSV file is largely intended for manual EDU segmentation or
study by a human. Because manual EDU segmentation is a crucial part
of our annotation process, it is an integral part of the whole
automated parsing pipeline, but it need not be in a sense. It's
worth remembering that it's something we made up and could easily
discard if no longer fit for purpose.

Each row corresponds to an "annotation turn". An annotation turn is a
*much* finer grained object than a Catan game turn. It roughly
corresponds to either a single game event, or a player chat event
(ie. every time somebody hits enter).  It has the following columns:

    - ID : an integer
    - timestamp: HH:MM:ss.SSS (S fraction of a second)
    - emitter: a string holding the identifier of the speaker of the turn
    - resources: a set of feature:value pairs
    - buildups: a set of feature:before-after pairs (NB: we inherited this
      notion of before-after pairs from a older verison of this code, but
      it's not clear what these pairs represent, possibly in the case of roads
      it could represent individual stretches)
    - text: the text of the turn
    - annotations: free form strings (not clear what these are)
    - comments: free form strings (offhand comments from pilot annotators)
"""
from __future__ import print_function

import argparse
import codecs
from collections import namedtuple, OrderedDict
from itertools import chain
import re
import string
import sys

from educe.stac.util import csv as stac_csv

# TODO write tests for these
TEST1 = ("2011:10:10:17:46:57:481:+0100:GAME-TEXT-MESSAGE:"
         "[game=pilot01|player=Tomm|speaking-queue=[]|"
         "clay=0|ore=1|sheep=0|wheat=0|wood=1|unknown=0|knights=1|"
         "roads=[69,86,70,71,72,73,90]|settlements=[69,103,107]|"
         "cities=[]|dev-cards=1|text=Hey!]")

TEST2 = ("2011:10:10:16:37:53:803:+0100:SOCGameTextMsg:"
         "game=pilot01|nickname=Server|"
         "text=Tomm traded 1 sheep for 1 ore from Dave.")


# extra space for empty columns, only really needed for
# backwards compatibility in my opinion
YUCK = u' '


# non-linguistic events:
# * 1st gen: trade, resource, dice roll, build, offer
# * 3rd gen: robber, steal, monopoly, discard, card play,
#   and various events about the game interface and status
EVENTS = {
    # non-ling events exported to CSV in the first round of annotation
    1: [
        'traded',
        'gets',
        'rolled',
        'built',
        'made an offer to trade'
    ],
    # additional non-ling events for the second round of annotation
    3: [
        'robber',
        'stole',
        # private by rights but treating as public
        # because it's so useful
        "can't end your turn yet",
        'Type *ADDTIME* to',
        'game will expire in',
        'has won the game',
        'discarded',
        'needs to discard',
        'played a',
        # WIP: capture additional server messages
        # * by request on the trello card
        'monopolized',
        # * on my own initiative (MM: ask JH and NA)
        'picking a starting player',
        "can't make that trade",
        "can't roll right now",
        # * caught by NA on pilot14
        "board reset",
        # * caught by NA on pilot01
        "left the gam",
    ]
}

# private messages: explicitly ignored
PRIVATE_MESSAGE = re.compile(
    r'^You (stole|monopolized|have been connected)|stole .* from you'
)

# server messages
SERVER_RE = (r"(?P<name>Server)\|text="
             r"(?P<event>.+(" +
             r'|'.join(chain.from_iterable(EVENTS.values())) +
             r").+$)")
SERVER = re.compile(SERVER_RE)

# player messages
PLAYER = re.compile(r"player=(?P<name>[^|]+)\|speaking-queue=\[\]\|"
                    r"(?P<state>.+)\|text=(?P<text>.+)\]$")

# 2nd gen: spectator messages
# they appear in the soclog as a timestamp-less line, that triggers
# two uninteresting but timestamped lines in the soclog ;
# we read the first of these to infer a timestamp for the spectator
# message (cf. soclog_to_turns)
SPECTATOR = re.compile(r"^player=(?P<name>[^|]+)\|speaking-queue=\[\]\|"
                       r"text=(?P<text>.+)$")

# 3rd gen: other game events, visible on the UI but not linguistically
# realized ; as of 2016-03-15, all the following were explicitly
# requested on the trello card
OTHER_EVENTS = {
    'game state 0': (
        r"SOCGameState:game=[^|]+\|state=0",
        'Game state 0.'
    ),
    'join game': (
        (r"SOCJoinGame:nickname=(?P<name>[^|]+)\|password=[^|]+\|" +
         r"host=(?P<host>[^|]+)\|"),
        '{name} joined the game.'
    ),
    'sit down': (
        (r"SOCSitDown:game=[^|]+\|nickname=(?P<name>[^|]+)\|" +
         r"playerNumber=(?P<plnb>[0-9]+)"),
        '{name} sat down at seat {plnb}.'
    ),
    'start game': (
        # this event appears as a block of lines which is opened
        # and closed by a 'SOCStartGame' line
        r"SOCStartGame",
        'Game started.'
    ),
    'board layout': (
        # this is the first line inside the start game block
        r"SOCBoardLayout",
        'Board layout set.'
    ),
    # linguistically realized (server msg)
    # 'leave game': (
    #     r"SOCLeaveGame:nickname=(?P<name>[^|]+)\|",
    #     '{name} left the game'
    # ),
    'reject offer': (
        # this line appears twice, we should just ignore the
        # 2nd occurrence
        r"SOCRejectOffer:game=[^|]+\|playerNumber=(?P<plnb>[0-9]+)",
        '{name} rejected trade offer.'
    ),
}


class TurnCounter(object):
    """
    counter for turn identifiers (which work a bit like
    software version ids eg. 3.4.9)
    """

    def __init__(self):
        self._top = 0
        self._stack = []

    def push(self):
        'open a subcounter'
        self._stack.append(self._top)
        self._top = 0

    def pop(self):
        'return to the previous counter'
        if len(self._stack) > 0:
            self._top = self._stack.pop()
        else:
            raise Exception('Cannot pop counter {}'.format(self))

    def incr(self):
        'increase the counter'
        self._top += 1

    def __len__(self):
        'stack depth'
        return 1 + len(self._stack)

    def __str__(self):
        version = self._stack + [self._top]
        return '.'.join(str(x) for x in version)

    def incr_at_gen(self, gen):
        'increment this counter according to the current generation'
        while len(self) > gen:
            self.pop()
        while len(self) < gen:
            self.push()
        if len(self) != gen:
            oops = ('impossible: incompatible generation ({})'
                    'and counter ({}) combo')
            raise Exception(oops.format(gen, self))
        self.incr()


class State(namedtuple('State',
                       'resources buildups')):
    "resources and buildups in an entry"

    # pylint: disable=no-self-use
    def _render(self, odict):
        "convert a dictionary to string"
        return "; ".join(u'{}={}'.format(k, v)
                         for k, v in odict.items())
    # pylint: enable=no-self-use

    def resources_string(self):
        "string representation of resources"
        return self._render(self.resources)

    def buildups_string(self):
        "string representation of buildups"
        formatted = OrderedDict()
        for key, nums in self.buildups.items():
            if len(nums) == 1:
                items = None
                # NB: Eric thinks it should be something like this, or
                # alternatively that this pairing mechanism should be limited
                # to roads, but for now backwards compatibility is the main
                # focus
                # items = nums[0]
            else:
                npairs = zip(nums, nums[1:])
                items = '; '.join('{},{}'.format(x, y)
                                  for x, y in npairs)
            if items:
                formatted[key] = '[{}]'.format(items)
        return self._render(formatted)


EMPTY_STATE = State(OrderedDict(), OrderedDict())


def parse_state(snippet):
    """
    From a substring soclog entry to some slightly higher level
    representation of the resources and buildups it represents
    """
    resources = OrderedDict()
    buildups = OrderedDict()
    for item in snippet.split('|'):
        key, value = item.split('=', 1)
        if value.isdigit():
            resources[key] = value
            continue
        num_match = re.match(r'^\[(.*)\]$', value)
        if num_match:
            nums = num_match.group(1).split(',')
            buildups[key] = nums
            continue
        oops = 'IMPOSSIBLE: Unknown key value pair ({}: {}) in state'
        raise Exception(oops.format(key, value, snippet))
    return State(resources, buildups)


def guess_generation(event):
    """
    Given an event string, determine what generation of this
    script it corresponds to

    Returns
    -------
    gen : Gen
        Generation this event belongs to.
    """
    for gen_key, gen_events in EVENTS.items():
        if any(x in event for x in gen_events):
            gen = gen_key
            break
    else:
        oops = 'IMPOSSIBLE: matched unknown event {}'
        raise Exception(oops.format(event))
    return gen


def parse_line(ctr, line, sel_gen=3, parsing_state=None):
    """Parse timestamped line.

    From a soclog line to either None or a Turn ::

        (TurnCounter, String) -> IO (Either None Turn)

    Note that this mutates the turn counter object

    Parameters
    ----------
    ctr : TurnCounter
        Turn counter, layered by generation
    line : string
        String to parse
    sel_gen : int
        Max generation to include.
    parsing_state : dictionary, optional
        Provide a description of the current state of the parsing, e.g.
        to avoid generating duplicate events when the soclog contains
        two or more lines for an event.

    Returns
    -------
    turn : Turn or None
        Turn for the given line.
    """
    # locally store the previous line and update the parsing state
    # for future iterations
    line_prev = parsing_state.get('line_prev', '')
    parsing_state['line_prev'] = line

    # line: <timestamp>:<SOCevent>:<description>
    # the entire timestamp in the soclogs is in fact formatted as
    # year:month:day:hour:minute:second:millisecond:utcoffset
    # i.e. a format specification approximately like:
    # YYYY:MM:DD:HH:MM:SS:mmm:+HHMM
    # here, we keep only part of it, forgetting the year, month, day
    # and signed UTC offset
    timestamp = line.split(":+", 1)[0]
    timestamp = ":".join(timestamp.split(":")[-4:])

    def mk_turn(turn_id, speaker, text, state=None):
        'convenience helper to construct Turn object'
        state = state or EMPTY_STATE
        return stac_csv.Turn(number=turn_id,
                             timestamp=timestamp,
                             emitter=speaker,
                             res=state.resources_string() or YUCK,
                             builds=state.buildups_string(),
                             rawtext=text.replace('&', r'\&'),
                             annot=YUCK,
                             comment=YUCK)

    # server message
    match_server = SERVER.search(line)
    if match_server:
        event = match_server.group("event")
        gen = guess_generation(event)
        if gen > sel_gen:
            return None
        if PRIVATE_MESSAGE.search(event):
            # skip private messages
            return None
        ctr.incr_at_gen(gen)
        return mk_turn(str(ctr),
                       match_server.group("name"),
                       event,
                       state=None)

    # player message
    match_player = PLAYER.search(line)
    if match_player:
        gen = 1
        ctr.incr_at_gen(gen)
        state = parse_state(match_player.group("state"))
        return mk_turn(str(ctr),
                       match_player.group("name"),
                       match_player.group("text"),
                       state=state)
    else:
        # WIP non-ling event
        gen = 3
        if sel_gen < gen:
            return None

        for k, evt_re_msg in OTHER_EVENTS.items():
            evt_re, evt_msg = evt_re_msg  # unpack the event regex and msg
            evt_re_obj = re.compile(evt_re)
            evt_search = evt_re_obj.search(line)
            if not evt_search:
                continue

            # get named groups from regex
            evt_fields = evt_search.groupdict()
            if k == 'game state 0':
                # keep only the first "game state 0"
                if 'game state 0' in parsing_state:
                    continue
                else:
                    parsing_state['game state 0'] = True
            elif k == 'start game':
                # keep only the first "start game"
                if 'start game' in parsing_state:
                    continue
                else:
                    parsing_state['start game'] = True
            elif k == 'join game':
                # keep only the latest "join game" event
                if evt_fields['host'] != 'dummyhost':
                    continue
            elif k == 'sit down':
                # sit down generates two messages, the first one with
                # nickname "dummy" should be ignored
                if evt_fields['name'] == 'dummy':
                    continue
                # store mapping from player number to nickname
                pl_nb = evt_fields['plnb']
                pl_name = evt_fields['name']
                if 'plnb2name' not in parsing_state:
                    parsing_state['plnb2name'] = dict()
                parsing_state['plnb2name'][pl_nb] = pl_name
            elif k == 'reject offer':
                reject_re_obj = re.compile(OTHER_EVENTS['reject offer'][0])
                # reject offer generates two identical messages, the
                # second one should be ignored
                reject_prev = reject_re_obj.search(line_prev)
                if reject_prev:
                    continue

            # this line matches a known pattern: generate a nonling turn
            gen = 3
            ctr.incr_at_gen(gen)
            # extract the field names from the "format string"
            msg_fnames = [name for text, name, spec, conv
                          in string.Formatter().parse(evt_msg)]
            # if a player name is expected but the soclog line only
            # provides a player number, map it
            if 'name' in msg_fnames and 'name' not in evt_fields:
                if 'plnb' in evt_fields:
                    # use player name instead of number, in the generated
                    # message
                    pl_nb = evt_fields['plnb']
                    evt_fields['name'] = parsing_state['plnb2name'][pl_nb]
                else:
                    raise ValueError("Fail to find required player name")
            return mk_turn(str(ctr),
                           'UI',  # custom emitter
                           evt_msg.format(**evt_fields),  # defined text
                           state=None)
        # end WIP

        # last resort case
        return None


def soclog_to_turns(soclog, sel_gen=3):
    """Generator from soclog to Turn objects.

    Parameters
    ----------
    soclog : File
        The soclog file
    sel_gen : int, optional
        Select generation for the extraction script: 1st gen corresponds
        to intake scripts until 2016-01, gen2 adds spectator messages,
        gen3 is for situated communication.
    """
    # WIP keep parsing state ; currently stores mapping from player number
    # to name
    parsing_state = dict()

    ctr = TurnCounter()
    for line in soclog:
        line = line.strip()
        if not line:
            continue
        # line: <timestamp>:<SOCevent>:<description>
        # timestamp is in fact formatted as
        # year:month:day:hour:min:sec:millisec:timezone
        # i.e. a format specification approximately like:
        # yyyy:mm:dd:hh:mm:ss:mmm:ttttt
        # here, we keep only part of the full timestamp, forgetting the year,
        # month, day and timezone.
        # timestamp = line.split(":+", 1)[0]
        timestamp_ht = line.split(":+", 1)

        if len(timestamp_ht) == 2:
            # timestamped line
            turn = parse_line(ctr, line, sel_gen=sel_gen,
                              parsing_state=parsing_state)
            if turn is not None:
                yield turn
        elif len(timestamp_ht) == 1:
            # non-timestamped lines were included from gen2 on
            gen = 2
            if sel_gen < gen:
                continue
            # gen2 linguistic info: spectator messages
            match_spect = SPECTATOR.search(line)
            if match_spect:
                # get timestamp from the next line (we won't use it anyway)
                next_line = next(soclog)
                timestamp = next_line.split(":+", 1)[0]
                timestamp = ":".join(timestamp.split(":")[-4:])
                # increase counter, 2nd generation
                ctr.incr_at_gen(gen)
                # these messages have no game state
                state = EMPTY_STATE
                # create turn
                turn = stac_csv.Turn(number=str(ctr),
                                     timestamp=timestamp,
                                     emitter=match_spect.group("name"),
                                     res=state.resources_string() or YUCK,
                                     builds=state.buildups_string() or YUCK,
                                     rawtext=match_spect.group(
                                         "text").replace('&', r'\&'),
                                     annot=YUCK,
                                     comment=YUCK)
                yield turn
            else:
                raise ValueError("Weird line with no timestamp: " + line)
        else:
            raise ValueError("You should not be here")


def main():
    """
    Parse CLI args, read resulting file write, and write to output
    """
    psr = argparse.ArgumentParser(description='soclog to CSV'
                                  'segmentation file')
    psr.add_argument('soclog', metavar='FILE')
    psr.add_argument('--output', metavar='FILE',
                     type=argparse.FileType('wb'),
                     default=sys.stdout)
    psr.add_argument('--gen', metavar='N', type=int, default=3,
                     help='generation of turns to include (1, 2, 3)')
    args = psr.parse_args()

    with codecs.open(args.soclog, 'r', 'utf-8') as soclog:
        outcsv = stac_csv.mk_csv_writer(args.output)
        outcsv.writeheader()
        for turn in soclog_to_turns(soclog, sel_gen=args.gen):
            outcsv.writerow(turn.to_dict())


if __name__ == '__main__':
    main()
