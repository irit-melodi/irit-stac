'''
graphing output from the harness
'''

from __future__ import print_function
from enum import Enum
from os import path as fp

from attelo.fold import (select_testing)
from attelo.graph import (diff_all, graph_all,
                          GraphSettings)
from attelo.io import (Torpor, load_predictions)
from attelo.util import (concat_l)
from joblib import (Parallel, delayed)

from .local import (GRAPH_DOCS,
                    DETAILED_EVALUATIONS)
from .path import (decode_output_path,
                   fold_dir_basename,
                   report_dir_path)
from .util import (test_evaluation)

# pylint: disable=too-few-public-methods


class GraphDiffMode(Enum):
    "what sort of graph output to make"
    solo = 1
    diff = 2
    diff_intra = 3


def to_predictions(mpack):
    """
    Convert a multipack to a list of predictions
    """
    return [(x1.id, x2.id, dpack.get_label(t))
            for dpack in mpack.values()
            for ((x1, x2), t) in zip(dpack.pairings,
                                     dpack.target)]


def _mk_econf_graphs(lconf, edus, gold, econf, fold):
    "Return jobs generating graphs for a single configuration"
    predictions = load_predictions(decode_output_path(lconf, econf, fold))
    for diffmode in GraphDiffMode:
        # output path
        if diffmode == GraphDiffMode.solo:
            output_bn_prefix = 'graphs-'
        elif diffmode == GraphDiffMode.diff:
            output_bn_prefix = 'graphs-gold-vs-'
        elif diffmode == GraphDiffMode.diff_intra:
            output_bn_prefix = 'graphs-sent-gold-vs-'
        else:
            raise Exception('Unknown diff mode {}'.format(diffmode))

        want_test = fold is None
        suffix = 'test' if want_test else fold_dir_basename(fold)
        output_dir = fp.join(report_dir_path(lconf, want_test, None),
                             output_bn_prefix + suffix,
                             econf.key)

        # settings
        to_hide = 'inter' if diffmode == GraphDiffMode.diff_intra else None
        settings =\
            GraphSettings(hide=to_hide,
                          select=GRAPH_DOCS,
                          unrelated=False,
                          timeout=15,
                          quiet=False)

        if diffmode == GraphDiffMode.solo:
            yield delayed(graph_all)(edus,
                                     predictions,
                                     settings,
                                     output_dir)
        else:
            yield delayed(diff_all)(edus,
                                    gold,
                                    predictions,
                                    settings,
                                    output_dir)


def _mk_gold_graphs(lconf, dconf):
    "Generate graphs for a single configuration"
    # output path
    output_dir = fp.join(report_dir_path(lconf, None),
                         'graphs-gold')

    settings =\
        GraphSettings(hide=None,
                      select=GRAPH_DOCS,
                      unrelated=False,
                      timeout=15,
                      quiet=True)

    predictions = to_predictions(dconf.pack)
    edus = concat_l(dpack.edus for dpack in dconf.pack.values())
    graph_all(edus, predictions, settings, output_dir)


def mk_graphs(lconf, dconf):
    "Generate graphs for the gold data and for one of the folds"
    with Torpor('creating gold graphs'):
        _mk_gold_graphs(lconf, dconf)
    fold = sorted(set(dconf.folds.values()))[0]

    with Torpor('creating graphs for fold {}'.format(fold),
                sameline=False):
        test_pack = select_testing(dconf.pack, dconf.folds, fold)
        edus = concat_l(dpack.edus for dpack in test_pack.values())
        gold = to_predictions(test_pack)
        jobs = []
        for econf in DETAILED_EVALUATIONS:
            jobs.extend(_mk_econf_graphs(lconf, edus, gold, econf, fold))
        Parallel(n_jobs=-1)(jobs)


def mk_test_graphs(lconf, dconf):
    "Generate graphs for test data"
    econf = test_evaluation()
    if econf is None:
        return
    with Torpor('creating test graphs'):
        edus = concat_l(dpack.edus for dpack in dconf.pack.values())
        gold = to_predictions(dconf.pack)
        _mk_econf_graphs(lconf, edus, gold, econf, None)
