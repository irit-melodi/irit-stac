# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
STAC Glozz conventions
"""

# TODO: should be moved into educe stac module perhaps
# Alternatively the stac module should be kicked out of educe and
# moved into the stac tree

import math
import time
import random

from educe.glozz import GlozzException
import educe.stac


class PseudoTimestamper(object):
    """
    Generator for the fake timestamps used as a Glozz IDs
    """
    def __init__(self):
        start_time = int(time.time())
        noise = math.floor(random.uniform(1, 5000))
        self.initial = int(start_time + noise)
        self.counter = 0

    def next(self):
        """
        Fresh timestamp
        """
        self.counter += 1
        return self.initial + self.counter


class TimestampCache(object):
    """
    Generates and stores a unique timestamp entry for each key.
    You can use any hashable key, for exmaple, a span, or a turn id.
    """

    def __init__(self):
        self.stamps = PseudoTimestamper()
        self.reset()

    def get(self, tid):
        """
        Return a timestamp for this turn id, either generating and
        caching (if unseen) or fetching from the cache
        """
        if tid not in self.cache:
            self.cache[tid] = self.stamps.next()
        return self.cache[tid]

    def reset(self):
        """
        Empty the cache (but maintain the timestamper state, so that
        different documents get different timestamps; the difference
        in timestamps is not mission-critical but potentially nice)
        """
        self.cache = {}


def anno_id_from_tuple(author_date):
    """
    Glozz string representation of authors and dates (AUTHOR_DATE)
    """
    return "%s_%d" % author_date


def anno_id_to_tuple(string):
    """
    Read a Glozz string representation of authors and dates into
    a pair (date represented as an int, ms since 1970?)
    """
    parts = string.split('_')
    if len(parts) != 2:
        msg = "%r is not of form author_date" % string
        raise Exception(msg)
    return (parts[0], int(parts[1]))


def anno_author(anno):
    """
    Annotation author
    """
    return anno.metadata['author']


def anno_date(anno):
    """
    Annotation creation date as an int
    """
    return int(anno.metadata['creation-date'])


def set_anno_author(anno, author):
    """
    Replace the annotation author the given author
    """
    anno.metadata['author'] = author
    anno._anno_id = anno_id_from_tuple((author, anno_date(anno)))


def set_anno_date(anno, date):
    """
    Replace the annotation creation date with the given integer
    """
    anno.metadata['creation-date'] = str(date)
    anno._anno_id = anno_id_from_tuple((anno_author(anno), date))


def is_dialogue(anno):
    """
    If a Glozz annotation is a STAC dialogue.
    """
    return anno.type == 'Dialogue'


def get_turn(tid, doc):
    """
    Return the turn annotation with the desired ID
    """
    def is_match(anno):
        "Is a turn with the right turn number"
        return educe.stac.is_turn(anno) and educe.stac.turn_id(anno) == tid

    turns = filter(is_match, doc.annotations())
    if not turns:
        raise GlozzException("Turn %d not found" % tid)
    elif len(turns) > 1:
        raise GlozzException("Found more than one turn with id %d" % tid)
    else:
        return turns[0]
