# pylint: disable=R0904, C0103
"""
Feature extraction library functions for STAC corpora.
The feature extraction script (rel-info) is a lightweight frontend
to this library
"""

from __future__ import absolute_import, print_function
from collections import defaultdict, namedtuple
from itertools import chain
import collections
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
from nltk.corpus import verbnet as vnet

import stac.csv
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
            Lexicon('ref', 'stac_referential.txt', False)]

PDTB_MARKERS_BASENAME = 'pdtb_markers.txt'

VerbNetEntry = namedtuple("VerbNetEntry", "classname lemmas")

VERBNET_CLASSES = ['steal-10.5',
                   'get-13.5.1',
                   'give-13.1-1',
                   'want-32.1-1-1',
                   'want-32.1',
                   'exchange-13.6-1']

INQUIRER_BASENAME = 'inqtabs.txt'

INQUIRER_CLASSES = ['Positiv',
                    'Negativ',
                    'Pstv',
                    'Ngtv',
                    'NegAff',
                    'PosAff',
                    'If',
                    'TrnGain',  # maybe gain/loss words related
                    'TrnLoss',  # ...transactions
                    'TrnLw',
                    'Food',    # related to Catan resources?
                    'Tool',    # related to Catan resources?
                    'Region',  # related to Catan game?
                    'Route']   # related to Catan game

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


def enclosed_lemmas(span, parses):
    """
    Given a span and a list of parses, return any lemmas that
    are within that span
    """
    return [x.features["lemma"] for x in enclosed(span, parses.tokens)]


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
                           'verbnet_entries',
                           'inquirer_lex',
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


class LexKeyGroup(KeyGroup):
    """
    The idea here is to provide a feature per lexical class in the
    lexicon entry
    """
    def __init__(self, lexicon):
        self.lexicon = lexicon
        description = "%s (lexical features)" % self.key_prefix()
        super(LexKeyGroup, self).__init__(description,
                                          self.mk_fields())

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

    def fill(self, current, edu, target=None):
        """
        See `SingleEduSubgroup`
        """
        vec = self if target is None else target
        ctx = current.contexts[edu]
        tokens = ctx.tokens
        lex = self.lexicon
        for subkey in lex.entries:
            sublex = lex.entries[subkey]
            markers = lexical_markers(sublex, tokens)
            if lex.classes:
                for subclass in lex.subclasses[subkey]:
                    field = self.mk_field(subkey, subclass)
                    vec[field.name] = subclass in markers
            else:
                field = self.mk_field(subkey)
                vec[field.name] = bool(markers)


class PdtbLexKeyGroup(KeyGroup):
    """
    One feature per PDTB marker lexicon class
    """
    def __init__(self, lexicon):
        self.lexicon = lexicon
        description = "PDTB features"
        super(PdtbLexKeyGroup, self).__init__(description,
                                              self.mk_fields())

    def mk_field(self, rel):
        "From relation name to feature key"
        name = '_'.join([self.key_prefix(), rel])
        return Key.discrete(name, "pdtb " + rel)

    def mk_fields(self):
        "Feature name for each relation in the lexicon"
        return [self.mk_field(x) for x in self.lexicon]

    @classmethod
    def key_prefix(cls):
        "All feature keys in this lexicon should start with this string"
        return "pdtb"

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

    def fill(self, current, edu, target=None):
        "See `SingleEduSubgroup`"
        vec = self if target is None else target
        ctx = current.contexts[edu]
        tokens = ctx.tokens
        for rel in self.lexicon:
            field = self.mk_field(rel)
            has_marker = has_pdtb_markers(self.lexicon[rel], tokens)
            vec[field.name] = has_marker


class VerbNetLexKeyGroup(KeyGroup):
    """
    One feature per VerbNet lexicon class
    """
    def __init__(self, ventries):
        self.ventries = ventries
        description = "VerbNet features"
        super(VerbNetLexKeyGroup, self).__init__(description,
                                                 self.mk_fields())

    def mk_field(self, ventry):
        "From verb class to feature key"
        name = '_'.join([self.key_prefix(), ventry.classname])
        return Key.discrete(name, "VerbNet " + ventry.classname)

    def mk_fields(self):
        "Feature name for each relation in the lexicon"
        return [self.mk_field(x) for x in self.ventries]

    @classmethod
    def key_prefix(cls):
        "All feature keys in this lexicon should start with this string"
        return "verbnet"

    def help_text(self):
        """
        CSV field names for each entry/class in the lexicon
        """
        header_name = (self.key_prefix() + "_...").ljust(KeyGroup.NAME_WIDTH)
        header_help = "if has lemma in the given class"
        header = "[D] %s %s" % (header_name, header_help)
        lines = [header]
        for ventry in self.ventries:
            lines.append("       %s" %
                         ventry.classname.ljust(KeyGroup.NAME_WIDTH))
        return "\n".join(lines)

    def fill(self, current, edu, target=None):
        "See `SingleEduSubgroup`"

        vec = self if target is None else target
        lemmas = frozenset(enclosed_lemmas(edu.text_span(), current.parses))
        for ventry in self.ventries:
            matching = lemmas.intersection(ventry.lemmas)
            field = self.mk_field(ventry)
            vec[field.name] = bool(matching)


class InquirerLexKeyGroup(KeyGroup):
    """
    One feature per Inquirer lexicon class
    """
    def __init__(self, lexicon):
        self.lexicon = lexicon
        description = "Inquirer features"
        super(InquirerLexKeyGroup, self).__init__(description,
                                                  self.mk_fields())

    def mk_field(self, entry):
        "From verb class to feature key"
        name = '_'.join([self.key_prefix(), entry])
        return Key.discrete(name, "Inquirer " + entry)

    def mk_fields(self):
        "Feature name for each relation in the lexicon"
        return [self.mk_field(x) for x in self.lexicon]

    @classmethod
    def key_prefix(cls):
        "All feature keys in this lexicon should start with this string"
        return "inq"

    def help_text(self):
        """
        CSV field names for each entry/class in the lexicon
        """
        header_name = (self.key_prefix() + "_...").ljust(KeyGroup.NAME_WIDTH)
        header_help = "if has token in the given class"
        header = "[D] %s %s" % (header_name, header_help)
        lines = [header]
        for entry in self.lexicon:
            lines.append("       %s" %
                         entry.ljust(KeyGroup.NAME_WIDTH))
        return "\n".join(lines)

    def fill(self, current, edu, target=None):
        "See `SingleEduSubgroup`"

        vec = self if target is None else target
        ctx = current.contexts[edu]
        tokens = frozenset(t.word.lower() for t in ctx.tokens)
        for entry in self.lexicon:
            field = self.mk_field(entry)
            matching = tokens.intersection(self.lexicon[entry])
            vec[field.name] = bool(matching)


class MergedLexKeyGroup(MergedKeyGroup):
    """
    Single-EDU features based on lexical lookup.
    """
    def __init__(self, inputs):
        groups =\
            [LexKeyGroup(l) for l in inputs.lexicons] +\
            [PdtbLexKeyGroup(inputs.pdtb_lex),
             InquirerLexKeyGroup(inputs.inquirer_lex),
             VerbNetLexKeyGroup(inputs.verbnet_entries)]
        description = "lexical features"
        super(MergedLexKeyGroup, self).__init__(description, groups)

    def help_text(self):
        lines = [self.description,
                 "-" * len(self.description)] +\
            [g.help_text() for g in self.groups]
        return "\n".join(lines)

    def fill(self, current, edu, target=None):
        "See `SingleEduSubgroup`"
        for group in self.groups:
            group.fill(current, edu, target)


# ---------------------------------------------------------------------
# single EDU non-lexical features
# ---------------------------------------------------------------------

QUESTION_WORDS = ["what",
                  "which",
                  "where",
                  "when",
                  "who",
                  "how",
                  "why",
                  "whose"]


def is_question(current, edu):
    """
    Is this EDU a question (or does it contain one?)
    """

    def is_sqlike(anno):
        "is some sort of question"
        return isinstance(anno, ConstituencyTree)\
            and anno.node in ['SBARQ', 'SQ']

    doc = current.doc
    span = edu.text_span()
    has_qmark = "?" in doc.text(span)[-1]

    ctx = current.contexts[edu]
    tokens = ctx.tokens
    starts_w_qword = False
    if tokens:
        starts_w_qword = tokens[0].word.lower() in QUESTION_WORDS

    parses = current.parses
    trees = enclosed_trees(span, parses.trees)
    with_q_tag = map_topdown(is_sqlike, None, trees)
    has_q_tag = bool(with_q_tag)
    return has_qmark or starts_w_qword or has_q_tag


class SingleEduSubgroup(KeyGroup):
    """
    Abstract keygroup for subgroups of the merged SingleEduKeys.
    We use these subgroup classes to help provide modularity, to
    capture the idea that the bits of code that define a set of
    related feature vector keys should go with the bits of code
    that also fill them out
    """
    def __init__(self, description, keys):
        super(SingleEduSubgroup, self).__init__(description, keys)

    def fill(self, current, edu, target=None):
        """
        Fill out a vector's features (if the vector is None, then we
        just fill out this group; but in the case of a merged key
        group, you may find it desirable to fill out the merged
        group instead)
        """
        raise NotImplementedError("fill should be implemented by a subclass")


class SingleEduSubgroup_Meta(SingleEduSubgroup):
    """
    Basic EDU-identification features
    """
    def __init__(self):
        desc = self.__doc__.strip()
        keys =\
            [Key.meta("id",
                      "some sort of unique identifier for the EDU"),
             Key.meta("start", "text span start"),
             Key.meta("end", "text span end")]
        super(SingleEduSubgroup_Meta, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        vec = self if target is None else target
        edu_span = edu.text_span()
        vec["id"] = edu.identifier()
        vec["start"] = edu_span.char_start
        vec["end"] = edu_span.char_end


class SingleEduSubgroup_Debug(SingleEduSubgroup):
    """
    debug features
    """
    def __init__(self):
        desc = self.__doc__.strip()
        keys = [Key.meta("text", "EDU text [debug only]")]
        super(SingleEduSubgroup_Debug, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        vec = self if target is None else target
        doc = current.doc
        edu_span = edu.text_span()
        vec["text"] = tune_for_csv(doc.text(edu_span))


class SingleEduSubgroup_Token(SingleEduSubgroup):
    """
    word/token-based features
    """
    def __init__(self):
        desc = self.__doc__.strip()
        keys =\
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
                          "if the EDU consists solely of an emoticon")]
        super(SingleEduSubgroup_Token, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        vec = self if target is None else target
        ctx = current.contexts[edu]
        tokens = ctx.tokens

        # first and last words
        if tokens:
            word_first = clean_chat_word(tokens[0])
            word_last = clean_chat_word(tokens[-1])
        else:
            word_first = None
            word_last = None

        # basic string features
        vec["num_tokens"] = len(tokens)
        # emoticons
        vec["is_emoticon_only"] = is_just_emoticon(tokens)
        vec["has_emoticons"] = bool(emoticons(tokens))
        # other tokens
        vec["has_player_name_exact"] =\
            has_one_of_words(current.players, tokens)
        vec["has_player_name_fuzzy"] =\
            has_one_of_words(current.players, tokens,
                             norm=fuzzy.nysiis)
        # first and last word
        vec["word_first"] = tune_for_csv(word_first)
        vec["word_last"] = tune_for_csv(word_last)


class SingleEduSubgroup_Punct(SingleEduSubgroup):
    "punctuation features"

    def __init__(self):
        desc = self.__doc__.strip()
        keys =\
            [Key.discrete("has_correction_star",
                          "if the EDU begins with a '*' but does "
                          "not contain others"),
             Key.discrete("ends_with_bang", "if the EDU text ends with '!'"),
             Key.discrete("ends_with_qmark", "if the EDU text ends with '?'")]
        super(SingleEduSubgroup_Punct, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        doc = current.doc

        def has_initial_star(span):
            "Text in span has an initial star but no other"
            txt = doc.text(span)
            return txt[0] == "*" and "*" not in txt[1:]

        def ends_with_bang(span):
            "Text in span ends with an exclamation"
            return doc.text(span)[-1] == '!'

        def ends_with_qmark(span):
            """
            Text in span ends with question mark. We might need better
            detection using eg subject-verb inversion from a parser
            """
            return doc.text(span)[-1] == '?'

        vec = self if target is None else target
        edu_span = edu.text_span()
        vec["ends_with_bang"] = ends_with_bang(edu_span)
        vec["ends_with_qmark"] = ends_with_qmark(edu_span)
        vec["has_correction_star"] = has_initial_star(edu_span)


class SingleEduSubgroup_Chat(SingleEduSubgroup):
    """
    Single-EDU features based on the EDU's relationship with the
    the chat structure (eg turns, dialogues).
    """

    def __init__(self):
        desc = "chat history features"
        keys =\
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
                            "relative position of the EDU in the turn")]
        super(SingleEduSubgroup_Chat, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        vec = self if target is None else target
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


class SingleEduSubgroup_Parser(SingleEduSubgroup):
    """
    Single-EDU features that come out of a syntactic parser.
    """

    def __init__(self):
        desc = "parser features"
        keys =\
            [Key.discrete("lemma_subject",
                          "the lemma corresponding to the "
                          "subject of this EDU"),
             Key.discrete("has_FOR_np",
                          "if the EDU has the pattern IN(for).. NP"),
             Key.discrete("is_question",
                          "if the EDU is (or contains) a question")]
        super(SingleEduSubgroup_Parser, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        vec = self if target is None else target

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

        vec = self if target is None else target
        edu_span = edu.text_span()
        parses = current.parses
        trees = enclosed_trees(edu_span, parses.trees)
        subjects = subject_lemmas(edu_span, parses.deptrees)
        subject = subjects[0] if subjects else None
        vec["has_FOR_np"] = bool(map_topdown(is_for_pp_with_np, None, trees))
        vec["lemma_subject"] = tune_for_csv(subject)
        vec["is_question"] = is_question(current, edu)


class SingleEduKeys(MergedKeyGroup):
    """
    Features for a single EDU
    """
    def __init__(self, inputs):
        groups = [SingleEduSubgroup_Meta(),
                  SingleEduSubgroup_Token(),
                  SingleEduSubgroup_Chat(),
                  SingleEduSubgroup_Punct(),
                  SingleEduSubgroup_Parser(),
                  MergedLexKeyGroup(inputs)]
        if inputs.debug:
            groups.append(SingleEduSubgroup_Debug())
        super(SingleEduKeys, self).__init__("single EDU features",
                                            groups)

    def fill(self, current, edu, target=None):
        """
        See `SingleEduSubgroup.fill`
        """
        vec = self if target is None else target
        for group in self.groups:
            group.fill(current, edu, vec)

# ---------------------------------------------------------------------
# EDU singletons (standalone mode)
# ---------------------------------------------------------------------


class SingleEduSubgroup_Standalone(SingleEduSubgroup):
    """
    additional keys for single EDU in standalone mode
    """
    def __init__(self):
        desc = self.__doc__.strip()
        keys = [Key.meta("dialogue", "dialogue that contains both EDUs")]
        super(SingleEduSubgroup_Standalone, self).__init__(desc, keys)

    def fill(self, current, edu, target=None):
        vec = self if target is None else target
        dia_span = current.contexts[edu].dialogue.text_span()
        vec["dialogue"] = friendly_dialogue_id(current.key, dia_span)


class SingleEduKeysForSingleExtraction(MergedKeyGroup):
    """
    Features for a single EDU, not used within EDU pair extraction,
    but just in standalone mode for dialogue act annotations
    """
    def __init__(self, inputs):
        groups = [SingleEduSubgroup_Standalone(),
                  SingleEduKeys(inputs)]
        super(SingleEduKeysForSingleExtraction,
              self).__init__("standalone single EDUs", groups)

    def fill(self, current, edu, target=None):
        "See `SingleEduSubgroup`"

        vec = self if target is None else target
        for group in self.groups:
            group.fill(current, edu, vec)


# ---------------------------------------------------------------------
# EDU pairs
# ---------------------------------------------------------------------

class PairSubgroup(KeyGroup):
    """
    Abstract keygroup for subgroups of the merged PairKeys.
    We use these subgroup classes to help provide modularity, to
    capture the idea that the bits of code that define a set of
    related feature vector keys should go with the bits of code
    that also fill them out
    """
    def __init__(self, description, keys):
        super(PairSubgroup, self).__init__(description, keys)

    def fill(self, current, edu1, edu2, target=None):
        """
        Fill out a vector's features (if the vector is None, then we
        just fill out this group; but in the case of a merged key
        group, you may find it desirable to fill out the merged
        group instead)
        """
        raise NotImplementedError("fill should be implemented by a subclass")


class PairSubgroup_Tuple(PairSubgroup):
    "artificial tuple features"

    def __init__(self, inputs, sf_cache):
        self.corpus = inputs.corpus
        self.sf_cache = sf_cache
        desc = self.__doc__.strip()
        keys =\
            [Key.discrete("is_question_pairs",
                          "boolean tuple: if each EDU is a question"),
             Key.discrete("dialogue_act_pairs",
                          "tuple of dialogue acts for both EDUs")]
        super(PairSubgroup_Tuple, self).__init__(desc, keys)

    def fill(self, current, edu1, edu2, target=None):
        vec = self if target is None else target
        vec_edu1 = self.sf_cache[edu1]
        vec_edu2 = self.sf_cache[edu2]
        edu1_q = vec_edu1["is_question"]
        edu2_q = vec_edu2["is_question"]
        edu1_act = clean_dialogue_act(real_dialogue_act(self.corpus, edu1))
        edu2_act = clean_dialogue_act(real_dialogue_act(self.corpus, edu2))

        vec["is_question_pairs"] = '%s_%s' % (edu1_q, edu2_q)
        vec["dialogue_act_pairs"] = '%s_%s' % (edu1_act, edu2_act)


class PairSubgroup_Gap(PairSubgroup):
    """
    Features related to the combined surrounding context of the
    two EDUs
    """

    def __init__(self, sf_cache):
        self.sf_cache = sf_cache
        desc = "the gap between EDUs"
        keys =\
            [Key.continuous("num_edus_between",
                            "number of intervening EDUs (0 if adjacent)"),
             Key.continuous("num_speakers_between",
                            "number of distinct speakers in intervening EDUs"),
             Key.discrete("same_speaker",
                          "if both EDUs have the same speaker"),
             Key.discrete("same_turn", "if both EDUs are in the same turn"),
             Key.discrete("has_inner_question",
                          "if there is an intervening EDU that is a question")]
        super(PairSubgroup_Gap, self).__init__(desc, keys)

    def fill(self, current, edu1, edu2, target):
        vec = self if target is None else target
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

        inner_edus = edus_in_span(doc, big_span)
        inner_edus.remove(edu1)
        inner_edus.remove(edu2)

        vec["has_inner_question"] = any(self.sf_cache[x]["is_question"]
                                        for x in inner_edus)
        vec["num_edus_between"] = len(inner_edus)
        vec["num_speakers_between"] = len(speakers_between)
        vec["same_speaker"] = speaker(ctx1.turn) == speaker(ctx2.turn)
        vec["same_turn"] = ctx1.turn == ctx2.turn


class PairSubgroup_Debug(PairSubgroup):
    "debug features"

    def __init__(self):
        desc = self.__doc__.strip()
        keys = [Key.meta("text",
                         "text from DU1 start to DU2 end [debug only]")]
        super(PairSubgroup_Debug, self).__init__(desc, keys)

    def fill(self, current, edu1, edu2, target=None):
        vec = self if target is None else target
        doc = current.doc
        edu1_span = edu1.text_span()
        edu2_span = edu2.text_span()
        big_span = edu1_span.merge(edu2_span)
        vec["text"] = tune_for_csv(doc.text(big_span))


class PairSubGroup_Core(PairSubgroup):
    "core features"

    def __init__(self):
        desc = self.__doc__.strip()
        keys =\
            [Key.meta("dialogue", "dialogue that contains both EDUs"),
             Key.meta("annotator", "annotator for the subdoc")]
        super(PairSubGroup_Core, self).__init__(desc, keys)

    def fill(self, current, edu1, edu2, target=None):
        vec = self if target is None else target
        ctx1 = current.contexts[edu1]
        dia_span = ctx1.dialogue.text_span()

        vec["dialogue"] = friendly_dialogue_id(current.key, dia_span)
        vec["annotator"] = current.doc.origin.annotator


class PairKeys(MergedKeyGroup):
    """
    Features for pairs of EDUs
    """
    def __init__(self, inputs, sf_cache=None):
        self.sf_cache = sf_cache
        groups = [PairSubGroup_Core(),
                  PairSubgroup_Gap(sf_cache),
                  PairSubgroup_Tuple(inputs, sf_cache)]
        if inputs.debug:
            groups.append(PairSubgroup_Debug())

        if sf_cache is None:
            self.edu1 = SingleEduKeys(inputs)
            self.edu2 = SingleEduKeys(inputs)
        else:
            self.edu1 = None  # will be filled out later
            self.edu2 = None  # from the feature cache

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

    def fill(self, current, edu1, edu2, target=None):
        "See `PairSubgroup`"
        vec = self if target is None else target
        vec.edu1 = self.sf_cache[edu1]
        vec.edu2 = self.sf_cache[edu2]
        for group in self.groups:
            group.fill(current, edu1, edu2, vec)

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
            vec.fill(self.current, edu)
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
                vec = PairKeys(inputs, sf_cache=sf_cache)
                vec.fill(current, edu1, edu2)
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
            vec = SingleEduKeysForSingleExtraction(inputs)
            vec.fill(current, edu)
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


def _read_inquirer_lexicon(args):
    """
    Read and return the local PDTB discourse marker lexicon.
    """
    inq_txt_file = os.path.join(args.resources, INQUIRER_BASENAME)
    with open(inq_txt_file) as cin:
        creader = stac.csv.SparseDictReader(cin, delimiter='\t')
        words = defaultdict(list)
        for row in creader:
            for k in row:
                word = row["Entry"].lower()
                word = re.sub(r'#.*$', r'', word)
                if k in INQUIRER_CLASSES:
                    words[k].append(word)
    return words


def _read_resources(args, corpus, postags, parses):
    """
    Read all external resources
    """
    for lex in LEXICONS:
        lex.read(args.resources)
    pdtb_lex = read_pdtb_lexicon(args)
    inq_lex = _read_inquirer_lexicon(args)

    verbnet_entries = [VerbNetEntry(x, frozenset(vnet.lemmas(x)))
                       for x in VERBNET_CLASSES]
    return FeatureInput(corpus, postags, parses,
                        LEXICONS, pdtb_lex, verbnet_entries, inq_lex,
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
    parses = corenlp.read_results(corpus, args.corpus)
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
