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
                       load_predictions)
from attelo.harness.report import (Slice, full_report)
from attelo.harness.util import (makedirs)
from attelo.table import (select_fakeroot,
                          select_intersentential,
                          select_intrasentential)
import attelo.score
import attelo.report

from .graph import (mk_graphs, mk_test_graphs)
from .learn import (LEARNERS)
from .local import (DETAILED_EVALUATIONS,
                    EVALUATIONS)
from .path import (attelo_doc_model_paths,
                   attelo_sent_model_paths,
                   decode_output_path,
                   eval_model_path,
                   mpack_paths,
                   model_info_path,
                   report_dir_basename,
                   report_dir_path)
from .util import (md5sum_file,
                   test_evaluation)



def _report_key(econf):
    """
    Rework an evaluation config key so it looks nice in
    our reports

    :rtype tuple(string)
    """
    return (econf.learner.key,
            econf.decoder.key[len(econf.settings.key) + 1:],
            econf.settings.key)


def _fold_report_slices(lconf, fold):
    """
    Report slices for a given fold
    """
    print('Scoring fold {}...'.format(fold),
          file=sys.stderr)
    dkeys = [econf.key for econf in DETAILED_EVALUATIONS]
    for econf in EVALUATIONS:
        p_path = decode_output_path(lconf, econf, fold)
        yield Slice(fold=fold,
                    configuration=_report_key(econf),
                    predictions=load_predictions(p_path),
                    enable_details=econf.key in dkeys)


def _mk_model_summary(lconf, dconf, rconf, test_data, fold):
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
        output = model_info_path(lconf, rconf, test_data,
                                 fold=fold,
                                 intra=intra)
        with codecs.open(output, 'wb', 'utf-8') as fout:
            print(attelo.report.show_discriminating_features(discr),
                  file=fout)

    dpack0 = dconf.pack.values()[0]
    labels = dpack0.labels
    vocab = dpack0.vocab
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


def _mk_hashfile(lconf, dconf, test_data):
    "Hash the features and models files for long term archiving"

    hash_me = list(mpack_paths(lconf, False))
    if test_evaluation() is not None:
        hash_me.extend(mpack_paths(lconf, True))
    for rconf in LEARNERS:
        models_path = eval_model_path(lconf, rconf, None, '*')
        hash_me.extend(sorted(glob.glob(models_path + '*')))
    if not test_data:
        for fold in sorted(frozenset(dconf.folds.values())):
            for rconf in LEARNERS:
                models_path = eval_model_path(lconf, rconf, fold, '*')
                hash_me.extend(sorted(glob.glob(models_path + '*')))
    provenance_dir = fp.join(report_dir_path(lconf, test_data, None),
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


def _copy_version_files(lconf, test_data):
    "Hash the features and models files for long term archiving"
    provenance_dir = fp.join(report_dir_path(lconf, test_data, None),
                             'provenance')
    makedirs(provenance_dir)
    for vpath in glob.glob(fp.join(lconf.eval_dir,
                                   'versions-*.txt')):
        shutil.copy(vpath, provenance_dir)


def _mk_report(lconf, dconf, slices, fold, test_data=False):
    """helper for report generation

    :type fold: int or None
    """
    # we could just use slices = list(slices) here but we have a
    # bit of awkward lazy IO where it says 'scoring fold N...'
    # the idea being that we should only really see this when it's
    # actually scoring that fold. Hoop-jumping induced by the fact
    # that we are now generating multiple reports on the same slices
    slices_ = itr.tee(slices, 4)
    rpack = full_report(dconf.pack, dconf.folds, slices_[0])
    rdir = report_dir_path(lconf, test_data, fold)
    rpack.dump(rdir, header='whole')

    partitions = [(1, 'intra', select_intrasentential),
                  (2, 'inter', select_intersentential),
                  (3, 'froot', select_fakeroot)]
    for i, header, adjust_pack in partitions:
        rpack = full_report(dconf.pack, dconf.folds, slices_[i],
                            adjust_pack=adjust_pack)
        rpack.append(rdir, header=header)

    for rconf in LEARNERS:
        if rconf.attach.payload == 'oracle':
            pass
        elif rconf.relate.payload == 'oracle':
            pass
        else:
            _mk_model_summary(lconf, dconf, rconf, test_data, fold)


def mk_fold_report(lconf, dconf, fold):
    "Generate reports for the given fold"
    slices = _fold_report_slices(lconf, fold)
    _mk_report(lconf, dconf, slices, fold)


def mk_global_report(lconf, dconf):
    "Generate reports for all folds"
    slices = itr.chain.from_iterable(_fold_report_slices(lconf, f)
                                     for f in frozenset(dconf.folds.values()))
    _mk_report(lconf, dconf, slices, None)
    _copy_version_files(lconf, False)

    report_dir = report_dir_path(lconf, False, None)
    final_report_dir = fp.join(lconf.eval_dir,
                               report_dir_basename(lconf, False))
    mk_graphs(lconf, dconf)
    _mk_hashfile(lconf, dconf, False)
    if fp.exists(final_report_dir):
        shutil.rmtree(final_report_dir)
    shutil.copytree(report_dir, final_report_dir)
    # this can happen if resuming a report; better copy
    # it again
    print('Report saved in ', final_report_dir,
          file=sys.stderr)


def mk_test_report(lconf, dconf):
    "Generate reports for test data"
    econf = test_evaluation()
    if econf is None:
        return

    p_path = decode_output_path(lconf, econf, None)
    slices = [Slice(fold=None,
                    configuration=_report_key(econf),
                    predictions=load_predictions(p_path),
                    enable_details=True)]
    _mk_report(lconf, dconf, slices, None,
               test_data=True)
    _copy_version_files(lconf, True)

    report_dir = report_dir_path(lconf, True, None)
    final_report_dir = fp.join(lconf.eval_dir,
                               report_dir_basename(lconf, True))
    mk_test_graphs(lconf, dconf)
    _mk_hashfile(lconf, dconf, True)
    # this can happen if resuming a report; better copy
    # it again
    if fp.exists(final_report_dir):
        shutil.rmtree(final_report_dir)
    shutil.copytree(report_dir, final_report_dir)
    print('TEST Report saved in ', final_report_dir,
          file=sys.stderr)
