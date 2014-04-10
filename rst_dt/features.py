"""
Feature extraction library functions for RST_DT corpus
"""

from collections import namedtuple
import copy
import itertools
import os
import re

from educe.rst_dt import SimpleRSTTree, deptree, id_to_path

from stac.features import tune_for_csv, treenode

# ---------------------------------------------------------------------
# csv files
# ---------------------------------------------------------------------

K_CLASS = "c#CLASS"  # the thing we want to learn
K_GROUPING = "m#file"
K_TEXT = "m#text"
K_NUM_EDUS_BETWEEN = "C#num_edus_between"

# fields for a given EDU (will need to be suffixed, eg. KDU_ID + 'DU1')
KDU_ID = "m#id"
KDU_NUM_TOKENS = "C#num_tokens"
KDU_SP1 = "C#start"
KDU_SP2 = "C#end"
KDU_TEXT = "m#text"
KDU_WORD_FIRST = "D#word_first"
KDU_WORD_LAST = "D#word_last"


def mk_csv_header_lex(_):
    "header entry for lexical features"
    return []


def mk_csv_header(inputs, before):
    "header entry for all features"
    fields = []
    fields.extend(before)
    fields.extend(
        [K_GROUPING,
         K_NUM_EDUS_BETWEEN])
    # du-specific fields
    du_fields =\
        [KDU_ID,
         KDU_SP1,
         KDU_SP2,
         KDU_NUM_TOKENS,
         KDU_WORD_FIRST,
         KDU_WORD_LAST]
    du_fields.extend(mk_csv_header_lex(inputs))
    if inputs.debug:
        du_fields.append(KDU_TEXT)
    for edu in ['EDU1', 'EDU2']:
        fields.extend(f + '_' + edu for f in du_fields)
    # --
    if inputs.debug:
        fields.append(K_TEXT)
    return fields


# ---------------------------------------------------------------------
# feature extraction
# ---------------------------------------------------------------------

# The comments on these named tuples can be docstrings in Python3,
# or we can wrap the class, but eh...

# Global resources and settings used to extract feature vectors
FeatureInput = namedtuple('FeatureInput',
                          ['corpus', 'debug'])

# A document and relevant contextual information
DocumentPlus = namedtuple('DocumentPlus',
                          ['key', 'rsttree', 'deptree'])


# ---------------------------------------------------------------------
# single EDUs
# ---------------------------------------------------------------------


def clean_corpus_word(word):
    """
    Given a word from the corpus, return a slightly normalised
    version of that word
    """
    return word.lower()


def _fill_single_edu_txt_features(inputs, current, edu, vec):
    """
    Textual features specific to one EDU.
    See related `_fill_single_edu_lex_features`.
    Note that this fills the input `vec` dictionary and
    returns void
    """
    clean_text = edu.text
    clean_text = re.sub(r'(\.|<P>|,)*$', r'', clean_text)
    clean_text = re.sub(r'^"', r'', clean_text)

    # basic string features
    vec[KDU_NUM_TOKENS] = len(edu.text)
    vec[KDU_SP1] = edu.span.char_start
    vec[KDU_SP2] = edu.span.char_end

    words = clean_text.split()
    if words:
        word_first = clean_corpus_word(words[0])
        word_last = clean_corpus_word(words[-1])
    else:
        word_first = None
        word_last = None

    # first and last word
    vec[KDU_WORD_FIRST] = tune_for_csv(word_first)
    vec[KDU_WORD_LAST] = tune_for_csv(word_last)

    if inputs.debug:
        vec[KDU_TEXT] = tune_for_csv(edu.text)


def single_edu_features(inputs, current, edu):
    """
    Fields specific to one EDU
    """
    vec = {}
    vec[KDU_ID] = edu.identifier()
    _fill_single_edu_txt_features(inputs, current, edu, vec)
    return vec


# ---------------------------------------------------------------------
# EDU pairs
# ---------------------------------------------------------------------


def _fill_edu_pair_gap_features(inputs,
                                current,
                                edu1,
                                edu2,
                                vec):
    """
    Pairwise features that are related to the gap between two EDUs
    """
    vec[K_NUM_EDUS_BETWEEN] = abs(edu2.num - edu1.num) - 1


def edu_pair_features(inputs, current, edu1, edu2):
    """
    Subvector for pairwise features between two given discourse units
    """
    vec = {}

    vec[K_GROUPING] = os.path.basename(id_to_path(current.key))

    _fill_edu_pair_gap_features(inputs, current, edu1, edu2, vec)
    return vec


def simplify_deptree(dtree):
    """
    Boil a dependency tree down into a dictionary from edu to [edu]
    and a dictionary from (edu, edu) to rel
    """
    links = {}
    relations = {}
    for subtree in dtree:
        src = treenode(subtree).edu
        tgts = [treenode(child).edu for child in subtree]
        links[src] = tgts
        for child in subtree:
            cnode = treenode(child)
            relations[(src, cnode.edu)] = cnode.rel
    return links, relations


def extract_pair_features(inputs, live=False):
    """
    Return a pair of dictionaries, one for attachments
    and one for relations
    """
    for k in inputs.corpus:
        current = preprocess(inputs, k)
        edus = current.rsttree.leaves()
        # reduced dependency graph as dictionary (edu to [edu])
        links, relations =\
            simplify_deptree(current.deptree) if not live else {}

        # single edu features
        edu_feats = {}
        for edu in edus:
            edu_feats[edu] = single_edu_features(inputs, current, edu)

        for edu1, edu2 in itertools.product(edus, edus):
            if edu1 == edu2:
                continue
            vec = edu_pair_features(inputs, current, edu1, edu2)

            # edu-specific features
            edu1_info = edu_feats[edu1]
            edu2_info = edu_feats[edu2]
            for k in edu1_info:
                vec[k + '_EDU1'] = edu1_info[k]
                vec[k + '_EDU2'] = edu2_info[k]

            pairs_vec = vec
            rels_vec = copy.copy(vec)

            if not live:
                pairs_vec[K_CLASS] = edu1 in links and edu2 in links[edu1]
                if pairs_vec[K_CLASS]:
                    rels_vec[K_CLASS] = relations[edu1, edu2]
                else:
                    rels_vec[K_CLASS] = 'UNRELATED'

            yield pairs_vec, rels_vec


def preprocess(inputs, k):
    """
    Pre-process and bundle up a representation of the current document
    """
    rtree = SimpleRSTTree.from_rst_tree(inputs.corpus[k])
    dtree = deptree.relaxed_nuclearity_to_deptree(rtree)
    return DocumentPlus(k, rtree, dtree)

# ---------------------------------------------------------------------
# input readers
# ---------------------------------------------------------------------


def read_common_inputs(args, corpus):
    """
    Read the data that is common to live/corpus mode.
    """
    return FeatureInput(corpus, args.debug)
