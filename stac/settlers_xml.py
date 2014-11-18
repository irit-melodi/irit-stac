# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)
# pylint: disable=too-few-public-methods

"""
XML communication between JSettlers and the parsing pipeline

Note that we model objects here that may seem to overlap with
what Educe etc provide; but here they are quite specific to
settlers XML
"""

from collections import namedtuple
from enum import Enum

from educe.stac.annotation import RENAMES
import xml.etree.cElementTree as ET



def text_elem(name, text):
    """
    convenience function for creating XML nodes with just text
    """
    tmp = ET.Element(name)
    tmp.text = text
    return tmp


class GameFragment(namedtuple('GameFragment',
                              ['events'])):
    """
    A sequence of events in a game
    """
    def to_xml(self):
        "to settlers XML element (root)"
        node = ET.Element("game_fragment")
        for event in self.events:
            node.append(event.to_xml())
        return node


class ChatMessage(namedtuple('ChatMessage',
                             ['identifier',
                              'edus'])):
    """
    A line of chat from a user
    """
    def to_xml(self):
        "to settlers XML element"
        node = ET.Element("game_event")
        node.append(text_elem("event_id", self.identifier))
        payload = ET.SubElement(node, "chat_message")
        for edu in self.edus:
            payload.append(edu.to_xml())
        return node


class Edu(namedtuple('Edu',
                     ['identifier',
                      'span',
                      'text',
                      'speaker',
                      'surface_act',
                      'dialogue_act',
                      'ds_pairs'])):
    """
    An elementary discourse unit
    """
    def to_xml(self):
        "to settlers XML element"
        node = ET.Element("edu")
        node.append(text_elem("edu_id", self.identifier))
        node.append(text_elem("start", str(self.span.char_start)))
        node.append(text_elem("end", str(self.span.char_end)))
        node.append(text_elem("speaker", self.speaker))
        node.append(text_elem("text", self.text))
        node.append(self.surface_act.to_xml())
        node.append(self.dialogue_act.to_xml())
        ds = ET.Element("discourse_structure")
        for pair in self.ds_pairs:
            ds.append(pair.to_xml())
        node.append(ds)
        return node


class DsPair(namedtuple('DsPair',
                        ['attachment_point',
                         'discourse_relation'])):
    """
    A link from an EDU to its parents
    """
    def to_xml(self):
        "to settles XML element"
        node = ET.Element("ds_pair")
        node.append(text_elem("attachment_point", self.attachment_point))
        rel_node = ET.Element("discourse_relation")
        rel_node.append(self.discourse_relation.to_xml())
        node.append(rel_node)
        return node


# pylint: disable=invalid-name
Resource = Enum('Resource', 'clay ore sheep wheat wood')
# pylint: enable=invalid-name


# pylint: disable=no-init
# no-init ok because enumeration
class SurfaceAct(Enum):
    "what form the EDU has: assertion, request..."
    assertion = 1
    request = 2
    question = 3
    unknown = 4

    def to_xml(self):
        "to settlers XML element"
        node = ET.Element("surface_act")
        # pylint: disable=no-member
        node.append(ET.Element(self.name))
        # pylint: enable=no-member
        return node

    @classmethod
    def from_string(cls, string):
        """
        From STAC representation ::

            String or None -> SurfaceAct
        """
        if string is None:
            return cls.unknown
        elif string == 'Assertion':
            return cls.assertion
        elif string == 'Question':
            return cls.question
        elif string == 'Please choose...':
            return cls.unknown
        else:
            raise ValueError('Unknown surface act: %s' % string)


class DialogueActType(Enum):
    "dialogue act type (nb educe.stac just calls this the dialogue act)"
    accept = 1
    refusal = 2
    offer_or_counteroffer = 3
    other = 4

    def to_xml(self):
        "to settlers XML element"
        return ET.Element(self.name)

    @classmethod
    def from_string(cls, string):
        """
        From STAC representation ::

            String -> SurfaceAct
        """
        string2 = RENAMES.get(string, string)
        if string2 == 'Accept':
            return cls.accept
        elif string2 == 'Refusal':
            return cls.refusal
        elif string2 == 'Offer':
            return cls.offer_or_counteroffer
        elif string2 == 'Counteroffer':
            return cls.offer_or_counteroffer
        elif string2 == 'Other':
            return cls.other
        else:
            raise ValueError('Unknown dialogue act type: %s' % string)


class DialogueAct(object):
    "what form the EDU has: assertion, request..."

    def __init__(self, da_type, resources):
        if da_type == DialogueActType.other and resources is not None:
            raise ValueError("dialogue act 'other' cannot have resources")
        self.da_type = da_type
        self.resources = resources

    def to_xml(self):
        "to settlers XML element"
        node = ET.Element("dialogue_act")
        # pylint: disable=no-member
        act = self.da_type.to_xml()
        node.append(act)
        # pylint: enable=no-member
        return node

    @classmethod
    def from_anno(cls, anno):
        """
        From STAC representation ::

            String or None -> SurfaceAct
        """

class RelationLabel(Enum):
    "discourse relation label"
    continuation = 1
    result = 2
    elaboration = 3
    conditional = 4
    contrast = 5
    qap = 6
    qelab = 7
    acknowledgement = 8
    narration = 9
    correction = 10
    explanation = 11
    alternation = 12
    parallel = 13
    commentary = 14
    clarification_q = 15
    background = 16

    def to_xml(self):
        "to settlers XML element"
        return ET.Element(self.name)

    @classmethod
    def from_string(cls, string):
        """
        From STAC representation ::

            String -> SurfaceAct
        """
        return RELATION_LABELS[string]


RELATION_LABELS =\
    {'Continuation': RelationLabel.continuation,
     'Result': RelationLabel.result,
     'Elaboration': RelationLabel.elaboration,
     'Conditional': RelationLabel.conditional,
     'Contrast': RelationLabel.contrast,
     'Question-answer_pair': RelationLabel.qap,
     'Q-Elab': RelationLabel.qelab,
     'Acknowledgement': RelationLabel.acknowledgement,
     'Narration': RelationLabel.narration,
     'Correction': RelationLabel.correction,
     'Explanation': RelationLabel.explanation,
     'Alternation': RelationLabel.alternation,
     'Parallel': RelationLabel.parallel,
     'Comment': RelationLabel.commentary,
     'Clarification_question': RelationLabel.clarification_q,
     'Background': RelationLabel.background}


# pylint: enable=no-init
