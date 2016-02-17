#!/usr/bin/env python

"""
Convert soclog files (from STACSettlers/JSettlers) to an internal CSV
format used by the STAC project.

This CSV file is largely intended for manual EDU segmentation or
study by a human. Because manual EDU segmentation is a crucial part
of our annotation process, it is an integral part of the whole
automated parsing pipeline, but it need not be in a sense. It's
worth remembering that it's something we made up and could easily
discard if no longer fit for purpose

Each row corresponds to an "annotation turn". An annotation turn is a
*much* finer grained object than than Catan game turn. It roughly
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
from collections import namedtuple, OrderedDict
from enum import Enum
from itertools import chain
import argparse
import codecs
import re
import sys

from educe.stac.util import csv as stac_csv


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


# pylint: disable=no-init, too-few-public-methods
class Gen(Enum):
    """
    distinction between various generations of the script where we
    have already done some annotations and need turn ids to be
    stable when moving from one version to another
    """
    first = 1
    second = 2
# pylint: enable=no-init, too-few-public-methods

EVENTS = {Gen.first: ['traded',
                      'gets',
                      'rolled',
                      'built',
                      'made an offer to trade'],
          Gen.second: ['robber',
                       'stole',
                       # private by rights but treating as public
                       # because it's so useful
                       "can't end your turn yet",
                       'Type *ADDTIME* to',
                       'game will expire in',
                       'has won the game',
                       'discarded',
                       'needs to discard',
                       'played a']}

PRIVATE_MESSAGE = re.compile(r'^You stole|stole .* from you')

SERVER = re.compile(r"(?P<name>Server)\|text="
                    r"(?P<event>.+(" +
                    r'|'.join(chain.from_iterable(EVENTS.values())) +
                    r").+$)")

PLAYER = re.compile(r"player=(?P<name>[^|]+)\|speaking-queue=\[\]\|"
                    r"(?P<state>.+)\|text=(?P<text>.+)\]$")

# spectator messages, first occurrence in soclog has no timestamp
# but it triggers two lines in the soclog ; we read the first one
# to infer a timestamp (cf. soclog_to_turns)
SPECTATOR = re.compile(r"^player=(?P<name>[^|]+)\|speaking-queue=\[\]\|"
                       r"text=(?P<text>.+)$")

# WIP
# other game events, visible on the UI but not linguistically realized
OTHER_EVENTS = {
    'SOCJoinGame': '{nickname} joined the game',
    'SOCSitDown': '{nickname} sat down',
    'SOCStartGame': 'game started',  # opens *and closes* the start block
    'SOCBoardLayout': 'board layout set',  # inside the start block
    # leaving game is realized linguistically in a Server message
    # 'SOCLeaveGame': '{nickname} left the game',
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
        # we may want to generalise this to arbitrary generations
        # later
        if gen == Gen.first and len(self) == 1:
            self.incr()
        elif gen == Gen.first and len(self) == 2:
            self.pop()
            self.incr()
        elif gen == Gen.second and len(self) == 1:
            self.push()
            self.incr()
        elif gen == Gen.second and len(self) == 2:
            self.incr()
        else:
            oops = ('impossible: incompatible generation ({})'
                    'and counter ({}) combo')
            raise Exception(oops.format(gen, self))


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


def parse_line(ctr, line, include_gen2=True):
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
    include_gen2 : boolean
        If True, include (non-linguistic) 2nd generation information.

    Returns
    -------
    turn : Turn or None
        Turn for the given line.
    """
    # line: <timestamp>:<SOCevent>:<description>
    # the entire timestamp in the soclogs is in fact formatted as
    # year:month:day:hour:minute:second:millisecond:utcoffset
    # i.e. a format specification approximately like:
    # YYYY:MM:DD:HH:MM:SS:mmm:+HHMM
    # here, we keep only part of it, forgetting the year, month, day
    # and signed UTC offset
    timestamp = line.split(":+", 1)[0]
    timestamp = ":".join(timestamp.split(":")[-4:])

    match_server = SERVER.search(line)
    match_player = PLAYER.search(line) if not match_server else None

    def mk_turn(turn_id, speaker, text, state=None):
        'convenience helper to construct Turn object'
        state = state or EMPTY_STATE
        return stac_csv.Turn(number=turn_id,
                             timestamp=timestamp,
                             emitter=speaker,
                             res=state.resources_string() or YUCK,
                             builds=state.buildups_string(),
                             rawtext=text,
                             annot=YUCK,
                             comment=YUCK)

    if match_server:
        event = match_server.group("event")
        gen = guess_generation(event)
        if gen == Gen.second and not include_gen2:
            # don't include (non-linguistic) 2nd generation events
            return None
        if PRIVATE_MESSAGE.search(event):
            # skip private messages
            return None
        ctr.incr_at_gen(gen)
        return mk_turn(str(ctr),
                       match_server.group("name"),
                       event,
                       state=None)
    elif match_player:
        ctr.incr_at_gen(Gen.first)
        state = parse_state(match_player.group("state"))
        return mk_turn(str(ctr),
                       match_player.group("name"),
                       match_player.group("text"),
                       state=state)
    else:
        return None


def soclog_to_turns(soclog, sel_gen='gen2'):
    """Generator from soclog to Turn objects.

    Parameters
    ----------
    soclog : File
        The soclog file
    sel_gen : one of {'gen1', 'gen2_ling_only', 'gen2'}
        Select generation for the extraction script: 1st gen corresponds
        to intake scripts until 2016-01, gen2_ling_only adds spectator
        messages, gen2 is for situated communication.
    """
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
            # don't include non-ling turns from 2nd generation
            include_gen2 = (sel_gen == 'gen2')
            turn = parse_line(ctr, line, include_gen2=include_gen2)
            if turn is not None:
                yield turn
        elif len(timestamp_ht) == 1:
            # these are excluded from gen1
            if sel_gen == 'gen1':
                continue
            # 2nd generation linguistic info: spectator messages
            match_spect = SPECTATOR.search(line)
            if match_spect:
                # get timestamp from the next line (we won't use it anyway)
                next_line = next(soclog)
                timestamp = next_line.split(":+", 1)[0]
                timestamp = ":".join(timestamp.split(":")[-4:])
                # increase counter, 2nd generation
                ctr.incr_at_gen(Gen.second)
                # these messages have no game state
                state = EMPTY_STATE
                # create turn
                turn = stac_csv.Turn(number=str(ctr),
                                     timestamp=timestamp,
                                     emitter=match_spect.group("name"),
                                     res=state.resources_string() or YUCK,
                                     builds=state.buildups_string() or YUCK,
                                     rawtext=match_spect.group("text"),
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
    # choose generation
    psr_gen = psr.add_mutually_exclusive_group()
    psr_gen.add_argument('--gen1',
                         action='store_true',
                         help='only include same turns as in 1st gen')
    psr_gen.add_argument('--gen2-ling-only',
                         action='store_true',
                         help='only include ling turns from 2nd gen')
    args = psr.parse_args()

    # selection of turns to include
    if args.gen1:
        sel_gen = 'gen1'
    elif args.gen2_ling_only:
        sel_gen = 'gen2_ling_only'
    else:
        sel_gen = 'gen2'
    #
    with codecs.open(args.soclog, 'r', 'utf-8') as soclog:
        outcsv = stac_csv.mk_csv_writer(args.output)
        outcsv.writeheader()
        for turn in soclog_to_turns(soclog, sel_gen=sel_gen):
            outcsv.writerow(turn.to_dict())


if __name__ == '__main__':
    main()
