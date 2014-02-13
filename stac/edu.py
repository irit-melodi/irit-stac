import warnings
from educe import stac

class Context:
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
        self.turn       = turn
        self.dialogue   = dialogue
        self.position   = position
        self.first      = first

    @classmethod
    def for_edu(cls, doc, edu):
        edu_span    = edu.text_span()
        surrounders = containing(edu_span, doc.units)

        def the(ty):
            xs = [ x for x in surrounders if x.type == ty ]
            if len(xs) == 1:
                return xs[0]
            else:
                msg = 'Was expecting exactly one %s for edu %s, got %d' % (ty, edu.identifier(), len(xs))
                if xs:
                    warnings.warn(msg)
                    return xs[0]
                else:
                    raise Exception(msg)

        turn     = the('Turn')
        dialogue = the('Dialogue')
        # the turns in this dialogue
        dturns   = sorted(turns_in_span(doc, dialogue.span), key=lambda x:x.span)
        position = dturns.index(turn)
        if position is None:
            msg = 'For EDU %s, was expecting turn to be %s, but it\'s not in dialogue %s'\
                    % (edu.identifier(), turn.local_id(), dialogue.local_id())
            raise Exception(msg)
        first = dturns[0]
        return cls(turn, dialogue, position, first)

def enclosed(sp, xs):
    """
    Given an iterable of standoff, pick just those that are
    enclosed by the given span (ie. are smaller and within)
    """
    return filter(lambda x: sp.encloses(x.span), xs)

def containing(sp, xs):
    """
    Given an iterable of standoff, pick just those that
    enclose/contain the given span (ie. are bigger and around)
    """
    return filter(lambda x: x.span.encloses(sp), xs)

def edus_in_span(doc, span):
    """
    Given an document and a text span return the EDUs the
    document contains in that span
    """
    return [ e for e in enclosed(span, doc.units) if stac.is_edu(e) ]

def turns_in_span(doc, span):
    """
    Given a document and a text span, return the turns that the
    document contains in that span
    """
    return [ e for e in enclosed(span, doc.units) if e.type == 'Turn' ]
