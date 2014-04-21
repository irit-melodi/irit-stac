"""
Feature extraction library functions for STAC corpora.
The feature extraction script (rel-info) is a lightweight frontend
to this library
"""

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

    def csv_field(self, prefix, entry, subclass=None):
        """
        For a given lexical class, return the name of its feature in the
        CSV file
        """
        subclass_elems = [subclass] if subclass else []
        return '_'.join([prefix, self.key, entry] + subclass_elems)

    def csv_fields(self, prefix):
        """
        CSV field names for each entry/class in the lexicon
        """
        if self.classes:
            headers = []
            for entry in self.entries:
                headers.extend(self.csv_field(prefix, entry, subclass=subcl)
                               for subcl in self.subclasses[entry])
            return headers
        else:
            return [self.csv_field(prefix, e) for e in self.entries]


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
            print >> sys.stderr,\
                'More than one dialogue act for %s: %s' % (anno, acts)
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
# csv files
# ---------------------------------------------------------------------

K_CLASS = "c#CLASS"  # the thing we want to learn
K_DIALOGUE = "m#dialogue"
K_DIALOGUE_ACT_PAIRS = "D#dialogue_act_pairs"
K_ENDS_WITH_QMARK_PAIRS = "D#ends_with_qmark_pairs"
K_NUM_EDUS_BETWEEN = "C#num_edus_between"
K_NUM_SPEAKERS_BETWEEN = "C#num_speakers_between"
K_ANNOTATOR = "m#annotator"
K_TEXT = "m#text"
K_SAME_TURN = "D#same_turn"

# fields for a given EDU (will need to be suffixed, eg. KDU_ID + 'DU1')
KDU_ID = "m#id"
KDU_SP1 = "m#start"
KDU_SP2 = "m#end"
KDU_TEXT = "m#text"
KDU_HAS_EMOTICONS = "D#has_emoticons"
KDU_HAS_PLAYER_NAME_EXACT = "D#has_player_name_exact"
KDU_HAS_PLAYER_NAME_FUZZY = "D#has_player_name_fuzzy"
KDU_HAS_FOR_NP = "D#has_FOR_np"
KDU_IS_EMOTICON_ONLY = "D#is_emoticon_only"
KDU_HAS_CORRECTION_STAR = "D#has_correction_star"
KDU_ENDS_WITH_BANG = "D#ends_with_bang"
KDU_ENDS_WITH_QMARK = "D#ends_with_qmark"
KDU_SPEAKER_STARTED_DIA = "D#speaker_started_the_dialogue"
KDU_SPEAKER_ALREADY_TALKED_IN_DIA = "D#speaker_already_spoken_in_dialogue"
KDU_EDU_POSITION_IN_TURN = "C#edu_position_in_turn"
KDU_TURN_FOLLOWS_GAP = "D#turn_follows_gap"
KDU_TURN_POSITION_IN_DIA = "C#position_in_dialogue"
KDU_TURN_POSITION_IN_GAME = "C#position_in_game"
KDU_SPEAKER_TURN1_POSITION_IN_DIA = "C#speakers_first_turn_in_dialogue"
KDU_NUM_TOKENS = "C#num_tokens"
KDU_LEX_ = "D#lex"
KDU_PDTB_ = "D#pdtb"
KDU_WORD_FIRST = "D#word_first"
KDU_WORD_LAST = "D#word_last"
KDU_LEMMA_SUBJECT = "D#lemma_subject"

DU_SPECIFIC_FIELDS =\
    [KDU_ID, KDU_WORD_FIRST,
     KDU_WORD_LAST,
     KDU_HAS_PLAYER_NAME_EXACT,
     KDU_HAS_PLAYER_NAME_FUZZY,
     KDU_HAS_EMOTICONS,
     KDU_IS_EMOTICON_ONLY,
     KDU_SPEAKER_STARTED_DIA,
     KDU_SPEAKER_ALREADY_TALKED_IN_DIA,
     KDU_SPEAKER_TURN1_POSITION_IN_DIA,
     KDU_TURN_FOLLOWS_GAP,
     KDU_TURN_POSITION_IN_DIA,
     KDU_TURN_POSITION_IN_GAME,
     KDU_EDU_POSITION_IN_TURN,
     KDU_HAS_CORRECTION_STAR,
     KDU_ENDS_WITH_BANG,
     KDU_ENDS_WITH_QMARK,
     KDU_NUM_TOKENS,
     KDU_SP1,
     KDU_SP2]


def mk_csv_header_lex(inputs):
    """
    CSV header segment based to lexical lookup
    """
    fields = []
    for lex in inputs.lexicons:
        fields.extend(lex.csv_fields(KDU_LEX_))

    for rel in inputs.pdtb_lex:
        field = '_'.join([KDU_PDTB_, rel])
        fields.append(field)

    return fields



def mk_csv_header(inputs, before):
    "header entry for all features"
    fields = []
    fields.extend(before)
    fields.extend(
        [K_DIALOGUE, K_ANNOTATOR,
         K_NUM_EDUS_BETWEEN,
         K_NUM_SPEAKERS_BETWEEN,
         K_ENDS_WITH_QMARK_PAIRS,
         K_DIALOGUE_ACT_PAIRS,
         K_SAME_TURN])
    # du-specific fields
    du_fields = copy.copy(DU_SPECIFIC_FIELDS)
    du_fields.extend(mk_csv_header_lex(inputs))
    if inputs.experimental:
        du_fields.append(KDU_LEMMA_SUBJECT)
        du_fields.append(KDU_HAS_FOR_NP)
    if inputs.debug:
        du_fields.append(KDU_TEXT)
    for edu in ['DU1', 'DU2']:
        fields.extend(f + '_' + edu for f in du_fields)
    # --
    if inputs.debug:
        fields.append(K_TEXT)
    return fields


def mk_csv_header_single(inputs,
                         before):
    "header entry for all features (single EDU variant)"
    fields = [K_DIALOGUE]
    fields.extend(DU_SPECIFIC_FIELDS)
    fields.extend(mk_csv_header_lex(inputs))
    if inputs.experimental:
        fields.append(KDU_LEMMA_SUBJECT)
        fields.append(KDU_HAS_FOR_NP)
    if inputs.debug:
        fields.append(KDU_TEXT)
    return before + fields


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


def _dump_vector(inputs, vec):
    """
    DEBUGGING ONLY: print a vector in the order it would appear in
    the CSV file, pairing each field with its value
    """

    du_csv_fields_lex = []
    for lex in inputs.lexicons:
        du_csv_fields_lex.extend(lex.csv_fields(KDU_LEX_))
    for rel in inputs.pdtb_lex:
        field = '_'.join([KDU_PDTB_, rel])
        du_csv_fields_lex.append(field)
    header = mk_csv_header(inputs, [])
    for hdr in header:
        print hdr, vec[hdr]


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
# single EDU
# ---------------------------------------------------------------------


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
    vec[KDU_NUM_TOKENS] = len(tokens)
    vec[KDU_SP1] = edu_span.char_start
    vec[KDU_SP2] = edu_span.char_end
    # emoticons
    vec[KDU_IS_EMOTICON_ONLY] = is_just_emoticon(tokens)
    vec[KDU_HAS_EMOTICONS] = bool(emoticons(tokens))
    # other tokens
    vec[KDU_HAS_PLAYER_NAME_EXACT] = has_one_of_words(current.players, tokens)
    vec[KDU_HAS_PLAYER_NAME_FUZZY] = has_one_of_words(current.players, tokens,
                                                      norm=fuzzy.nysiis)
    # first and last word
    vec[KDU_WORD_FIRST] = tune_for_csv(word_first)
    vec[KDU_WORD_LAST] = tune_for_csv(word_last)
    # string features
    edu_span = edu.text_span()
    vec[KDU_ENDS_WITH_BANG] = ends_with_bang(edu_span)
    vec[KDU_ENDS_WITH_QMARK] = ends_with_qmark(edu_span)
    vec[KDU_HAS_CORRECTION_STAR] = has_initial_star(edu_span)

    if inputs.debug:
        vec[KDU_TEXT] = tune_for_csv(doc.text(edu_span))


def _fill_single_edu_lex_features(inputs, current, edu, vec):
    """
    Single-EDU features based on lexical lookup.
    Returns void.
    """
    ctx = current.contexts[edu]
    tokens = ctx.tokens

    # lexical features
    for lex in inputs.lexicons:
        for subkey in lex.entries:
            sublex = lex.entries[subkey]
            markers = lexical_markers(sublex, tokens)
            if lex.classes:
                for subclass in lex.subclasses[subkey]:
                    field = lex.csv_field(KDU_LEX_, subkey, subclass=subclass)
                    vec[field] = subclass in markers
            else:
                field = lex.csv_field(KDU_LEX_, subkey)
                vec[field] = bool(markers)

    # PDTB discoure relation markers
    for rel in inputs.pdtb_lex:
        field = '_'.join([KDU_PDTB_, rel])
        vec[field] = has_pdtb_markers(inputs.pdtb_lex[rel],
                                      tokens)


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

    vec[KDU_EDU_POSITION_IN_TURN] = edu_pos
    vec[KDU_TURN_POSITION_IN_DIA] = turn_pos_wrt_dia
    vec[KDU_TURN_POSITION_IN_GAME] = turn_pos_wrt_game
    vec[KDU_TURN_FOLLOWS_GAP] =\
        tid - 1 in dialogue_tids and tid != min(dialogue_tids)
    vec[KDU_SPEAKER_STARTED_DIA] = speaker_started_dialogue(ctx)
    vec[KDU_SPEAKER_TURN1_POSITION_IN_DIA] = spk_turn1_pos
    vec[KDU_SPEAKER_ALREADY_TALKED_IN_DIA] = spk_turn1_pos < turn_pos_wrt_dia


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
    if inputs.experimental:
        parses = current.parses
        trees = enclosed_trees(edu_span, parses.trees)
        has_for_np = bool(map_topdown(is_for_pp_with_np, None, trees))
        subjects = subject_lemmas(edu_span, parses.deptrees)
        subject = subjects[0] if subjects else None
        vec[KDU_HAS_FOR_NP] = has_for_np
        vec[KDU_LEMMA_SUBJECT] = tune_for_csv(subject)


def single_edu_features(inputs, current, edu):
    """
    Fields specific to one EDU
    """
    vec = {KDU_ID: edu.identifier()}
    _fill_single_edu_txt_features(inputs, current, edu, vec)
    _fill_single_edu_lex_features(inputs, current, edu, vec)
    _fill_single_edu_psr_features(inputs, current, edu, vec)
    _fill_single_edu_chat_features(inputs, current, edu, vec)
    return vec


# ---------------------------------------------------------------------
# EDU pairs
# ---------------------------------------------------------------------


def _fill_edu_pair_edu_features(inputs, current, edu1, edu2, vec):
    """
    Pairwise features that come out of the single-edu features for
    each edu
    """
    edu1_info = single_edu_features(inputs, current, edu1)
    edu2_info = single_edu_features(inputs, current, edu2)
    edu1_qmark = edu1_info[KDU_ENDS_WITH_QMARK]
    edu2_qmark = edu2_info[KDU_ENDS_WITH_QMARK]
    edu1_act = clean_dialogue_act(real_dialogue_act(inputs.corpus, edu1))
    edu2_act = clean_dialogue_act(real_dialogue_act(inputs.corpus, edu2))

    vec[K_ENDS_WITH_QMARK_PAIRS] = '%s_%s' % (edu1_qmark, edu2_qmark)
    vec[K_DIALOGUE_ACT_PAIRS] = '%s_%s' % (edu1_act, edu2_act)

    # edu-specific features
    for k in edu1_info:
        vec[k + '_DU1'] = edu1_info[k]
        vec[k + '_DU2'] = edu2_info[k]


def _fill_edu_pair_gap_features(inputs, current, edu1, edu2, vec):
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

    vec[K_NUM_EDUS_BETWEEN] = len(edus_in_span(doc, big_span)) - 2
    vec[K_NUM_SPEAKERS_BETWEEN] = len(speakers_between)
    vec[K_SAME_TURN] = ctx1.turn == ctx2.turn

    if inputs.debug:
        vec[K_TEXT] = tune_for_csv(doc.text(big_span))


def edu_pair_features(inputs, current, edu1, edu2):
    """
    Subvector for pairwise features between two given discourse units
    """
    ctx1 = current.contexts[edu1]
    dia_span = ctx1.dialogue.text_span()
    vec = {K_DIALOGUE: friendly_dialogue_id(current.key, dia_span),
           K_ANNOTATOR: current.doc.origin.annotator}

    _fill_edu_pair_edu_features(inputs, current, edu1, edu2, vec)
    _fill_edu_pair_gap_features(inputs, current, edu1, edu2, vec)
    return vec


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
        for edu1 in edus:
            for edu2 in itr.dropwhile(lambda x: x.span <= edu1.span, edus):
                vec = edu_pair_features(inputs, current, edu1, edu2)
                ctx1 = current.contexts[edu1]
                ctx2 = current.contexts[edu2]
                if ctx1.dialogue != ctx2.dialogue:
                    continue
                if window >= 0 and vec[K_NUM_EDUS_BETWEEN] > window:
                    break
                rels = attachments(doc.relations, edu1, edu2)
                rels_vec = copy.copy(vec)
                if len(rels) > 1:
                    print >> sys.stderr,\
                        'More than one relation between ', edu1, 'and', edu2
                if rels and not live:
                    rels_vec[K_CLASS] = rels[0].type
                elif not live:
                    rels_vec[K_CLASS] = 'UNRELATED'

                pairs_vec = vec
                if not live:
                    pairs_vec[K_CLASS] = bool(rels)
                yield pairs_vec, rels_vec


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
            vec = single_edu_features(inputs, current, edu)
            act = real_dialogue_act(inputs.corpus, edu)
            dia_span = current.contexts[edu].dialogue.text_span()
            vec[K_DIALOGUE] = friendly_dialogue_id(current.key, dia_span)
            if not live:
                vec[K_CLASS] = clean_dialogue_act(act)
            yield vec


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


def read_common_inputs(args, corpus):
    """
    Read the data that is common to live/corpus mode.
    """
    init_lexicons(args)
    pdtb_lex = read_pdtb_lexicon(args)
    postags = postag.read_tags(corpus, args.corpus)
    if args.experimental:
        parses = corenlp.read_results(corpus, args.corpus)
    else:
        parses = None
    return FeatureInput(corpus, postags,
                        parses, LEXICONS, pdtb_lex,
                        args.ignore_cdus, args.debug, args.experimental)


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
