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

SERVER = re.compile(r"(?P<name>Server)\|text="
                    r"(?P<event>.+(traded|gets|rolled|built|"
                    r"made an offer to trade).+$)")
PLAYER = re.compile(r"player=(?P<name>[^|]+)\|speaking-queue=\[\]\|"
                    r"(?P<state>.+)\|text=(?P<text>.+)\]$")


class SoclogEntry(namedtuple('SoclogEntry',
                             'timestamp speaker text state')):
    "interesting entry in the soclog file"
    pass


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
        oops = 'Unknown key value pair ({}: {}) in state'
        raise Exception(oops.format(key, value, snippet))
    return State(resources, buildups)


def parse_line(turn_id, line):
    """
    From a soclog line to either None or a Turn ::

        String -> Either None Turn
    """
    line = line.strip()
    timestamp = line.split(":+", 1)[0]
    timestamp = ":".join(timestamp.split(":")[-4:])

    match1 = SERVER.search(line)
    match2 = PLAYER.search(line) if not match1 else None

    def mk_turn(speaker, text, state=None):
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
        return mk_turn(match1.group("name"),
                       match1.group("event"))
    elif match2:
        state = parse_state(match2.group("state"))
        return mk_turn(match2.group("name"),
                       match2.group("text"),
                       state)
    else:
        return None


def soclog_to_turns(lines):
    """
    Generator from soclog lines to Turn objects
    """
    turn_counter = 1
    for line in lines:
        turn = parse_line(turn_counter, line)
        if turn is not None:
            turn_counter += 1
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
