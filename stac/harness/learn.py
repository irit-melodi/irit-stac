'''Building models from features
'''

from __future__ import print_function
from os import path as fp
import os
import sys

from attelo.learning import (Task)
from attelo.table import (for_intra, select_window)
from attelo.util import (Team)
import attelo.harness.learn as ath_learn
from joblib import (delayed)

from .local import (EVALUATIONS, WINDOW)
from .path import (attelo_doc_model_paths,
                   attelo_sent_model_paths,
                   combined_dir_path,
                   fold_dir_path)
from .util import (concat_i, parallel)


LEARNERS = {e.learner.key: e.learner for e in EVALUATIONS}.values()


def _get_learn_job(lconf, rconf, subpack, paths, task):
    'learn a model and write it to the given output path'

    if task == Task.attach:
        sub_rconf = rconf.attach
        output_path = paths.attach
    elif task == Task.relate:
        sub_rconf = rconf.relate or rconf.attach
        output_path = paths.relate
    else:
        raise ValueError('Unknown learning task: {}'.format(task))

    if sub_rconf.key == 'oracle':
        return None
    elif fp.exists(output_path):
        print(("reusing {key} {task} model (already built): {path}"
               "").format(key=sub_rconf.key,
                          task=task.name,
                          path=fp.relpath(output_path, lconf.scratch_dir)),
              file=sys.stderr)
    else:
        learn_fn = ath_learn.learn
        learners = Team(attach=rconf.attach,
                        relate=rconf.relate or rconf.attach)
        learners = learners.fmap(lambda x: x.payload)
        return delayed(learn_fn)(subpack, learners, task, output_path,
                                 quiet=False)


def delayed_learn(lconf, dconf, rconf, fold, include_intra):
    """
    Return possible futures for learning models for this
    fold
    """
    if fold is None:
        parent_dir = combined_dir_path(lconf)
        get_subpack_ = lambda d: d
    else:
        parent_dir = fold_dir_path(lconf, fold)
        get_subpack_ = lambda d: d.training(dconf.folds, fold)

    get_subpack = lambda d: select_window(get_subpack_(d),
                                          None if WINDOW < -1 else WINDOW)

    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    jobs = []
    if True:
        subpack = get_subpack(dconf.pack)
        paths = attelo_doc_model_paths(lconf, rconf, fold)
        jobs.append(_get_learn_job(lconf, rconf, subpack, paths, Task.attach))
        jobs.append(_get_learn_job(lconf, rconf, subpack, paths, Task.relate))
    if include_intra:
        subpack = for_intra(get_subpack(dconf.pack))
        paths = attelo_sent_model_paths(lconf, rconf, fold)
        jobs.append(_get_learn_job(lconf, rconf, subpack, paths, Task.attach))
        jobs.append(_get_learn_job(lconf, rconf, subpack, paths, Task.relate))
    return [j for j in jobs if j is not None]


def mk_combined_models(lconf, dconf):
    """
    Create global for all learners
    """
    include_intra = any(e.settings.intra is not None
                        for e in EVALUATIONS)
    jobs = concat_i(delayed_learn(lconf, dconf, learner, None, include_intra)
                    for learner in LEARNERS)
    parallel(lconf)(jobs)
