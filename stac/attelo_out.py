'''
Reading back the CONLL outputs from attelo
'''

from __future__ import print_function
from collections import namedtuple
import copy
import re

from educe.annotation import RelSpan, Relation
import educe.corpus
import educe.learning.keys
import educe.glozz
import educe.stac
import educe.stac.util.glozz as stac_glozz
import educe.util

# pylint: disable=too-few-public-methods


class Background(namedtuple('Background',
                            'contexts dialogues resources')):
    '''
    contextual information needed to translate an edu;
    resources can be set to `{}`
    '''
    pass


def dialogue_map(corpus):
    """
    Return a dictionary mapping dialogue ids to the document that
    that they would be found in
    """
    dialogues = {}
    for key in corpus:
        doc = corpus[key]
        for anno in doc.units:
            if not educe.stac.is_dialogue(anno):
                continue
            dialogues[anno.identifier()] = doc
    return dialogues


def guess_doc(corpus, doc_subdoc):
    """
    Return the file id and document associated with the given
    global annotation ID
    """
    matches = [(k, v) for k, v in corpus.items() if
               (k.doc, k.subdoc) == doc_subdoc]  # live input; no subdoc
    if not matches:
        raise Exception(('Found no documents with key {}'
                         '').format(doc_subdoc))
    else:
        return matches[0]


# ex: pilot03_2011_10_19_16_30_51_+0100
DOC_TIMESTAMP_PATTERN = r"(?P<doc_id>.*_[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[-+][0-9]{4})_(?P<subdoc_id>[0-9]+)_(?P<loc_id>.*)"
DOC_TIMESTAMP = re.compile(DOC_TIMESTAMP_PATTERN)

def split_id(anno_id):
    """
    Split a global annotation into its global components and its
    local suffix
    """
    # WIP match a widespread format: doc_timestamp_anno
    m = DOC_TIMESTAMP.match(anno_id)
    if m is not None:
        doc = m.group('doc_id')
        subdoc = m.group('subdoc_id')
        suffix = m.group('loc_id')
    else:
        doc, subdoc, suffix = anno_id.split('_', 2)
    return ((doc, subdoc), suffix)


def mk_relation(tstamp, local_id_parent, local_id_child, label):
    """
    Given a document and edu ids, create a relation
    instance betweenthem

    """
    span = RelSpan(local_id_parent,
                   local_id_child)
    label = label
    annotator = 'stacparser'
    date = tstamp.next()
    rel_id = stac_glozz.anno_id_from_tuple((annotator, date))
    features = {}
    metadata = {}
    metadata['author'] = annotator
    metadata['creation-date'] = str(date)
    return Relation(rel_id=rel_id,
                    span=span,
                    rtype=label,
                    features=features,
                    metadata=metadata)


def copy_discourse_corpus(corpus, annotator):
    """
    Return a fairly shallow copy of a presumably unannotated corpus,
    where every key is converted to a discourse stage key and every
    document is a shallow copy of the original.

    It should be safe to add things to the corpus, but modifying
    pre-existing EDUs (for example) would be destructive on the
    other side
    """
    corpus2 = {}
    for key, doc in corpus.items():
        key2 = copy.copy(key)
        key2.stage = 'discourse'
        key2.annotator = annotator
        corpus2[key2] = copy.copy(doc)
    return corpus2


def add_predictions(tstamp, corpus, predictions):
    """
    Augment a corpus with attelo predictions (parent global id,
    child global id, label) triples

    Predictions will be added to a fresh corpus with each
    document being marked as being in the discourse dir by
    by the given author

    Note that this mutates the corpus

    :type predictions: [(string, string, string)]
    """
    # build dictionary from FileId to relations in that document
    for id_parent, id_child, label in predictions:
        if id_parent == 'ROOT':
            continue
        doc_subdoc1, local_id_parent = split_id(id_parent)
        doc_subdoc2, local_id_child = split_id(id_child)
        assert doc_subdoc1 == doc_subdoc2
        _, doc = guess_doc(corpus, doc_subdoc1)
        if label != 'UNRELATED':
            doc.relations.append(mk_relation(tstamp,
                                             local_id_parent,
                                             local_id_child,
                                             label))


def remove_unseen_edus(corpus, predictions):
    """
    The notion of unseen EDUs is a fairly visual one. The problem is
    that folds are allocated randomly over dialogues, so any EDUs
    may be confused for EDUs which are marked as unrelated. We need
    to set these aside somehow (for example hiding them outright) so
    they don't confuse analysis

    Note that this mutates the corpus
    """
    unseen = {}
    # build dictionary from FileId to relations in that document
    for id_parent, id_child, _ in predictions:
        doc_subdoc2, local_id_child = split_id(id_child)
        if id_parent != 'ROOT':
            doc_subdoc1, local_id_parent = split_id(id_parent)
            assert doc_subdoc1 == doc_subdoc2
        key, doc = guess_doc(corpus, doc_subdoc2)
        if key not in unseen:
            unseen[key] = set(x.local_id() for x in doc.units
                              if educe.stac.is_edu(x))
        if id_parent != 'ROOT':
            unseen[key].discard(local_id_parent)
        unseen[key].discard(local_id_child)

    for key, doc in corpus.items():
        if key not in unseen:
            continue
        edus = [x for x in doc.units if educe.stac.is_edu(x)]
        for edu in edus:
            if edu.local_id() in unseen[key]:
                doc.units.remove(edu)
