#!/usr/bin/env python
# pylint: disable=invalid-name
# this is a script, not a module
# pylint: enable=invalid-name

"""
Learn and predict dialogue acts from EDU feature vectors
"""

from os import path as fp
import argparse
import copy
import os

import joblib
from scipy.sparse import lil_matrix
from sklearn.datasets import load_svmlight_file
from attelo.io import (load_labels,
                       load_vocab)

from educe.stac.annotation import set_addressees
from educe.stac.context import Context
from educe.stac.learning.addressee import guess_addressees_for_edu
import educe.stac.learning.features as stac_features
import educe.stac
from educe.stac.util.output import save_document


# ---------------------------------------------------------------------
# learning
# ---------------------------------------------------------------------


def learn_and_save(learner, feature_path, output_path):
    '''
    learn dialogue acts from an svmlight features file and dump
    the model to disk
    '''
    # pylint: disable=unbalanced-tuple-unpacking
    data, target = load_svmlight_file(feature_path)
    # pylint: enable=unbalanced-tuple-unpacking
    output_dir = fp.dirname(output_path)
    model = learner.fit(data, target)
    if not fp.exists(output_dir):
        os.makedirs(output_dir)
    joblib.dump(model, output_path)


# ---------------------------------------------------------------------
# prediction
# ---------------------------------------------------------------------


def _output_key(key):
    """
    Given a `FileId` key for an input document, return a version that
    would be appropriate for its output equivalent
    """
    key2 = copy.copy(key)
    key2.stage = 'units'
    key2.annotator = 'simple-da'
    return key2


def get_edus_plus(inputs):
    """Generate edus and extra environmental information for each

    Currently:

    * environment
    * contexts
    * edu
    """
    for env in stac_features.mk_envs(inputs, 'unannotated'):
        doc = env.current.doc
        contexts = Context.for_edus(doc)
        for unit in doc.units:
            if educe.stac.is_edu(unit):
                yield env, contexts, unit


def extract_features(vocab, edus_plus):
    """
    Return a sparse matrix of features for all edus in the corpus
    """
    matrix = lil_matrix((len(edus_plus), len(vocab)))
    # this unfortunately duplicates stac_features.extract_single_features
    # but it's the price we pay to ensure we get the edus and vectors in
    # the same order
    for row, (env, _, edu) in enumerate(edus_plus):
        vec = stac_features.SingleEduKeys(env.inputs)
        vec.fill(env.current, edu)
        for feat, val in vec.one_hot_values_gen():
            if feat in vocab:
                matrix[row, vocab[feat]] = val
    return matrix.tocsr()


def annotate_edus(model, vocab, labels, inputs):
    """
    Annotate each EDU with its dialogue act and addressee
    """
    edus_plus = list(get_edus_plus(inputs))
    feats = extract_features(vocab, edus_plus)
    predictions = model.predict(feats)
    for (env, contexts, edu), da_num in zip(edus_plus, predictions):
        da_label = labels[int(da_num) - 1]
        addressees = guess_addressees_for_edu(contexts,
                                              env.current.players,
                                              edu)
        set_addressees(edu, addressees)
        edu.type = da_label


def command_annotate(args):
    """
    Top-level command: given a dialogue act model, and a corpus with some
    Glozz documents, perform dialogue act annotation on them, and simple
    addressee detection, and dump Glozz documents in the output directory
    """
    args.ignore_cdus = False
    args.parsing = True
    args.single = True
    inputs = stac_features.read_corpus_inputs(args)
    model = joblib.load(args.model)
    vocab = {f: i for i, f in
             enumerate(load_vocab(args.vocabulary))}
    labels = load_labels(args.labels)

    # add dialogue acts and addressees
    annotate_edus(model, vocab, labels, inputs)

    # corpus has been modified in-memory, now save to disk
    for key in inputs.corpus:
        key2 = _output_key(key)
        doc = inputs.corpus[key]
        save_document(args.output, key2, doc)


def main():
    "channel to subcommands"

    psr = argparse.ArgumentParser(add_help=False)
    psr.add_argument("corpus", default=None, metavar="DIR",
                     help="corpus to annotate (live mode assumed)")
    psr.add_argument('resources', metavar='DIR',
                     help='Resource dir (eg. data/resources/lexicon)')
    psr.add_argument("--model", default=None, required=True,
                     help="provide saved model for prediction of "
                     "dialogue acts")
    psr.add_argument("--vocabulary", default=None, required=True,
                     help="feature vocabulary")
    psr.add_argument("--labels", default=None, required=True,
                     help="dialogue act labels file (features file)")
    psr.add_argument("--output", "-o", metavar="DIR",
                     default=None,
                     required=True,
                     help="output directory")
    psr.set_defaults(func=command_annotate)

    args = psr.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

# vim:filetype=python:
