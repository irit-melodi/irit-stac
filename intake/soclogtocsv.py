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
    """
    for gen_key, gen_events in EVENTS.items():
        if any(x in event for x in gen_events):
            gen = gen_key
            break
    else:
        oops = 'IMPOSSIBLE: matched unknown event {}'
        raise Exception(oops.format(event))
    return gen


def parse_line(ctr, line):
    """
    From a soclog line to either None or a Turn ::

        (TurnCounter, String) -> IO (Either None Turn)

    Note that this mutates the turn counter object
    """
    line = line.strip()
    timestamp = line.split(":+", 1)[0]
    timestamp = ":".join(timestamp.split(":")[-4:])

    match1 = SERVER.search(line)
    match2 = PLAYER.search(line) if not match1 else None

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

    if match1:
        event = match1.group("event")
        gen = guess_generation(event)
        if PRIVATE_MESSAGE.search(event):
            # skip private messages
            return None
        ctr.incr_at_gen(gen)
        return mk_turn(str(ctr),
                       match1.group("name"),
                       event)
    elif match2:
        ctr.incr_at_gen(Gen.first)
        state = parse_state(match2.group("state"))
        return mk_turn(str(ctr),
                       match2.group("name"),
                       match2.group("text"),
                       state)
    else:
        return None


def soclog_to_turns(lines):
    """
    Generator from soclog lines to Turn objects
    """
    ctr = TurnCounter()
    for line in lines:
        turn = parse_line(ctr, line)
        if turn is not None:
            yield turn


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
    args = psr.parse_args()

    with codecs.open(args.soclog, 'r', 'utf-8') as soclog:
        lines = soclog.readlines()
        outcsv = stac_csv.mk_csv_writer(args.output)
        outcsv.writeheader()
        for turn in soclog_to_turns(lines):
            outcsv.writerow(turn.to_dict())


if __name__ == '__main__':
    main()
