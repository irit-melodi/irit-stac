'''
Reading back the CONLL outputs from attelo
'''

from __future__ import print_function
from collections import namedtuple
import copy
import csv

from educe.stac.learning import features
import educe.corpus
import educe.learning.keys
import educe.glozz
import educe.stac
import educe.util


class Background(namedtuple('Background',
                            'contexts dialogues resources')):
    '''
    contextual information needed to translate an edu;
    resources can be set to `{}`
    '''
    pass


class LightEdu(namedtuple('LightEdu',
                          'anno doc context parents resources')):
    '''
    Lightweight representation of an EDU as we would see in
    the attelo output
    '''


def read_conll(instream):
    """
    Iterator for an attelo conll file
    """
    return csv.reader(instream, dialect=csv.excel_tab)


def _unannotated_key(key):
    """
    Given a corpus key, return a copy of that equivalent key
    in the unannotated portion of the corpus (the parser
    outputs objects that are based in unannotated)
    """
    ukey = copy.copy(key)
    ukey.stage = 'unannotated'
    ukey.annotator = None
    return ukey


def dialogue_map(corpus):
    """
    Return a dictionary mapping 'friendly' dialogue ids that we would
    have given to attelo (via feature extraction) to the actual
    documents
    """
    dialogues = {}
    for key in corpus:
        doc = corpus[key]
        ukey = _unannotated_key(key)
        for anno in doc.units:
            if not educe.stac.is_dialogue(anno):
                continue
            anno_id = features.friendly_dialogue_id(ukey, anno.text_span())
            dialogues[anno_id] = (doc, anno.identifier())
    return dialogues


def _get_anno(doc, anno_id):
    """
    Return the annotation object associated with the given
    global annotation ID
    """
    ukey = _unannotated_key(doc.origin)
    matches = [x for x in doc.units
               if ukey.mk_global_id(x.local_id()) == anno_id]
    if len(matches) > 1 is None:
        raise Exception('More than one annotation has global id [%s]'
                        % anno_id)
    elif not matches:
        raise Exception('Found no annotations with global id [%s]'
                        % anno_id)
    else:
        return matches[0]


def extract_edu(background, row):
    """
    Given a row of CONLL output from attelo, return an EDU
    and a list of [(String, EDU)] objects representing links
    from parents
    """
    [global_id, group_id] = row[:2]
    doc, _ = background.dialogues[group_id]
    anno = _get_anno(doc, global_id)
    anno_units_global_id = anno.identifier()
    resources = background.resources.get(anno_units_global_id)
    links = []
    for i in range(4, len(row), 2):
        parent_id = row[i]
        if parent_id not in ['', '0']:
            parent = _get_anno(doc, parent_id)
            drel = row[i + 1]
            links.append((parent, drel))
    context = background.contexts[anno]
    return LightEdu(anno, doc, context, links, resources)
