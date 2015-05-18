# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
build models for standalone parser
"""

from __future__ import print_function
from os import path as fp
import os

from attelo.harness.config import (DataConfig, RuntimeConfig)
from attelo.harness.parse import (learn)
from attelo.harness.util import (call, force_symlink)
from attelo.io import (load_multipack, Torpor)

from ..harness import (IritHarness)
from ..local import (DIALOGUE_ACT_LEARNER,
                     SNAPSHOTS)
from ..pipeline import (dact_features_path,
                        dact_model_path,
                        latest_snap,
                        link_files)
from ..util import (exit_ungathered,
                    latest_tmp)
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


def _mk_dialogue_act_model(hconf):
    "Learn and save the dialogue acts model"
    learner = DIALOGUE_ACT_LEARNER.payload
    fpath = dact_features_path(hconf)
    mpath = dact_model_path(hconf, DIALOGUE_ACT_LEARNER)
    with Torpor('Learning dialogue acts model'):
        stac_unit.learn_and_save(learner, fpath, mpath)


def _do_corpus(hconf):
    "Run evaluation on a corpus"
    paths = hconf.mpack_paths(test_data=False)
    if not fp.exists(paths[0]):
        exit_ungathered()
    mpack = load_multipack(paths[0],
                           paths[1],
                           paths[2],
                           paths[3],
                           verbose=True)
    dconf = DataConfig(pack=mpack,
                       folds=None)
    # (re)learn combined model (we shouldn't assume
    # it's in some scratch directory)
    for econf in hconf.evaluations:
        learn(hconf, econf, dconf, None)
    _mk_dialogue_act_model(hconf)

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
    data_dir = latest_tmp()
    if not fp.exists(data_dir):
        exit_ungathered()
    snap_dir = _create_snapshot_dir(data_dir)
    runcfg = RuntimeConfig(mode=None,
                           folds=None,
                           stage=None,
                           n_jobs=args.n_jobs)
    hconf = IritHarness()
    hconf.load(runcfg, snap_dir, snap_dir)
    _do_corpus(hconf)
