import collections
import sys

from   educe.corpus import FileId
import educe.util
from   educe        import stac, annotation, graph
import educe.stac.graph   as egr
import educe.stac.corenlp as stac_corenlp
from   educe.stac.tests import FakeEDU, FakeCDU, FakeRelInst, FakeDocument

from   stac.edu import Context

def is_cross_dialogue(contexts):
    """
    The units connected by this relation (or cdu)
    do not inhabit the same dialogue.
    """
    def expect_dialogue(anno):
        return stac.is_edu(anno) or stac.is_cdu(anno)

    def dialogue(anno):
        if stac.is_edu(anno):
            if anno not in contexts:
                return None
            else:
                return contexts[anno].dialogue
        elif stac.is_cdu(anno):
            units = anno.terminals()
            ds    = map(dialogue, units)
            if ds and all(d == ds[0] for d in ds[1:]):
                return ds[0]
            else:
                return None
        else:
            return None

    def is_bad(anno):
        if stac.is_relation_instance(anno):
            members = [ anno.source, anno.target ]
        elif stac.is_cdu(anno):
            members = list(anno.members)
        else:
            members = []

        # don't worry about members which are relations
        members = filter(expect_dialogue, members)

        dialogues = map(dialogue, members)
        if members:
            d0 = dialogues[0]
            return any(not d or d != d0 for d in dialogues)
        else:
            return False
    return is_bad

# ---------------------------------------------------------------------
# pre-annotation level errors
# ---------------------------------------------------------------------

def is_maybe_off_by_one(text, anno):
    """
    True if an annotation has non-whitespace characters on its
    immediate left/right
    """
    sp    = anno.text_span()
    start = sp.char_start
    end   = sp.char_end
    start_ok = start == 0         or text[start - 1].isspace()
    end_ok   = end   == len(text) or text[end].isspace()
    return not (start_ok and end_ok)


# ---------------------------------------------------------------------
# graph errors
# ---------------------------------------------------------------------

def containing_cdu_chain(g, n):
    """
    Given an annotation, return a list which represents its
    containing CDU, the container's container, and forth.
    Return the empty list if no CDU contains this one.
    """
    cdu    = n
    res    = []
    while cdu:
        node = g.nodeform(cdu)
        res.append(node)
        cdu  = g.containing_cdu(node)
    return res[1:] # drop the node itself

def is_puncture(g, contexts, r):
    """
    Relation in a graph that traverse a CDU boundary
    """
    if not stac.is_relation_instance(g.annotation(r)):
        return False
    n_from, n_to = g.links(r)
    cdus_from = containing_cdu_chain(g, n_from)
    cdus_to   = containing_cdu_chain(g, n_to)
    prefix    = len(cdus_from) - len(cdus_to)
    return prefix < 0 or cdus_from[prefix:] != cdus_to

def is_weird_ack(g, contexts, r):
    """
    Relation in a graph that represent a question answer pair
    which either does not start with a question, or which ends
    in a question.

    Note the detection process is a lot sloppier when one of
    the endpoints is a CDU. If all EDUs in the CDU are by
    the same speaker, we can check as usual; otherwise, all
    bets are off, so we ignore the relation.

    Note: slightly curried to accept contexts as an argument
    """
    def edu_speaker(n):
        if n in contexts:
            speaker = contexts[n].turn.features['Emitter']
            return speaker
        else:
            return None

    def node_speaker(n):
        if stac.is_edu(n):
            return edu_speaker(n)
        elif stac.is_cdu(n):
            terms    = n.terminals()
            speakers = list(frozenset(map(edu_speaker, n.terminals())))
            if len(speakers) == 1:
                return speakers[0]
            else:
                return None
        else:
            return None

    n1, n2 = g.links(r)
    is_ty  = g.annotation(r).type == 'Acknowledgement'
    anno1  = g.annotation(n1)
    anno2  = g.annotation(n2)
    speaker1 = node_speaker(anno1)
    speaker2 = node_speaker(anno2)
    is_talking_to_self = speaker1 and speaker2 and speaker1 == speaker2
    return is_ty and is_talking_to_self

def dialogue_graphs(k, doc, contexts):
    """
    Return a dict from dialogue annotations to subgraphs
    containing at least everything in that dialogue (and
    perhaps some connected items)
    """
    dialogues = collections.defaultdict(list)
    graphs    = {}
    for u,v in contexts.items():
        d = v.dialogue
        dialogues[d].append(u)
    for d,units in dialogues.items():
        def in_dialogue(x):
            if stac.is_edu(x):
                return x in units
            elif stac.is_relation_instance(x):
                return x.source in units and x.target in units
            elif stac.is_cdu(x):
                return all(t in units for t in x.terminals())
            else:
                return False
        graphs[d] = egr.Graph.from_doc({k:doc},k, pred=in_dialogue)
    return graphs

def is_disconnected(gr, contexts, x):
    """
    An EDU is considered disconnected unless:

    * it has an incoming link or
    * it has an outgoing Conditional link
    * it's at the beginning of a dialogue

    In principle we don't need to look at EDUs that are disconnected
    on the outgoing end because (1) it's can be legitimate for
    non-dialogue-ending EDUs to not have outgoing links and (2) such
    information would be redundant with the incoming anyway
    """
    BACKWARDS_WHITELIST = ["Conditional"]
    def rel_type(rel):
        "relation type for a given link (string)"
        return gr.annotation(gr.mirror(rel)).type

    edu = gr.annotation(x)
    if edu not in contexts:
        return True
    else:
        ctx      = contexts[edu]
        dialogue = ctx.dialogue
        first_turn_span = ctx.dialogue_turns[0].text_span()
        first_turn_text = gr.doc.text(first_turn_span)
        first_turn_pref = stac.split_turn_text(first_turn_text)[0]
        first_turn_start = first_turn_span.char_start + len(first_turn_pref)
        rel_links    = [ r for r in gr.links(x) if gr.is_relation(r) ]
        has_incoming = any(x == gr.links(r)[1] for r in rel_links)
        has_outgoing_whitelist = any(x == gr.links(r)[0] and
                                     rel_type(r) in BACKWARDS_WHITELIST
                                     for r in rel_links)
        espan        = edu.text_span()
        is_at_start  = espan.char_start == first_turn_start
        return not (has_incoming or has_outgoing_whitelist or is_at_start)

# ---------------------------------------------------------------------
# annotation errors
# ---------------------------------------------------------------------

stac_expected_features =\
        {'EDU'        : frozenset(['Addressee','Surface_act']),
         'relation'   : frozenset(['Argument_scope']),
         'Resource'   : frozenset(['Status','Quantity','Correctness','Kind']),
         'Preference' : frozenset(),
         'Several_resources'      : frozenset(['Operator']),
         'Complex_discourse_unit' : frozenset()
         }

# lowercase stripped
stac_missing_feature_txt_whitelist =\
        frozenset([":)",":p",":d",":o",":/",":(","^_^","...","lol"])

def rough_type(anno):
    if anno.type == 'Segment' or stac.is_edu(anno):
        return 'EDU'
    elif stac.is_relation_instance(anno):
        return 'relation'
    else:
        return anno.type

def missing_features(doc, anno):
    rty = rough_type(anno)
    txt = doc.text(anno.text_span()).strip().lower()
    if rty == 'EDU' and txt in stac_missing_feature_txt_whitelist:
        return frozenset()
    elif rty in stac_expected_features:
        expected = stac_expected_features[rty]
        present  = frozenset(k for k,v in anno.features.items() if v)
        return expected - present
    else:
        return frozenset()

def unexpected_features(doc, anno):
    rty = rough_type(anno)
    txt = doc.text(anno.text_span()).strip().lower()
    ignored = frozenset(['Comments', 'highlight'])

    if rty in stac_expected_features:
        expected = stac_expected_features[rty]
        present  = frozenset(anno.features.keys())
        leftover = present - ignored - expected
        return { k : anno.features[k] for k in leftover }
    else:
        return {}

def is_fixme(feature_value):
    return feature_value and feature_value[:5] == "FIXME"

def fixme_features(doc, anno):
    rty = rough_type(anno)
    txt = doc.text(anno.text_span()).strip().lower()
    return { k:v for k,v in anno.features.items() if is_fixme(v) }
