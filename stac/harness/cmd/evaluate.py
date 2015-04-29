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

from attelo.io import (load_multipack,
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
                     NAUGHTY_TURN_CONSTRAINT,
                     TRAINING_CORPUS,
                     TEST_CORPUS)
from ..path import (fold_dir_path,
                    mpack_paths)
from ..report import (mk_fold_report,
                      mk_global_report,
                      mk_test_report)
from ..util import (concat_i,
                    exit_ungathered,
                    latest_tmp,
                    parallel,
                    sanity_check_config,
                    test_evaluation)
from ..loop import (LoopConfig,
                    DataConfig,
                    ClusterStage)
from ..turn_constraint import (apply_turn_constraint)

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
        if fp.isfile(data_file) and not fp.exists(eval_file):
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


def _link_fold_files(old_dir, new_dir):
    """
    Hardlink the fold file
    """
    for old_path in glob.glob(fp.join(old_dir, 'folds*.json')):
        new_path = fp.join(new_dir, fp.basename(old_path))
        os.link(old_path, new_path)


def _create_tstamped_dir(prefix, suffix):
    """
    Given a path prefix (eg. 'foo/bar') and a new suffix
    (eg. quux),

    If the desired path (eg. 'foo/bar-quux') already exists,
    return False.
    Otherwise:

    1. Create a directory at the desired path
    2. Rename any existing prefix-'current' link
       to prefix-'previous'
    3. Link prefix-suffix to prefix-'current'
    4. Return True
    """
    old = prefix + '-previous'
    new = prefix + '-current'
    actual_new = prefix + '-' + suffix
    if fp.exists(actual_new):
        return False
    else:
        os.makedirs(actual_new)
        if os.path.exists(new):
            actual_old = fp.realpath(prefix + '-current')
            force_symlink(fp.basename(actual_old), old)
        force_symlink(fp.basename(actual_new), new)
        return True


def _create_eval_dirs(args, data_dir, jumpstart):
    """
    Return eval and scatch directory paths
    """
    eval_prefix = fp.join(data_dir, "eval")
    scratch_prefix = fp.join(data_dir, "scratch")

    eval_current = eval_prefix + '-current'
    scratch_current = scratch_prefix + '-current'
    stage = args_to_stage(args)

    if args.resume or stage in [ClusterStage.main,
                                ClusterStage.combined_models,
                                ClusterStage.end]:
        if not fp.exists(eval_current) or not fp.exists(scratch_current):
            sys.exit("No currently running evaluation to resume!")
        else:
            eval_dir = fp.realpath(eval_current)
            scratch_dir = fp.realpath(scratch_current)
            # in case there are any new data files to link
            _link_data_files(data_dir, eval_dir)
            return eval_dir, scratch_dir
    else:
        eval_actual_old = fp.realpath(eval_current)
        scratch_actual_old = fp.realpath(scratch_current)
        tstamp = "TEST" if _DEBUG else timestamp()
        if _create_tstamped_dir(eval_prefix, tstamp):
            eval_dir = eval_prefix + '-' + tstamp
            scratch_dir = scratch_prefix + '-' + tstamp
            _create_tstamped_dir(scratch_prefix, tstamp)
            _link_data_files(data_dir, eval_dir)
            if jumpstart:
                _link_fold_files(eval_actual_old, eval_dir)
                _link_model_files(scratch_actual_old, scratch_dir)
        elif not _DEBUG:
            sys.exit("Try again in one minute")

        with open(fp.join(eval_dir, "versions-evaluate.txt"), "w") as stream:
            call(["pip", "freeze"], stdout=stream)

        return eval_dir, scratch_dir

# ---------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------


def _generate_fold_file(lconf, mpack):
    """
    Generate the folds file; return the resulting folds
    """
    rng = mk_rng()
    fold_dict = attelo.fold.make_n_fold(mpack, 10, rng)
    save_fold_dict(fold_dict, lconf.fold_file)
    return fold_dict


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


def _do_global_decode(lconf, dconf):
    """
    Run decoder on test data (if available)
    """
    econf = test_evaluation()
    if econf is not None:
        decoder_jobs = delayed_decode(lconf, dconf, econf, None)
        parallel(lconf)(decoder_jobs)
        post_decode(lconf, dconf, econf, None)


def _is_standalone_or(lconf, stage):
    """
    True if we are in standalone mode (do everything)
    or in a given cluster stage
    """
    return lconf.stage is None or lconf.stage == stage


def _load_harness_multipack(lconf, test_data=False):
    """
    Load the multipack for our current configuration.

    Load the stripped features file if we don't actually need to
    use the features (this would only make sense on the cluster
    where evaluation is broken up into separate stages that we
    can fire on different nodes)

    :type test_data: bool

    :rtype: Multipack
    """
    stripped_paths = mpack_paths(lconf, test_data, stripped=True)
    if (lconf.stage in [ClusterStage.end, ClusterStage.start]
            and fp.exists(stripped_paths[2])):
        paths = stripped_paths
    else:
        paths = mpack_paths(lconf, test_data, stripped=False)
    return load_multipack(paths[0],
                          paths[1],
                          paths[2],
                          paths[3],
                          verbose=True)


def _apply_naughty_filters(lconf, mpack):
    """Make any modifications to the multipack that we load as we see
    fit
    """
    for key in mpack:
        if 'turn-constraint' in lconf.naughty_filters:
            mpack[key] = apply_turn_constraint(mpack[key])
    return mpack


def _init_corpus(lconf):
    """Start evaluation; generate folds if needed

    :rtype: DataConfig or None
    """
    can_skip_folds = fp.exists(lconf.fold_file)
    msg_skip_folds = ('Skipping generation of fold files '
                      '(must have been jumpstarted)')

    if lconf.stage is None:
        # standalone: we always have to load the datapack
        # because we'll need it for further stages
        mpack = _load_harness_multipack(lconf)
        if can_skip_folds:
            print(msg_skip_folds, file=sys.stderr)
            fold_dict = load_fold_dict(lconf.fold_file)
        else:
            fold_dict = _generate_fold_file(lconf, mpack)
        mpack = _apply_naughty_filters(lconf, mpack)
        return DataConfig(pack=mpack, folds=fold_dict)
    elif lconf.stage == ClusterStage.start:
        if can_skip_folds:
            # if we are just running --start and the fold file already
            # exists we can even bail out before reading the datapacks
            # because that's all we wanted them for
            print(msg_skip_folds, file=sys.stderr)
        else:
            mpack = _load_harness_multipack(lconf)
            _generate_fold_file(lconf, mpack)
        return None
    else:
        # any other stage: fold files have already been
        # created so we just read them in
        mpack = _load_harness_multipack(lconf)
        mpack = _apply_naughty_filters(lconf, mpack)
        fold_dict = load_fold_dict(lconf.fold_file)
        return DataConfig(pack=mpack, folds=fold_dict)


def _do_corpus(lconf):
    "Run evaluation on a corpus"
    print(_corpus_banner(lconf), file=sys.stderr)

    evidence_of_gathered = mpack_paths(lconf, False)[0]
    if not fp.exists(evidence_of_gathered):
        exit_ungathered()

    dconf = _init_corpus(lconf)
    if _is_standalone_or(lconf, ClusterStage.main):
        foldset = lconf.folds if lconf.folds is not None\
            else frozenset(dconf.folds.values())
        for fold in foldset:
            _do_fold(lconf, dconf, fold)

    if _is_standalone_or(lconf, ClusterStage.combined_models):
        mk_combined_models(lconf, dconf)
        if test_evaluation() is not None:
            test_pack = _load_harness_multipack(lconf, test_data=True)
            test_dconf = DataConfig(pack=test_pack, folds=None)
            _do_global_decode(lconf, test_dconf)
            mk_test_report(lconf, test_dconf)

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
    testset = None if TEST_CORPUS is None else fp.basename(TEST_CORPUS)
    fold_file = fp.join(eval_dir, "folds-%s.json" % dataset)

    naughty_filters = []
    if NAUGHTY_TURN_CONSTRAINT:
        naughty_filters.append('turn-constraint')


    lconf = LoopConfig(eval_dir=eval_dir,
                       scratch_dir=scratch_dir,
                       naughty_filters=naughty_filters,
                       folds=args.folds,
                       stage=stage,
                       fold_file=fold_file,
                       n_jobs=args.n_jobs,
                       dataset=dataset,
                       testset=testset)
    _do_corpus(lconf)
