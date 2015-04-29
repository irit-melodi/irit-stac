# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)


"""
Building models from features
"""

from __future__ import print_function
import os
import sys

from attelo.fold import (select_training)

from .path import (attelo_model_paths,
                   combined_dir_path,
                   fold_dir_path)


def learn(lconf, econf, dconf, fold):
    """
    Run the learners for the given configuration
    """
    if fold is None:
        parent_dir = combined_dir_path(lconf)
        get_subpack = lambda d: d
    else:
        parent_dir = fold_dir_path(lconf, fold)
        get_subpack = lambda d: select_training(d, dconf.folds, fold)

    if WINDOW <= -1:
        narrow = lambda d: d
    else:
        narrow = lambda d: select_window(d, WINDOW)

    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    cache = attelo_model_paths(lconf, econf.learner, fold)
    print('learning ', econf.key, '...', file=sys.stderr)
    dpacks = get_subpack(dconf.pack).values()
    targets = [d.target for d in dpacks]
    econf.parser.payload.fit(dpacks, targets, cache=cache)


def mk_combined_models(lconf, econfs, dconf):
    """
    Create global for all learners
    """
    for econf in econfs:
        learn(lconf, econf, dconf, None)
