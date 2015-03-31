# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
run an experiment
"""

from __future__ import print_function
from os import path as fp
import glob
import os
import sys

from attelo.io import (load_data_pack,
                       load_fold_dict, save_fold_dict)
from attelo.harness.util import\
    timestamp, call, force_symlink
from attelo.util import (mk_rng)
import attelo.fold
import attelo.score
import attelo.report

from ..decode import (delayed_decode, post_decode)
from ..learn import (LEARNERS,
                     delayed_learn,
                     mk_combined_models)
from ..local import (EVALUATIONS,
                     TRAINING_CORPUS)
from ..path import (edu_input_path,
                    features_path,
                    fold_dir_path,
                    pairings_path)
from ..report import (mk_fold_report,
                      mk_global_report)
from ..util import (concat_i,
                    exit_ungathered,
                    latest_tmp,
                    parallel,
                    sanity_check_config)
from ..loop import (LoopConfig,
                    DataConfig,
                    ClusterStage)

# pylint: disable=too-few-public-methods

NAME = 'evaluate'
_DEBUG = 0

# ---------------------------------------------------------------------
# CODE CONVENTIONS USED HERE
# ---------------------------------------------------------------------
#
# lconf - loop config :: LoopConfig
# rconf - learner config :: LearnerConfig
# econf - evaluation config :: EvaluationConfig
# dconf - data config :: DataConfig

# ---------------------------------------------------------------------
# user feedback
# ---------------------------------------------------------------------


def _corpus_banner(lconf):
    "banner to announce the corpus"
    return "\n".join(["==========" * 7,
                      lconf.dataset,
                      "==========" * 7])


def _fold_banner(lconf, fold):
    "banner to announce the next fold"
    return "\n".join(["==========" * 6,
                      "fold %d [%s]" % (fold, lconf.dataset),
                      "==========" * 6])

# ---------------------------------------------------------------------
# preparation
# ---------------------------------------------------------------------


def _link_data_files(data_dir, eval_dir):
    """
    Hard-link all files from the data dir into the evaluation
    directory. This does not cost space and it makes future
    archiving a bit more straightforward
    """
    for fname in os.listdir(data_dir):
        data_file = os.path.join(data_dir, fname)
        eval_file = os.path.join(eval_dir, fname)
        if os.path.isfile(data_file):
            os.link(data_file, eval_file)


def _link_model_files(old_dir, new_dir):
    """
    Hardlink any fold-level or combined folds files
    """
    for old_mpath in glob.glob(fp.join(old_dir, '*', '*model*')):
        old_fold_dir_bn = fp.basename(fp.dirname(old_mpath))
        new_fold_dir = fp.join(new_dir, old_fold_dir_bn)
        new_mpath = fp.join(new_fold_dir, fp.basename(old_mpath))
        if not fp.exists(new_fold_dir):
            os.makedirs(new_fold_dir)
        os.link(old_mpath, new_mpath)


def _create_eval_dirs(args, data_dir, jumpstart):
    """
    Return eval and scatch directory paths
    """

    eval_current = fp.join(data_dir, "eval-current")
    scratch_current = fp.join(data_dir, "scratch-current")
    stage = args_to_stage(args)

    if args.resume or stage in [ClusterStage.main,
                                ClusterStage.combined_models,
                                ClusterStage.end]:
        if not fp.exists(eval_current) or not fp.exists(scratch_current):
            sys.exit("No currently running evaluation to resume!")
        else:
            return eval_current, scratch_current
    else:
        tstamp = "TEST" if _DEBUG else timestamp()
        eval_dir = fp.join(data_dir, "eval-" + tstamp)
        if not fp.exists(eval_dir):
            os.makedirs(eval_dir)
            _link_data_files(data_dir, eval_dir)
            force_symlink(fp.basename(eval_dir), eval_current)
        elif not _DEBUG:
            sys.exit("Try again in one minute")

        scratch_dir = fp.join(data_dir, "scratch-" + tstamp)
        if not fp.exists(scratch_dir):
            os.makedirs(scratch_dir)
            if jumpstart:
                _link_model_files(scratch_current, scratch_dir)
            force_symlink(fp.basename(scratch_dir), scratch_current)

        with open(fp.join(eval_dir, "versions-evaluate.txt"), "w") as stream:
            call(["pip", "freeze"], stdout=stream)

        return eval_dir, scratch_dir

# ---------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------


def _generate_fold_file(lconf, dpack):
    """
    Generate the folds file
    """
    rng = mk_rng()
    fold_dict = attelo.fold.make_n_fold(dpack, 10, rng)
    save_fold_dict(fold_dict, lconf.fold_file)


def _do_fold(lconf, dconf, fold):
    """
    Run all learner/decoder combos within this fold
    """
    fold_dir = fold_dir_path(lconf, fold)
    print(_fold_banner(lconf, fold), file=sys.stderr)
    if not os.path.exists(fold_dir):
        os.makedirs(fold_dir)

    # learn all models in parallel
    include_intra = any(e.settings.intra is not None
                        for e in EVALUATIONS)
    learner_jobs = concat_i(delayed_learn(lconf, dconf, rconf, fold,
                                          include_intra)
                            for rconf in LEARNERS)
    parallel(lconf)(learner_jobs)
    # run all model/decoder joblets in parallel
    decoder_jobs = concat_i(delayed_decode(lconf, dconf, econf, fold)
                            for econf in EVALUATIONS)
    parallel(lconf)(decoder_jobs)
    for econf in EVALUATIONS:
        post_decode(lconf, dconf, econf, fold)
    mk_fold_report(lconf, dconf, fold)


def _is_standalone_or(lconf, stage):
    """
    True if we are in standalone mode (do everything)
    or in a given cluster stage
    """
    return lconf.stage is None or lconf.stage == stage


def _do_corpus(lconf):
    "Run evaluation on a corpus"
    print(_corpus_banner(lconf), file=sys.stderr)

    edus_file = edu_input_path(lconf)
    if not os.path.exists(edus_file):
        exit_ungathered()

    has_stripped = (lconf.stage in [ClusterStage.end, ClusterStage.start]
                    and fp.exists(features_path(lconf, stripped=True)))
    dpack = load_data_pack(edus_file,
                           pairings_path(lconf),
                           features_path(lconf, stripped=has_stripped),
                           verbose=True)

    if _is_standalone_or(lconf, ClusterStage.start):
        _generate_fold_file(lconf, dpack)

    dconf = DataConfig(pack=dpack,
                       folds=load_fold_dict(lconf.fold_file))

    if _is_standalone_or(lconf, ClusterStage.main):
        foldset = lconf.folds if lconf.folds is not None\
            else frozenset(dconf.folds.values())
        for fold in foldset:
            _do_fold(lconf, dconf, fold)

    if _is_standalone_or(lconf, ClusterStage.combined_models):
        mk_combined_models(lconf, dconf)

    if _is_standalone_or(lconf, ClusterStage.end):
        mk_global_report(lconf, dconf)

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
    psr.add_argument("--resume",
                     default=False, action="store_true",
                     help="resume previous interrupted evaluation")
    psr.add_argument("--n-jobs", type=int,
                     default=-1,
                     help="number of jobs (-1 for max [DEFAULT], "
                     "2+ for parallel, "
                     "1 for sequential but using parallel infrastructure, "
                     "0 for fully sequential)")
    psr.add_argument("--jumpstart", action='store_true',
                     help="copy any model files over from last evaluation "
                     "(useful if you just want to evaluate recent changes "
                     "to the decoders without losing previous scores)")

    cluster_grp = psr.add_mutually_exclusive_group()
    cluster_grp.add_argument("--start", action='store_true',
                             default=False,
                             help="initialise an evaluation but don't run it "
                             "(cluster mode)")
    cluster_grp.add_argument("--folds", metavar='N', type=int, nargs='+',
                             help="run only these folds (cluster mode)")
    cluster_grp.add_argument("--combined-models", action='store_true',
                             help="generate only the combined model")
    cluster_grp.add_argument("--end", action='store_true',
                             default=False,
                             help="generate report only (cluster mode)")


def args_to_stage(args):
    "return the cluster stage from the CLI args"

    if args.start:
        return ClusterStage.start
    elif args.folds is not None:
        return ClusterStage.main
    elif args.combined_models:
        return ClusterStage.combined_models
    elif args.end:
        return ClusterStage.end
    else:
        return None


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    sys.setrecursionlimit(10000)
    sanity_check_config()
    stage = args_to_stage(args)
    data_dir = latest_tmp()
    if not os.path.exists(data_dir):
        exit_ungathered()
    eval_dir, scratch_dir = _create_eval_dirs(args, data_dir, args.jumpstart)

    dataset = fp.basename(TRAINING_CORPUS)
    fold_file = fp.join(eval_dir, "folds-%s.json" % dataset)

    lconf = LoopConfig(eval_dir=eval_dir,
                       scratch_dir=scratch_dir,
                       folds=args.folds,
                       stage=stage,
                       fold_file=fold_file,
                       n_jobs=args.n_jobs,
                       dataset=dataset)
    _do_corpus(lconf)
