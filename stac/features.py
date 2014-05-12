"""
Feature extraction library functions for STAC corpora.
The feature extraction script (rel-info) is a lightweight frontend
to this library
"""

from __future__ import absolute_import, print_function
from collections import defaultdict, namedtuple
from itertools import chain
import collections
import copy
import itertools as itr
import os
import re
import sys

from educe.annotation import Span
from educe.external.parser import\
    SearchableTree,\
    ConstituencyTree
from educe.stac import postag, corenlp
from educe.stac.annotation import turn_id
import educe.corpus
import educe.glozz
import educe.stac
import educe.stac.graph as stac_gr
import educe.util
import fuzzy

import stac.lexicon.pdtb_markers as pdtb_markers
from stac.keys import Key, KeyGroup, MergedKeyGroup, ClassKeyGroup
from stac.lexicon.wordclass import WordClass
from stac.edu import Context, enclosed, edus_in_span

if sys.version > '3':
    def treenode(tree):
        "API-change padding for NLTK 2 vs NLTK 3 trees"
        return tree.label()
else:
    def treenode(tree):
        "API-change padding for NLTK 2 vs NLTK 3 trees"
        return tree.node


class CorpusConsistencyException(Exception):
    """
    Exceptions which arise if one of our expecations about the
    corpus data is violated, in short, weird things we don't
    know how to handle. We should avoid using this for
    things which are definitely bugs in the code, and not just
    weird things in the corpus we didn't know how to handle.
    """
    def __init__(self, msg):
        super(CorpusConsistencyException, self).__init__(msg)


# ---------------------------------------------------------------------
# lexicon configuration
# ---------------------------------------------------------------------


class Lexicon(object):
    """
    Configuration options for a given lexicon: where to find it,
    what to call it, what sorts of results to return
    """

    def __init__(self, key, filename, classes):
        """
        Note: classes=True means we want the (sub)-class of the lexical
        item found, and not just a general boolean
        """
        self.key = key
        self.filename = filename
        self.classes = classes
        self.entries = {}
        self.subclasses = {}

    def read(self, lexdir):
        """
        Read and store the lexicon as a mapping from words to their
        classes
        """
        path = os.path.join(lexdir, self.filename)
        entries = defaultdict(dict)
        subclasses = defaultdict(set)
        for entry in WordClass.read_lexicon(path):
            word = entry.word.lower()
            entries[entry.lex_class][word] = entry.subclass
            subclasses[entry.lex_class].add(entry.subclass)
        self.entries = entries
        if self.classes:
            self.subclasses = {k: frozenset(subcl) for k, subcl
                               in subclasses.items()}


LEXICONS = [Lexicon('domain', 'stac_domain.txt', True),
            Lexicon('robber', 'stac_domain2.txt', False),
            Lexicon('trade', 'trade.txt', True),
            Lexicon('dialog', 'dialog.txt', False),
            Lexicon('opinion', 'opinion.txt', False),
            Lexicon('modifier', 'modifiers.txt', False),
            # hand-extracted from trade prediction code, could
            # perhaps be merged with one of the other lexicons
            # fr.irit.stac.features.CalculsTraitsTache3
            Lexicon('pronoun', 'pronouns.txt', True),
            # collapsed into single is_question feature
            Lexicon('question', 'questions.txt', False),
            Lexicon('ref', 'stac_referential.txt', False)]

PDTB_MARKERS_BASENAME = 'pdtb_markers.txt'

# ---------------------------------------------------------------------
# relation queries
# ---------------------------------------------------------------------


def emoticons(tokens):
    "Given some tokens, return just those which are emoticons"
    return frozenset(token for token in tokens if token.tag == 'E')


def is_just_emoticon(tokens):
    "Return true if a sequence of tokens consists of a single emoticon"
    if not isinstance(tokens, collections.Sequence):
        raise TypeError("tokens must form a sequence")
    return bool(emoticons(tokens)) and len(tokens) == 1


def speaker(turn):
    """
    The speaker for a given turn annotation
    """
    return turn.features['Emitter']


def player_addresees(edu):
    """
    The set of people spoken to during an edu annotation.
    This excludes known non-players, like 'All', or '?', or 'Please choose...',
    """
    k = 'Addressee'
    blacklist = frozenset(['Please choose...', 'All', '?'])
    if k in edu.features:
        addressee = edu.features[k]
        if addressee not in blacklist:
            return frozenset(name.strip() for name in addressee.split(','))
    return frozenset()


def speaker_started_dialogue(ctx):
    """
    Given an EDU context, determine if the speaker for that EDU is the
    same as the speaker for the dialogue
    """
    return speaker(ctx.dialogue_turns[0]) == speaker(ctx.turn)


def position_of_speaker_first_turn(ctx):
    """
    Given an EDU context, determine the position of the first turn by that
    EDU's speaker relative to other turns in that dialogue.
    """
    edu_speaker = speaker(ctx.turn)
    # we can assume these are sorted
    for i, turn in enumerate(ctx.dialogue_turns):
        if speaker(turn) == edu_speaker:
            return i
    oops = "Implementation error? No turns found which match speaker's turn"
    raise CorpusConsistencyException(oops)


def players(docs):
    """
    Return the set of speakers/addressees within a set of (sub)documents. In
    STAC, documents are semi-arbitrarily cut into sub-documents for technical
    and possibly ergonomic reasons, ie. meaningless as far as we are concerned.
    So to find all speakers, we would have to search all the subdocuments of a
    single document.
    """
    speakers = set()
    for doc in docs:
        for anno in doc.units:
            if educe.stac.is_turn(anno):
                turn_speaker = speaker(anno)
                if turn_speaker:
                    speakers.add(turn_speaker)
            elif educe.stac.is_edu(anno):
                speakers.update(player_addresees(anno))
    return frozenset(speakers)


def clean_chat_word(token):
    """
    Given a word and its postag (educe PosTag representation)
    return a somewhat tidied up version of the word.

    * Sequences of the same letter greater than length 3 are
      shortened to just length three
    * Letter is lower cased
    """
    if token.tag == 'E':
        return token.word
    else:
        word = token.word.lower()
        # collapse 3 or more of the same char into 3
        return re.sub(r'(.)\1{2,}', r'\1\1\1', word)


def has_one_of_words(sought, tokens, norm=lambda x: x.lower()):
    """
    Given a set of words, a collection tokens, return True if the
    tokens contain words match one of the desired words, modulo
    some minor normalisations like lowercasing.
    """
    norm_sought = frozenset(norm(word) for word in sought)
    norm_tokens = frozenset(norm(tok.word) for tok in tokens)
    return bool(norm_sought & norm_tokens)


def has_pdtb_markers(markers, tokens):
    """
    Given a sequence of tagged tokens, return True
    if any of the given PDTB markers appears within the tokens
    """
    if not isinstance(tokens, collections.Sequence):
        raise TypeError("tokens must form a sequence")
    words = [t.word for t in tokens]
    return pdtb_markers.Marker.any_appears_in(markers, words)


def lexical_markers(sublex, tokens):
    """
    Given a dictionary (words to categories) and a text span, return all the
    categories of words that appear in that set.

    Note that for now we are doing our own white-space based tokenisation,
    but it could make sense to use a different source of tokens instead
    """
    sought = frozenset(sublex.keys())
    present = frozenset(t.word.lower() for t in tokens)
    return frozenset(sublex[x] for x in sought & present)


def real_dialogue_act(corpus, anno):
    """
    Given an EDU in the 'discourse' stage of the corpus, return its
    dialogue act from the 'units' stage
    """
    twin = educe.stac.twin(corpus, anno)
    edu = twin if twin is not None else anno
    acts = educe.stac.dialogue_act(edu)
    if len(acts) < 1:
        oops = 'Was expecting at least one dialogue act for %s' % anno
        raise CorpusConsistencyException(oops)
    else:
        if len(acts) > 1:
            print("More than one dialogue act for %s: %s" % (anno, acts),
                  file=sys.stderr)
        return list(acts)[0]


def subject_lemmas(span, trees):
    """
    Given a span and a list of dependency trees, return any lemmas
    which are marked as being some subject in that span
    """
    def prunable(tree):
        "is outside the search span, so stop going down"
        return not span.overlaps(tree.span)

    def good(tree):
        "is within the search span"
        return tree.link == "nsubj" and\
            span.encloses(tree.node.text_span())

    subtrees = map_topdown(good, prunable, trees)
    return [tree.node.features["lemma"] for tree in subtrees]


# TODO: maybe shuffle into educe.stac
# The trouble with these TODOs is deciding at what point it's genuinely useful,
# and at what point it's going to clutter the library.  Ideally you pick
# just the right bits and pieces to maximise composability, but I don't
# know how to do that, so the process is a bit organic :-(
def attachments(relations, du1, du2):
    """
    Return any relations between the two discourse units
    """
    def connects(rel, id1, id2):
        "is a rel between the annotations with the two ids"
        return rel.span.t1 == id1 and rel.span.t2 == id2

    def is_match(rel):
        "is a rel between the two discourse units"
        id1 = du1.local_id()
        id2 = du2.local_id()
        return connects(rel, id1, id2) or connects(rel, id2, id1)

    return filter(is_match, relations)


def map_topdown(good, prunable, trees):
    """
    Do topdown search on all these trees, concatenate results.
    """
    return list(chain.from_iterable(
        tree.topdown(good, prunable)
        for tree in trees if isinstance(tree, SearchableTree)))


def enclosed_trees(span, trees):
    """
    Return the biggest (sub)trees in xs that are enclosed in the span
    """
    def prunable(tree):
        "is outside the search span, so stop going down"
        return not span.overlaps(tree.span)

    def good(tree):
        "is within the search span"
        return span.encloses(tree.span)

    return map_topdown(good, prunable, trees)


# ---------------------------------------------------------------------
# features
# ---------------------------------------------------------------------


def _kg(*args):
    """
    Shorthand for KeyGroup, just to save on some indentation
    """
    return KeyGroup(*args)


def tune_for_csv(string):
    """
    Given a string or None, return a variant of that string that
    skirts around possibly buggy CSV implementations

    SIGH: some CSV parsers apparently get really confused by
    empty fields
    """
    if string:
        string2 = string
        string2 = re.sub(r'"', r"''", string2)  # imitating PTB slightly
        string2 = re.sub(r',', r'-COMMA-', string2)
        return string2
    else:
        return '__nil__'


# ---------------------------------------------------------------------
# feature extraction
# ---------------------------------------------------------------------

# The comments on these named tuples can be docstrings in Python3,
# or we can wrap the class, but eh...

# Global resources and settings used to extract feature vectors
FeatureInput = namedtuple('FeatureInput',
                          ['corpus', 'postags', 'parses',
                           'lexicons', 'pdtb_lex',
                           'ignore_cdus', 'debug', 'experimental'])

# Overlaps with FeatureInput a bit; if this keeps up we may merge
# them somehow
Resources = namedtuple('Resources', "lexicons pdtb_lex")

# A document and relevant contextual information
DocumentPlus = namedtuple('DocumentPlus',
                          ['key', 'doc', 'contexts', 'players', 'parses'])


def clean_dialogue_act(act):
    """
    Knock out temporary markers used during corpus annotation
    """
    pref = "F"+"IXME:"  # fooling pylint a bit
    act2 = act[len(pref):] if act.startswith(pref) else act
    return "Other" if act2 == "Strategic_comment" else act2


def friendly_dialogue_id(k, span):
    """
    Dialogue identifier which may be easier to understand when debugging
    the feature vector (based on its text span).

    The regular timestamp based identifiers look too much like each other.
    """
    bname = os.path.basename(educe.stac.id_to_path(k))
    start = span.char_start
    end = span.char_end
    return '%s_%04d_%04d' % (bname, start, end)

# ---------------------------------------------------------------------
# single EDU lexical features
# ---------------------------------------------------------------------


class LexKeyMaker(object):
    """
    Converter from lexical entries to feature keys in the stac.keys based
    framework
    """
    def __init__(self, lexicon):
        self.lexicon = lexicon

    def mk_field(self, entry, subclass=None):
        """
        For a given lexical class, return the name of its feature in the
        CSV file
        """
        subclass_elems = [subclass] if subclass else []
        name = "_".join([self.key_prefix(), entry] + subclass_elems)
        helptxt = "boolean (subclass of %s)" % entry if subclass else "boolean"
        return Key.discrete(name, helptxt)

    def mk_fields(self):
        """
        CSV field names for each entry/class in the lexicon
        """
        if self.lexicon.classes:
            headers = []
            for entry in self.lexicon.entries:
                headers.extend(self.mk_field(entry, subclass=subcl)
                               for subcl in self.lexicon.subclasses[entry])
            return headers
        else:
            return [self.mk_field(e) for e in self.lexicon.entries]

    def key_prefix(self):
        """
        Common CSV header name prefix to all columns based on this particular
        lexicon
        """
        return "lex_" + self.lexicon.key


class LexKeyGroup(KeyGroup, LexKeyMaker):
    def __init__(self, lexicon):
        LexKeyMaker.__init__(self, lexicon)
        description = "%s (lexical features)" % self.key_prefix()
        super(LexKeyGroup, self).__init__(description,
                                          self.mk_fields())

    def help_text(self):
        """
        CSV field names for each entry/class in the lexicon
        """
        header_name = (self.key_prefix() + "_...").ljust(KeyGroup.NAME_WIDTH)
        header = "[D] %s %s" % (header_name, "")
        lines = [header]
        for entry in self.lexicon.entries:
            keyname = entry
            if self.lexicon.classes:
                subkeys = ", ".join(self.lexicon.subclasses.get(entry, []))
                keyname = keyname + "_{%s}" % subkeys
            lines.append("       %s" % keyname.ljust(KeyGroup.NAME_WIDTH))
        return "\n".join(lines)


class PdtbKeyMaker(object):
    def __init__(self, lexicon):
        self.lexicon = lexicon

    def mk_field(self, rel):
        name = '_'.join([self.key_prefix(), rel])
        return Key.discrete(name, "pdtb " + rel)

    def mk_fields(self):
        return [self.mk_field(x) for x in self.lexicon]

    def key_prefix(self):
        return "pdtb"


class MergedLexKeyGroup(MergedKeyGroup):
    def __init__(self, inputs):
        groups =\
            [LexKeyGroup(l) for l in inputs.lexicons] +\
            [PdtbLexKeyGroup(inputs.pdtb_lex)]
        description = "lexical features"
        super(MergedLexKeyGroup, self).__init__(description, groups)

    def help_text(self):
        lines = [self.description,
                 "-" * len(self.description)] +\
            [g.help_text() for g in self.groups]
        return "\n".join(lines)


def _fill_single_edu_lex_features(inputs, current, edu, vec):
    """
    Single-EDU features based on lexical lookup.
    Returns void.
    """
    ctx = current.contexts[edu]
    tokens = ctx.tokens

    # lexical features
    for lex in inputs.lexicons:
        factory = LexKeyMaker(lex)
        for subkey in lex.entries:
            sublex = lex.entries[subkey]
            markers = lexical_markers(sublex, tokens)
            if lex.classes:
                for subclass in lex.subclasses[subkey]:
                    field = factory.mk_field(subkey, subclass)
                    vec[field.name] = subclass in markers
            else:
                field = factory.mk_field(subkey)
                vec[field.name] = bool(markers)


class PdtbLexKeyGroup(KeyGroup, PdtbKeyMaker):
    def __init__(self, lexicon):
        PdtbKeyMaker.__init__(self, lexicon)
        description = "PDTB features"
        super(PdtbLexKeyGroup, self).__init__(description,
                                              self.mk_fields())

    def help_text(self):
        """
        CSV field names for each entry/class in the lexicon
        """
        header_name = (self.key_prefix() + "_...").ljust(KeyGroup.NAME_WIDTH)
        header_help = "if has lexical marker for the given class"
        header = "[D] %s %s" % (header_name, header_help)
        lines = [header]
        for rel in self.lexicon:
            lines.append("       %s" % rel.ljust(KeyGroup.NAME_WIDTH))
        return "\n".join(lines)


def _fill_single_edu_pdtb_features(inputs, current, edu, vec):
    """
    Single-EDU features based on lexical lookup
    (PDTB marker lexicon)
    """
    ctx = current.contexts[edu]
    tokens = ctx.tokens

    # PDTB discoure relation markers
    lex = inputs.pdtb_lex
    factory = PdtbKeyMaker(lex)
    for rel in lex:
        field = factory.mk_field(rel)
        has_marker = has_pdtb_markers(lex[rel], tokens)
        vec[field.name] = has_marker


# ---------------------------------------------------------------------
# single EDU non-lexical features
# ---------------------------------------------------------------------


def is_question(inputs, current, edu):
    """
    Is this EDU a question (or does it contain one?)
    """
    doc = current.doc
    span = edu.text_span()
    has_qmark = "?" in doc.text(span)[-1]
    QWORDS = ["what", "which", "where", "when", "who", "how", "why", "whose"]
    return has_qmark

KEYS_SINGLE_META =\
    _kg("EDU identification features",
        [Key.meta("id",
                  "some sort of unique identifier for the EDU"),
         Key.meta("start", "text span start"),
         Key.meta("end", "text span end")])


KEYS_SINGLE_TOKEN =\
    _kg("token-based features",
        [Key.continuous("num_tokens", "length of this EDU in tokens"),
         Key.discrete("word_first", "the first word in this EDU"),
         Key.discrete("word_last", "the last word in this EDU"),
         Key.discrete("has_player_name_exact",
                      "if the EDU text has a player name in it"),
         Key.discrete("has_player_name_fuzzy",
                      "if the EDU has a word that sounds like "
                      "a player name"),
         Key.discrete("has_emoticons",
                      "if the EDU has emoticon-tagged tokens"),
         Key.discrete("is_emoticon_only",
                      "if the EDU consists solely of an emoticon")])



KEYS_SINGLE_PUNCT =\
    _kg("punctuation features",
        [Key.discrete("has_correction_star",
                      "if the EDU begins with a '*' but does "
                      "not contain others"),
         Key.discrete("ends_with_bang", "if the EDU text ends with '!'"),
         Key.discrete("ends_with_qmark", "if the EDU text ends with '?'")])


KEYS_SINGLE_DEBUG =\
    _kg("debug features",
        [Key.meta("text", "EDU text [debug only]")])


def _fill_single_edu_txt_features(inputs, current, edu, vec):
    """
    Textual features specific to one EDU.
    See related `_fill_single_edu_lex_features`.
    Note that this fills the input `vec` dictionary and
    returns void
    """
    doc = current.doc
    ctx = current.contexts[edu]
    tokens = ctx.tokens
    edu_span = edu.text_span()

    def has_initial_star(span):
        "Text in span has an initial star but no other"
        txt = doc.text(span)
        return txt[0] == "*" and "*" not in txt[1:]

    def ends_with_bang(span):
        "Text in span ends with an exclamation"
        return doc.text(span)[-1] == '!'

    def ends_with_qmark(span):
        """
        Text in span ends with question mark. We might need better detection
        using eg subject-verb inversion from a parser
        """
        return doc.text(span)[-1] == '?'

    # first and last words
    if tokens:
        word_first = clean_chat_word(tokens[0])
        word_last = clean_chat_word(tokens[-1])
    else:
        word_first = None
        word_last = None

    # basic string features
    vec["num_tokens"] = len(tokens)
    vec["start"] = edu_span.char_start
    vec["end"] = edu_span.char_end
    # emoticons
    vec["is_emoticon_only"] = is_just_emoticon(tokens)
    vec["has_emoticons"] = bool(emoticons(tokens))
    # other tokens
    vec["has_player_name_exact"] = has_one_of_words(current.players, tokens)
    vec["has_player_name_fuzzy"] = has_one_of_words(current.players, tokens,
                                                    norm=fuzzy.nysiis)
    # first and last word
    vec["word_first"] = tune_for_csv(word_first)
    vec["word_last"] = tune_for_csv(word_last)
    # string features
    edu_span = edu.text_span()
    vec["ends_with_bang"] = ends_with_bang(edu_span)
    vec["ends_with_qmark"] = ends_with_qmark(edu_span)
    vec["has_correction_star"] = has_initial_star(edu_span)

    if inputs.debug:
        vec["text"] = tune_for_csv(doc.text(edu_span))


KEYS_SINGLE_CHAT =\
    _kg("chat features",
        [Key.discrete("speaker_started_the_dialogue",
                      "if the speaker for this EDU is the same as that "
                      "of the first turn in the dialogue"),
         Key.discrete("speaker_already_spoken_in_dialogue",
                      "if the speaker for this EDU is the same as that "
                      "of a previous turn in the dialogue"),
         Key.continuous("speakers_first_turn_in_dialogue",
                        "position in the dialogue of the turn in which "
                        "the speaker for this EDU first spoke"),
         Key.discrete("turn_follows_gap",
                      "if the EDU turn number is > 1 + previous turn"),
         Key.continuous("position_in_dialogue",
                        "relative position of the turn in the dialogue"),
         Key.continuous("position_in_game",
                        "relative position of the turn in the game"),
         Key.continuous("edu_position_in_turn",
                        "relative position of the EDU in the turn")])


def _fill_single_edu_chat_features(_, current, edu, vec):
    """
    Single-EDU features based on the EDU's relationship with the
    the chat structure (eg turns, dialogues).
    Returns void.
    """
    ctx = current.contexts[edu]
    spk_turn1_pos = 1 + position_of_speaker_first_turn(ctx)
    turn_pos_wrt_dia = 1 + ctx.dialogue_turns.index(ctx.turn)
    turn_pos_wrt_game = 1 + ctx.doc_turns.index(ctx.turn)
    assert spk_turn1_pos <= turn_pos_wrt_dia
    edu_pos = 1 + ctx.turn_edus.index(edu)

    dialogue_tids = list(map(turn_id, ctx.dialogue_turns))
    tid = turn_id(ctx.turn)

    vec["edu_position_in_turn"] = edu_pos
    vec["position_in_dialogue"] = turn_pos_wrt_dia
    vec["position_in_game"] = turn_pos_wrt_game
    vec["turn_follows_gap"] =\
        tid and tid - 1 in dialogue_tids and tid != min(dialogue_tids)
    vec["speaker_started_the_dialogue"] = speaker_started_dialogue(ctx)
    vec["speakers_first_turn_in_dialogue"] = spk_turn1_pos
    vec["speaker_already_spoken_in_dialogue"] =\
        spk_turn1_pos < turn_pos_wrt_dia


KEYS_SINGLE_PARSER =\
    _kg("parser features [experimental]",
        [Key.discrete("lemma_subject",
                      "the lemma corresponding to the subject of this EDU"),
         Key.discrete("has_FOR_np",
                      "if the EDU has the pattern IN(for).. NP")])


def _fill_single_edu_psr_features(inputs, current, edu, vec):
    """
    Single-EDU features that come out of a syntactic parser.
    Returns void.
    """

    def is_nplike(anno):
        "is some sort of NP annotation from a parser"
        return isinstance(anno, ConstituencyTree)\
            and anno.node in ['NP', 'WHNP', 'NNP', 'NNPS']

    def is_prep_for(anno):
        "is a node representing for as the prep in a PP"
        return isinstance(anno, ConstituencyTree)\
            and anno.node == 'IN'\
            and len(anno.children) == 1\
            and anno.children[0].features["lemma"] == "for"

    def is_for_pp_with_np(anno):
        "is a for PP node (see above) with some NP-like descendant"
        return any(is_prep_for(child) for child in anno.children)\
            and anno.topdown(is_nplike, None)

    edu_span = edu.text_span()
    parses = current.parses
    trees = enclosed_trees(edu_span, parses.trees)
    subjects = subject_lemmas(edu_span, parses.deptrees)
    subject = subjects[0] if subjects else None
    vec["has_FOR_np"] = bool(map_topdown(is_for_pp_with_np, None, trees))
    vec["lemma_subject"] = tune_for_csv(subject)


class SingleEduKeys(MergedKeyGroup):
    """
    Features for a single EDU
    """
    def __init__(self, inputs):
        groups = [KEYS_SINGLE_META,
                  KEYS_SINGLE_TOKEN,
                  KEYS_SINGLE_CHAT,
                  KEYS_SINGLE_PUNCT,
                  MergedLexKeyGroup(inputs)]
        if inputs.experimental:
            groups.append(KEYS_SINGLE_PARSER)
        if inputs.debug:
            groups.append(KEYS_SINGLE_DEBUG)
        super(SingleEduKeys, self).__init__("single EDU features",
                                            groups)


def _fill_single_edu_features(inputs, current, edu, vec):
    """
    Fields specific to one EDU (helper)
    """
    vec["id"] = edu.identifier()
    _fill_single_edu_txt_features(inputs, current, edu, vec)
    _fill_single_edu_lex_features(inputs, current, edu, vec)
    _fill_single_edu_pdtb_features(inputs, current, edu, vec)
    _fill_single_edu_chat_features(inputs, current, edu, vec)
    if inputs.experimental:
        _fill_single_edu_psr_features(inputs, current, edu, vec)


# ---------------------------------------------------------------------
# EDU singletons (standalone mode)
# ---------------------------------------------------------------------


KEYS_SINGLE_STANDALONE =\
    _kg("additional keys for single EDU in standalone mode",
        [Key.meta("dialogue", "dialogue that contains both EDUs")])


class SingleEduKeysForSingleExtraction(MergedKeyGroup):
    """
    Features for a single EDU, not used within EDU pair extraction,
    but just in standalone mode for dialogue act annotations
    """
    def __init__(self, inputs):
        groups = [KEYS_SINGLE_STANDALONE,
                  SingleEduKeys(inputs)]
        super(SingleEduKeysForSingleExtraction,
              self).__init__("standalone single EDUs", groups)


def standalone_single_edu_features(inputs, current, edu):
    """
    Fields specific to one EDU (for use in dialogue act annotation)
    """
    vec = SingleEduKeysForSingleExtraction(inputs)
    _fill_single_edu_features(inputs, current, edu, vec)
    dia_span = current.contexts[edu].dialogue.text_span()
    vec["dialogue"] = friendly_dialogue_id(current.key, dia_span)
    return vec


# ---------------------------------------------------------------------
# EDU pairs
# ---------------------------------------------------------------------

# interesting problem: how do we manage the single edu features
# here? one natural response might be to group it all into one
# class but then what we would like to do is to also control the
# help text so that the single edu features appear after all the
# other features (we could conveniently arrange to have this be the
# last block in the hierarchy)

KEYS_PAIR_TUPLE =\
    _kg("artificial tuple features",
        [Key.discrete("ends_with_qmark_pairs",
                      "boolean tuple: if each EDU ends with ?"),
         Key.discrete("dialogue_act_pairs",
                      "tuple of dialogue acts for both EDUs")])


def _fill_edu_pair_edu_features(inputs, current, sf_cache, edu1, edu2, vec):
    """
    Pairwise features that come out of the single-edu features for
    each edu
    """
    vec.edu1 = sf_cache[edu1]
    vec.edu2 = sf_cache[edu2]
    edu1_qmark = vec.edu1["ends_with_qmark"]
    edu2_qmark = vec.edu2["ends_with_qmark"]
    edu1_act = clean_dialogue_act(real_dialogue_act(inputs.corpus, edu1))
    edu2_act = clean_dialogue_act(real_dialogue_act(inputs.corpus, edu2))

    vec["ends_with_qmark_pairs"] = '%s_%s' % (edu1_qmark, edu2_qmark)
    vec["dialogue_act_pairs"] = '%s_%s' % (edu1_act, edu2_act)


KEYS_PAIR_GAP =\
    _kg("the gap between EDUs",
        [Key.continuous("num_edus_between",
                        "number of intervening EDUs (0 if adjacent)"),
         Key.continuous("num_speakers_between",
                        "number of distinct speakers in intervening EDUs"),
         Key.discrete("same_speaker",
                      "if both EDUs have the same speaker"),
         Key.discrete("same_turn", "if both EDUs are in the same turn")])


def _fill_edu_pair_gap_features(inputs, current, sf_cache, edu1, edu2, vec):
    """
    Pairwise features that are related to the gap between two EDUs
    """
    doc = current.doc
    ctx1 = current.contexts[edu1]
    ctx2 = current.contexts[edu2]

    edu1_span = edu1.text_span()
    edu2_span = edu2.text_span()
    big_span = edu1_span.merge(edu2_span)

    # spans for the turns that come between the two edus
    turns_between_span = Span(ctx1.turn.text_span().char_end,
                              ctx2.turn.text_span().char_start)
    turns_between = enclosed(turns_between_span,
                             (t for t in doc.units if t.type == 'Turn'))
    speakers_between = frozenset(speaker(t) for t in turns_between)

    vec["num_edus_between"] = len(edus_in_span(doc, big_span)) - 2
    vec["num_speakers_between"] = len(speakers_between)
    vec["same_speaker"] = speaker(ctx1.turn) == speaker(ctx2.turn)
    vec["same_turn"] = ctx1.turn == ctx2.turn

    if inputs.debug:
        vec["text"] = tune_for_csv(doc.text(big_span))


KEYS_PAIR_BASIC =\
    _kg("core features",
        [Key.meta("dialogue", "dialogue that contains both EDUs"),
         Key.meta("annotator", "annotator for the subdoc")])

KEYS_PAIR_DEBUG =\
    _kg("debug features",
        [Key.meta("text", "text from DU1 start to DU2 end [debug only]")])


class PairKeys(MergedKeyGroup):
    """
    Features for pairs of EDUs
    """
    def __init__(self, inputs):
        groups = [KEYS_PAIR_BASIC,
                  KEYS_PAIR_GAP,
                  KEYS_PAIR_TUPLE]
        if inputs.debug:
            groups.append(KEYS_PAIR_DEBUG)
        self.edu1 = SingleEduKeys(inputs)
        self.edu2 = SingleEduKeys(inputs)
        super(PairKeys, self).__init__("pair features",
                                       groups)

    def csv_headers(self):
        return super(PairKeys, self).csv_headers() +\
            [h + "_DU1" for h in self.edu1.csv_headers()] +\
            [h + "_DU2" for h in self.edu2.csv_headers()]

    def csv_values(self):
        return super(PairKeys, self).csv_values() +\
            self.edu1.csv_values() +\
            self.edu2.csv_values()

    def help_text(self):
        lines = [super(PairKeys, self).help_text(),
                 "",
                 self.edu1.help_text()]
        return "\n".join(lines)


def edu_pair_features(inputs, current, sf_cache, edu1, edu2):
    """
    Subvector for pairwise features between two given discourse units
    """
    ctx1 = current.contexts[edu1]
    dia_span = ctx1.dialogue.text_span()

    vec = PairKeys(inputs)
    vec["dialogue"] = friendly_dialogue_id(current.key, dia_span)
    vec["annotator"] = current.doc.origin.annotator
    _fill_edu_pair_gap_features(inputs, current, sf_cache, edu1, edu2, vec)
    _fill_edu_pair_edu_features(inputs, current, sf_cache, edu1, edu2, vec)

    return vec

# ---------------------------------------------------------------------
# (single) feature cache
# ---------------------------------------------------------------------


class FeatureCache(dict):
    """
    Cache for single edu features.
    Retrieving an item from the cache lazily computes/memoises
    the single EDU features for it.
    """
    def __init__(self, inputs, current):
        self.inputs = inputs
        self.current = current
        super(FeatureCache, self).__init__()

    def __getitem__(self, edu):
        if edu in self:
            return super(FeatureCache, self).__getitem__(edu)
        else:
            vec = SingleEduKeys(self.inputs)
            _fill_single_edu_features(self.inputs,
                                      self.current,
                                      edu,
                                      vec)
            self[edu] = vec
            return vec

    def expire(self, edu):
        """
        Remove an edu from the cache if it's in there
        """
        if edu in self:
            del self[edu]

# ---------------------------------------------------------------------
# extraction generators
# ---------------------------------------------------------------------


def mk_current(inputs, people, k):
    """
    Pre-process and bundle up a representation of the current document
    """
    doc = inputs.corpus[k]
    if not inputs.ignore_cdus:
        # replace all CDUs in links with their recursive heads
        graph = stac_gr.Graph.from_doc(inputs.corpus, k)
        graph.strip_cdus(sloppy=True)

    contexts = Context.for_edus(doc, inputs.postags[k])
    parses = inputs.parses[k] if inputs.parses else None
    doc_people = people[k.doc]
    return DocumentPlus(k, doc, contexts, doc_people, parses)


def get_players(inputs):
    """
    Return a dictionary mapping each document to the set of
    players in that document
    """
    people = {}
    for doc in frozenset(k.doc for k in inputs.corpus):
        people[doc] = players(inputs.corpus[k] for k in inputs.corpus
                              if k.doc == doc)
    return people


def extract_pair_features(inputs, window, discourse_only=True, live=False):
    """
    Return a pair of dictionaries, one for attachments
    and one for relations
    """
    people = get_players(inputs)

    for k in inputs.corpus:
        if discourse_only and k.stage != 'discourse':
            continue
        current = mk_current(inputs, people, k)
        doc = current.doc
        edus = sorted([x for x in doc.units if educe.stac.is_edu(x)],
                      key=lambda x: x.span)

        sf_cache = FeatureCache(inputs, current)
        for edu1 in edus:
            for edu2 in itr.dropwhile(lambda x: x.span <= edu1.span, edus):
                ctx1 = current.contexts[edu1]
                ctx2 = current.contexts[edu2]
                if ctx1.dialogue != ctx2.dialogue:
                    break  # we can break because the EDUs are sorted
                           # so once we're out of dialogue, anything
                           # that follows will also be so
                vec = edu_pair_features(inputs, current, sf_cache, edu1, edu2)
                if window >= 0 and vec["num_edus_between"] > window:
                    break
                rels = attachments(doc.relations, edu1, edu2)
                if live:
                    yield vec, vec
                else:
                    rels_vec = ClassKeyGroup(vec)
                    pairs_vec = ClassKeyGroup(vec)
                    if len(rels) > 1:
                        print('More than one relation between %s and %s' %
                              (edu1, edu2),
                              file=sys.stderr)
                    rels_vec.set_class(rels[0].type if rels else 'UNRELATED')
                    pairs_vec.set_class(bool(rels))
                    yield pairs_vec, rels_vec
            # we shouldn't ever need edu1 again; expiring this means
            # the cache uses constantish memory
            sf_cache.expire(edu1)


def extract_single_features(inputs, live=False):
    """
    Return a dictionary for each EDU
    """
    people = get_players(inputs)
    for k in inputs.corpus:
        if k.stage != 'units':
            continue
        current = mk_current(inputs, people, k)
        doc = current.doc
        edus = [unit for unit in doc.units if educe.stac.is_edu(unit)]
        for edu in edus:
            vec = standalone_single_edu_features(inputs, current, edu)
            if live:
                yield vec
            else:
                act = real_dialogue_act(inputs.corpus, edu)
                cl_vec = ClassKeyGroup(vec)
                cl_vec.set_class(clean_dialogue_act(act))
                yield cl_vec


# ---------------------------------------------------------------------
# input readers
# ---------------------------------------------------------------------


def read_pdtb_lexicon(args):
    """
    Read and return the local PDTB discourse marker lexicon.
    """
    pdtb_lex_file = os.path.join(args.resources, PDTB_MARKERS_BASENAME)
    return pdtb_markers.read_lexicon(pdtb_lex_file)


def init_lexicons(args):
    """
    Read all the lexicons in, from their expected locations
    """
    for lex in LEXICONS:
        lex.read(args.resources)


def _read_resources(args, corpus, postags, parses):
    init_lexicons(args)
    pdtb_lex = read_pdtb_lexicon(args)
    return FeatureInput(corpus, postags, parses,
                        LEXICONS, pdtb_lex,
                        args.ignore_cdus, args.debug, args.experimental)


def read_list_inputs(args):
    """
    Read just the resources and flags needed to do a feature listing
    """
    args.debug = True
    args.experimental = True
    args.ignore_cdus = None
    return _read_resources(args, None, None, None)


def read_common_inputs(args, corpus):
    """
    Read the data that is common to live/corpus mode.
    """
    postags = postag.read_tags(corpus, args.corpus)
    if args.experimental:
        parses = corenlp.read_results(corpus, args.corpus)
    else:
        parses = None
    return _read_resources(args, corpus, postags, parses)


def read_live_inputs(args):
    """
    Read the live Glozz data.
    """
    reader = educe.stac.LiveInputReader(args.corpus)
    anno_files = reader.files()
    corpus = reader.slurp(anno_files, verbose=True)
    return read_common_inputs(args, corpus)


def read_corpus_inputs(args, stage=None):
    """
    Read and filter the part of the corpus we want features for
    """
    args.stage = stage or 'discourse|units'
    is_interesting = educe.util.mk_is_interesting(args)
    reader = educe.stac.Reader(args.corpus)
    anno_files = reader.filter(reader.files(), is_interesting)
    corpus = reader.slurp(anno_files, verbose=True)
    return read_common_inputs(args, corpus)
