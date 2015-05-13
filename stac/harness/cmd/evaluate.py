# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
run an experiment
"""

from __future__ import print_function

from attelo.harness import (RuntimeConfig, ClusterStage)

from ..harness import (IritHarness)

# pylint: disable=too-few-public-methods

NAME = 'evaluate'

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
    mode_grp = psr.add_mutually_exclusive_group()
    mode_grp.add_argument("--resume",
                          default=False, action="store_true",
                          help="resume previous interrupted evaluation")
    mode_grp.add_argument("--jumpstart", action='store_true',
                          help="copy any model files over from last "
                          "evaluation (useful if you just want to "
                          "evaluate recent changes to the decoders "
                          "without losing previous scores)")

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
    if args.resume:
        mode = 'resume'
    elif args.jumpstart:
        mode = 'jumpstart'
    else:
        mode = None
    runcfg = RuntimeConfig(mode=mode,
                           folds=args.folds,
                           stage=args_to_stage(args),
                           n_jobs=args.n_jobs)
    hconf = IritHarness()
    hconf.run(runcfg)
