# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)


"""
Scoring and formatting results
"""

from __future__ import print_function
from os import path as fp
import codecs
import glob
import itertools as itr
import shutil
import sys

from attelo.io import (load_model,
                       load_predictions,
                       load_vocab)
from attelo.harness.report import (Slice, full_report)
from attelo.harness.util import (makedirs)
import attelo.score
import attelo.report

from .graph import (mk_graphs)
from .learn import (LEARNERS)
from .local import (DETAILED_EVALUATIONS,
                    EVALUATIONS)
from .path import (attelo_doc_model_paths,
                   attelo_sent_model_paths,
                   decode_output_path,
                   eval_model_path,
                   features_path,
                   model_info_path,
                   report_dir_basename,
                   report_dir_path,
                   vocab_path)
from .util import (md5sum_file)


def _fold_report_slices(lconf, fold):
    """
    Report slices for a given fold
    """
    print('Scoring fold {}...'.format(fold),
          file=sys.stderr)
    dkeys = [econf.key for econf in DETAILED_EVALUATIONS]
    for econf in EVALUATIONS:
        p_path = decode_output_path(lconf, econf, fold)
        enable_details = econf.key in dkeys
        stripped_decoder_key = econf.decoder.key[len(econf.settings.key) + 1:]
        config = (econf.learner.key,
                  stripped_decoder_key,
                  econf.settings.key)
        yield Slice(fold, config,
                    load_predictions(p_path),
                    enable_details)


def _mk_model_summary(lconf, dconf, rconf, fold):
    "generate summary of best model features"
    _top_n = 3

    def _write_discr(discr, intra):
        "write discriminating features to disk"
        if discr is None:
            print(('No discriminating features for {name} {grain} model'
                   '').format(name=rconf.key,
                              grain='sent' if intra else 'doc'),
                  file=sys.stderr)
            return
        output = model_info_path(lconf, rconf, fold, intra)
        with codecs.open(output, 'wb', 'utf-8') as fout:
            print(attelo.report.show_discriminating_features(discr),
                  file=fout)

    dpack0 = dconf.pack.values()[0]
    labels = dpack0.labels
    vocab = load_vocab(vocab_path(lconf))
    # doc level discriminating features
    if True:
        models = attelo_doc_model_paths(lconf, rconf, fold).fmap(load_model)
        discr = attelo.score.discriminating_features(models, labels, vocab,
                                                     _top_n)
        _write_discr(discr, False)

    # sentence-level
    spaths = attelo_sent_model_paths(lconf, rconf, fold)
    if fp.exists(spaths.attach) and fp.exists(spaths.relate):
        models = spaths.fmap(load_model)
        discr = attelo.score.discriminating_features(models, labels, vocab,
                                                     _top_n)
        _write_discr(discr, True)


def _mk_hashfile(lconf, dconf):
    "Hash the features and models files for long term archiving"

    hash_me = [features_path(lconf)]
    for fold in sorted(frozenset(dconf.folds.values())):
        for rconf in LEARNERS:
            models_path = eval_model_path(lconf, rconf, fold, '*')
            hash_me.extend(sorted(glob.glob(models_path + '*')))
    provenance_dir = fp.join(report_dir_path(lconf, None),
                             'provenance')
    makedirs(provenance_dir)
    with open(fp.join(provenance_dir, 'hashes.txt'), 'w') as stream:
        for path in hash_me:
            fold_basename = fp.basename(fp.dirname(path))
            if fold_basename.startswith('fold-'):
                nice_path = fp.join(fold_basename, fp.basename(path))
            else:
                nice_path = fp.basename(path)
            print('\t'.join([nice_path, md5sum_file(path)]),
                  file=stream)


def _copy_version_files(lconf):
    "Hash the features and models files for long term archiving"
    provenance_dir = fp.join(report_dir_path(lconf, None),
                             'provenance')
    makedirs(provenance_dir)
    for vpath in glob.glob(fp.join(lconf.eval_dir,
                                   'versions-*.txt')):
        shutil.copy(vpath, provenance_dir)


def _mk_report(lconf, dconf, slices, fold):
    """helper for report generation

    :type fold: int or None
    """
    rpack = full_report(dconf.pack, dconf.folds, slices)
    rpack.dump(report_dir_path(lconf, fold))
    for rconf in LEARNERS:
        if rconf.attach.payload == 'oracle':
            pass
        elif rconf.relate is not None and rconf.relate.payload == 'oracle':
            pass
        else:
            _mk_model_summary(lconf, dconf, rconf, fold)


def mk_fold_report(lconf, dconf, fold):
    "Generate reports for the given fold"
    slices = _fold_report_slices(lconf, fold)
    _mk_report(lconf, dconf, slices, fold)


def mk_global_report(lconf, dconf):
    "Generate reports for all folds"
    slices = itr.chain.from_iterable(_fold_report_slices(lconf, f)
                                     for f in frozenset(dconf.folds.values()))
    _mk_report(lconf, dconf, slices, None)
    _copy_version_files(lconf)

    report_dir = report_dir_path(lconf, None)
    final_report_dir = fp.join(lconf.eval_dir,
                               report_dir_basename(lconf))
    mk_graphs(lconf, dconf)
    _mk_hashfile(lconf, dconf)
    if fp.exists(final_report_dir):
        shutil.rmtree(final_report_dir)
    shutil.copytree(report_dir, final_report_dir)
    # this can happen if resuming a report; better copy
    # it again
    print('Report saved in ', final_report_dir,
          file=sys.stderr)
