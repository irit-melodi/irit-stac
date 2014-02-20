"""
The dialogue and turn surrounding an EDU along with some convenient
information about it
"""

import warnings
from educe import stac, graph
from educe.annotation import Annotation

# ---------------------------------------------------------------------
# enclosure graph
# ---------------------------------------------------------------------

class WrappedToken(Annotation):
    """
    Thin wrapper around POS tagged token which adds a local_id
    field for use by the EnclosureGraph mechanism
    """

    def __init__(self, token):
        self.token = token
        anno_id = WrappedToken._mk_id(token)
        super(WrappedToken, self).__init__(anno_id,
                                           token.span,
                                           "token",
                                           {"tag":token.tag,
                                            "word":token.word})

    @classmethod
    def _mk_id(cls, token):
        """
        Generate a string that could work as a node identifier
        in the enclosure graph
        """
        span = token.text_span()
        return "%s_%s_%d_%d"\
                % (token.word,
                   token.tag,
                   span.char_start,
                   span.char_end)

def _stac_enclosure_ranking(anno):
    """
    Given an annotation, return an integer representing its position in
    a hierarchy of nodes that are expected to enclose each other.

    Smaller negative numbers are higher (say the top of the hiearchy
    might be something like -1000 whereas the very bottom would be 0)
    """
    ranking = {"token": -1,
               "edu": -2,
               "turn": -3,
               "dialogue": -4}

    key = None
    if anno.type == "token":
        key = "token"
    elif stac.is_edu(anno):
        key = "edu"
    elif stac.is_turn(anno):
        key = "turn"
    elif stac.is_dialogue(anno):
        key = "dialogue"

    return ranking[key] if key else 0

# TODO: should probably be moved into educe
class EnclosureGraph(graph.EnclosureGraph):
    """
    An enclosure graph based on STAC conventions
    """
    def __init__(self, doc, postags=None):
        annos = [anno for anno in doc.units if anno.type != 'paragraph']
        if postags:
            annos += [WrappedToken(tok) for tok in postags]
        super(EnclosureGraph, self).__init__(annos,
                                             key=_stac_enclosure_ranking)

class EnclosureDotGraph(graph.EnclosureDotGraph):
    """
    Conventions for visualising STAC enclosure graphs
    """
    def __init__(self, core):
        super(EnclosureDotGraph, self).__init__(core)

    def _unit_label(self, anno):
        span = anno.text_span()
        if anno.type == "token":
            word = anno.features["word"]
            tag = anno.features["tag"]
            return "%s [%s] %s" % (word, tag, span)
        else:
            return "%s %s" % (anno.type, span)

# ---------------------------------------------------------------------
# contexts
# ---------------------------------------------------------------------


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
    def _the(cls, surrounders, typ):
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

    @classmethod
    def _mk_context(cls, edu, turn, dialogue, dturns):
        """
        Build a context out of the minimum information we need
        """
        sorted_dturns = sorted(dturns, key=lambda x: x.span)
        position = sorted_dturns.index(turn)
        if position is None:
            raise Exception(("For EDU %s, was expecting " % edu.identifier()) +
                            ("turn to be %s, but it's " % turn.local_id()) +
                            ("not in dialogue %s" % dialogue.local_id()))
        first = sorted_dturns[0]
        return cls(turn, dialogue, position, first)

    @classmethod
    def for_edu(cls, doc, edu):
        """
        Extract the context for a single EDU
        """
        edu_span = edu.text_span()
        surrounders = containing(edu_span, doc.units)

        turn = cls._the(surrounders, 'Turn')
        dialogue = cls._the(surrounders, 'Dialogue')
        # the turns in this dialogue
        dturns = turns_in_span(doc, dialogue.span)
        return cls._mk_context(edu, turn, dialogue, dturns)

    @classmethod
    def _for_edu_given_graph(cls, enclosure, edu):
        """
        Extract the context for a single EDU, but with the benefit of an
        enclosure graph to avoid repeatedly combing over objects
        """
        turn = cls._the(enclosure.outside(edu), 'Turn')
        dialogue = cls._the(enclosure.outside(turn), 'Dialogue')
        dturns = filter(stac.is_turn, enclosure.inside(dialogue))
        return cls._mk_context(edu, turn, dialogue, dturns)

    @classmethod
    def for_edus(cls, doc, postags=None):
        """
        Return a dictionary of context objects for each EDU in the document

        :rtype dict(educe.glozz.Unit, Context)
        """
        egraph = EnclosureGraph(doc)
        egraph.reduce()
        contexts = {}
        for edu in filter(stac.is_edu, doc.units):
            contexts[edu] = cls._for_edu_given_graph(egraph, edu)
        return contexts

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
