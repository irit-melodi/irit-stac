# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
STAC Glozz conventions
"""

# TODO: should be moved into educe stac module perhaps
# Alternatively the stac module should be kicked out of educe and
# moved into the stac tree

from educe import stac
from educe.glozz import GlozzException



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


def set_anno_date(anno, date):
    """
    Replace the annotation creation date with the given integer
    """
    anno.metadata['creation-date'] = str(date)

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
        return stac.is_turn(anno) and int(anno.features['Identifier']) == tid

    turns = filter(is_match, doc.annotations())
    if not turns:
        raise GlozzException("Turn %d not found" % tid)
    elif len(turns) > 1:
        raise GlozzException("Found more than one turn with id %d" % tid)
    else:
        return turns[0]
