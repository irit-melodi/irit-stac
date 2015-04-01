# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
build models for standalone parser
"""

from __future__ import print_function
from os import path as fp
import os
import sys

from attelo.harness.util import (call, force_symlink)
from attelo.io import (load_multipack, Torpor)

from ..learn import (mk_combined_models)
from ..local import (DIALOGUE_ACT_LEARNER,
                     SNAPSHOTS,
                     TRAINING_CORPUS)
from ..loop import (LoopConfig,
                    DataConfig)
from ..path import (edu_input_path,
                    eval_model_path,
                    eval_data_path,
                    pairings_path,
                    features_path)
from ..util import (exit_ungathered, sanity_check_config,
                    latest_tmp, latest_snap, link_files)
import stac.unit_annotations as stac_unit

NAME = 'model'


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def _create_snapshot_dir(data_dir):
    """
    Instantiate a snapshot dir and return its path
    """

    bname = fp.basename(os.readlink(data_dir))
    snap_dir = fp.join(SNAPSHOTS, bname)
    if not fp.exists(snap_dir):
        os.makedirs(snap_dir)
        link_files(data_dir, snap_dir)
        force_symlink(bname, latest_snap())
    with open(fp.join(snap_dir, "versions-model.txt"), "w") as stream:
        call(["pip", "freeze"], stdout=stream)
    return snap_dir


def _mk_dialogue_act_model(lconf):
    "Learn and save the dialogue acts model"
    mpath = eval_model_path(lconf,
                            DIALOGUE_ACT_LEARNER,
                            None,
                            'dialogue-acts')
    fpath = eval_data_path(lconf,
                           'dialogue-acts.sparse')
    with Torpor('Learning dialogue acts model'):
        stac_unit.learn_and_save(DIALOGUE_ACT_LEARNER.payload,
                                 fpath, mpath)


def _do_corpus(lconf):
    "Run evaluation on a corpus"
    edus_file = edu_input_path(lconf)
    if not os.path.exists(edus_file):
        exit_ungathered()

    mpack = load_multipack(edus_file,
                           pairings_path(lconf),
                           features_path(lconf),
                           verbose=True)
    dconf = DataConfig(pack=mpack,
                       folds=None)
    mk_combined_models(lconf, dconf)
    _mk_dialogue_act_model(lconf)

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------


def config_argparser(psr):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    psr.set_defaults(func=main)
    psr.add_argument("--n-jobs", type=int,
                     default=-1,
                     help="number of jobs (-1 for max [DEFAULT], "
                     "2+ for parallel, "
                     "1 for sequential but using parallel infrastructure, "
                     "0 for fully sequential)")


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    sys.setrecursionlimit(10000)
    sanity_check_config()
    data_dir = latest_tmp()
    if not fp.exists(data_dir):
        exit_ungathered()
    snap_dir = _create_snapshot_dir(data_dir)

    dataset = fp.basename(TRAINING_CORPUS)
    lconf = LoopConfig(eval_dir=snap_dir,
                       scratch_dir=snap_dir,
                       folds=None,
                       stage=None,
                       fold_file=None,
                       n_jobs=args.n_jobs,
                       dataset=dataset)
    _do_corpus(lconf)
