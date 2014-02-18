"""
The dialogue and turn surrounding an EDU along with some convenient
information about it
"""

import warnings
from educe import stac

class Context(object):
    """
    Representation of the surrounding context for an EDU,
    basically the relevant enclosing annotations: turns,
    dialogues. The idea is potentially extend this to a
    somewhat richer notion of context, including things
    like a sentence count, etc.

    * turn     - the turn surrounding this EDU
    * dialogue - the dialogue surrounding this EDU
    * position - this edu occurs in the Nth turn of this dialogue
    * first    - the first turn in this EDU's dialogue

    """
    def __init__(self, turn, dialogue, position, first):
        self.turn = turn
        self.dialogue = dialogue
        self.position = position
        self.first = first

    @classmethod
    def for_edu(cls, doc, edu):
        """
        Extract the context for a single EDU
        """
        edu_span = edu.text_span()
        surrounders = containing(edu_span, doc.units)

        def the(typ):
            """
            Return the surrounding annotation of the given type.
            We are expecting there to be exactly one such surrounder.
            If none, we we consider it worth an exception. If more
            than one, we grit our teeth and move.
            """
            matches = [x for x in surrounders if x.type == typ]
            if len(matches) == 1:
                return matches[0]
            else:
                msg = "Was expecting exactly one %s for edu %s, got %d"\
                        % (typ, edu.identifier(), len(matches))
                if matches:
                    warnings.warn(msg)
                    return matches[0]
                else:
                    raise Exception(msg)

        turn = the('Turn')
        dialogue = the('Dialogue')
        # the turns in this dialogue
        dturns = sorted(turns_in_span(doc, dialogue.span), key=lambda x: x.span)
        position = dturns.index(turn)
        if position is None:
            raise Exception(("For EDU %s, was expecting " % edu.identifier()) +
                            ("turn to be %s, but it's " % turn.local_id()) +
                            ("not in dialogue %s" % dialogue.local_id()))
        first = dturns[0]
        return cls(turn, dialogue, position, first)

def enclosed(span, annos):
    """
    Given an iterable of standoff, pick just those that are
    enclosed by the given span (ie. are smaller and within)
    """
    return [anno for anno in annos if span.encloses(anno.span)]


def containing(span, annos):
    """
    Given an iterable of standoff, pick just those that
    enclose/contain the given span (ie. are bigger and around)
    """
    return [anno for anno in annos if anno.span.encloses(span)]


def edus_in_span(doc, span):
    """
    Given an document and a text span return the EDUs the
    document contains in that span
    """
    return [anno for anno in enclosed(span, doc.units) if stac.is_edu(anno)]


def turns_in_span(doc, span):
    """
    Given a document and a text span, return the turns that the
    document contains in that span
    """
    return [anno for anno in enclosed(span, doc.units) if stac.is_turn(anno)]
