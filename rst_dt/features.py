"""
Feature extraction library functions for RST_DT corpus
"""

import educe.rst_dt

# ---------------------------------------------------------------------
# csv files
# ---------------------------------------------------------------------

K_CLASS = "c#CLASS"  # the thing we want to learn
K_GROUPING = "m#file"
K_TEXT = "m#text"

# fields for a given EDU (will need to be suffixed, eg. KDU_ID + 'DU1')
KDU_ID = "m#id"
KDU_SP1 = "C#start"
KDU_SP2 = "C#end"
KDU_TEXT = "m#text"

def mk_csv_header_lex(inputs):
    return []


def mk_csv_header(inputs, before):
    "header entry for all features"
    fields = []
    fields.extend(before)
    fields.extend(
        [K_GROUPING])
    # du-specific fields
    du_fields =\
        [KDU_ID,
         KDU_SP1,
         KDU_SP2]
    du_fields.extend(mk_csv_header_lex(inputs))
    if inputs.debug:
        du_fields.append(KDU_TEXT)
    for edu in ['DU1', 'DU2']:
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
                          ['key', 'doc'])


# ---------------------------------------------------------------------
# EDU pairs
# ---------------------------------------------------------------------


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

    if inputs.debug:
        vec[K_TEXT] = tune_for_csv(doc.text(big_span))


def edu_pair_features(inputs, current, edu1, edu2):
    """
    Subvector for pairwise features between two given discourse units
    """
    ctx1 = current.contexts[edu1]
    dia_span = ctx1.dialogue.text_span()
    vec = {}

    vec[K_GROUPING] = friendly_dialogue_id(current.key, dia_span)

    _fill_edu_pair_edu_features(inputs, current, edu1, edu2, vec)
    _fill_edu_pair_gap_features(inputs, current, edu1, edu2, vec)
    return vec


def extract_pair_features(inputs):
    """
    Return a pair of dictionaries, one for attachments
    and one for relations
    """
    people = get_players(inputs)

    for k in inputs.corpus:

# ---------------------------------------------------------------------
# input readers
# ---------------------------------------------------------------------


def read_common_inputs(args, corpus):
    """
    Read the data that is common to live/corpus mode.
    """
    return FeatureInput(corpus, args.debug)


def read_corpus_inputs(args):
    """
    Read and filter the part of the corpus we want features for
    """
    is_interesting = educe.util.mk_is_interesting(args)
    reader = educe.rst_dt.Reader(args.corpus)
    anno_files = reader.filter(reader.files(), is_interesting)
    corpus = reader.slurp(anno_files, verbose=True)
    return read_common_inputs(args, corpus)
