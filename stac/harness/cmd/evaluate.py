# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
run an experiment
"""

from __future__ import print_function
from os import path as fp
from collections import namedtuple
import json
import os
import sys

from attelo.args import\
    args_to_decoder, args_to_phrasebook, args_to_threshold,\
    DEFAULT_HEURISTIC, DEFAULT_RFC, DEFAULT_NIT, DEFAULT_NFOLD
from attelo.decoding import\
    DataAndModel, DecoderConfig
from attelo.io import\
    read_data, load_model
import attelo.cmd as att

from attelo.harness.report import CountIndex
from attelo.harness.util import\
    timestamp, call, force_symlink

from ..local import\
    EVALUATION_CORPORA, EVALUATIONS, ATTELO_CONFIG_FILE
from ..util import latest_tmp, link_files

NAME = 'evaluate'
_DEBUG = 0

#pylint: disable=pointless-string-statement
LoopConfig = namedtuple("LoopConfig",
                        ["eval_dir",
                         "scratch_dir",
                         "fold_file",
                         "dataset"])
"that which is common to outerish loops"

DataConfig = namedtuple("DataConfig", "attach relate")
"data tables we have read"
#pylint: enable=pointless-string-statement

# ---------------------------------------------------------------------
# user feedback
# ---------------------------------------------------------------------


def _exit_ungathered():
    """
    You don't seem to have run the gather command
    """
    sys.exit("""No data to run experiments on.
Please run `irit-rst-dt gather`""")


def _eval_banner(econf, lconf, fold):
    """
    Which combo of eval parameters are we running now?
    """
    rname = econf.learner.relate
    learner_str = econf.learner.attach + (":" + rname if rname else "")
    return "\n".join(["----------" * 3,
                      "fold %d [%s]" % (fold, lconf.dataset),
                      "learner(s): %s" % learner_str,
                      "decoder: %s" % econf.decoder.decoder,
                      "----------" * 3])


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
# attelo config
# ---------------------------------------------------------------------


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class FakeEvalArgs(object):
    """
    Fake argparse object (to be subclassed)
    Things in common between attelo learn/decode
    """
    def __init__(self, lconf, econf, fold):
        model_file_a = _eval_model_path(lconf, econf, fold, "attach")
        model_file_r = _eval_model_path(lconf, econf, fold, "relate")

        self.config = ATTELO_CONFIG_FILE
        self.data_attach = _eval_csv_path(lconf, "edu-pairs"),
        self.data_relations = _eval_csv_path(lconf, "relations")
        self.attachment_model = model_file_a
        self.relation_model = model_file_r
        self.fold_file = open(lconf.fold_file, "r")
        self.fold = fold
        self.threshold = None
        self.use_prob = None
        self.heuristics = DEFAULT_HEURISTIC
        self.rfc = DEFAULT_RFC
        self.quiet = False

    def cleanup(self):
        "Tidy up any open file handles, etc"
        self.fold_file.close()


class FakeEnfoldArgs(object):
    """
    Fake argparse object that would be generated by attelo enfold
    """
    def __init__(self, lconf):
        self.config = ATTELO_CONFIG_FILE
        self.nfold = DEFAULT_NFOLD
        self.attachment_model = _eval_csv_path(lconf, "edu-pairs")
        self.relation_model = None
        self.shuffle = False
        self.output = open(lconf.fold_file, "w")

    def cleanup(self):
        "Tidy up any open file handles, etc"
        self.output.close()


class FakeLearnArgs(FakeEvalArgs):
    """
    Fake argparse object that would be generated by attelo learn
    """
    def __init__(self, lconf, econf, fold):
        super(FakeLearnArgs, self).__init__(lconf, econf, fold)

        self.decoder = econf.decoder.decoder
        self.learner = econf.learner.attach
        self.relation_learner = econf.learner.relate
        self.nit = DEFAULT_NIT
        self.averaging = False


class FakeDecodeArgs(FakeEvalArgs):
    """
    Fake argparse object that would be generated by attelo decode
    """
    def __init__(self, lconf, econf, fold):
        super(FakeDecodeArgs, self).__init__(lconf, econf, fold)
        self.decoder = econf.decoder.decoder
        self.scores = open(_counts_file_path(lconf, econf, fold), "w")
        self.output = _decode_output_path(lconf, econf, fold)

    def cleanup(self):
        "Tidy up any open file handles, etc"
        super(FakeDecodeArgs, self).cleanup()
        self.scores.close()
# pylint: enable=too-many-instance-attributes, too-few-public-methods


# ---------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------

def _eval_csv_path(lconf, ext):
    """
    Path to data file in the evaluation dir
    """
    return os.path.join(lconf.eval_dir,
                        "%s.%s.csv" % (lconf.dataset, ext))


def _fold_dir_path(lconf, fold):
    "Scratch directory for working within a given fold"
    return os.path.join(lconf.scratch_dir, "fold-%d" % fold)


def _eval_model_path(lconf, econf, fold, mtype):
    "Model for a given loop/eval config and fold"
    lname = econf.learner.name
    fold_dir = _fold_dir_path(lconf, fold)
    return os.path.join(fold_dir,
                        "%s.%s.%s.model" % (lconf.dataset, lname, mtype))


def _counts_file_path(lconf, econf, fold):
    "Scores collected for a given loop and eval configuration"
    fold_dir = _fold_dir_path(lconf, fold)
    return os.path.join(fold_dir,
                        ".".join(["counts", econf.name, "csv"]))


def _decode_output_path(lconf, econf, fold):
    "Model for a given loop/eval config and fold"
    fold_dir = _fold_dir_path(lconf, fold)
    return os.path.join(fold_dir,
                        ".".join(["output", econf.name]))


def _index_file_path(parent_dir, lconf):
    """
    Create a blank count index file in the given directory,
    see `CountIndex` for how this is to be used
    """
    return os.path.join(parent_dir,
                        "count-index-%s.csv" % lconf.dataset)


def _score_file_path_prefix(parent_dir, lconf):
    """
    Path to a score file given a parent dir.
    You'll need to tack an extension onto this
    """
    return fp.join(parent_dir, "scores-%s" % lconf.dataset)


def _maybe_learn(lconf, dconf, econf, fold):
    """
    Run the learner unless the model files already exist
    """
    fold_dir = _fold_dir_path(lconf, fold)
    if not os.path.exists(fold_dir):
        os.makedirs(fold_dir)

    args = FakeLearnArgs(lconf, econf, fold)
    phrasebook = args_to_phrasebook(args)
    fold_attach, fold_relate =\
        att.learn.select_fold(dconf.attach,
                              dconf.relate,
                              args,
                              phrasebook)

    if os.path.exists(args.attachment_model) and\
       os.path.exists(args.relation_model):
        print("reusing %s model (already built)" % econf.learner.name,
              file=sys.stderr)
        return

    att.learn.main_for_harness(args, fold_attach, fold_relate)
    args.cleanup()


def _decode(lconf, dconf, econf, fold):
    """
    Run the decoder for this given fold
    """
    if fp.exists(_counts_file_path(lconf, econf, fold)):
        print("skipping %s/%s (already done)" % (econf.learner.name,
                                                 econf.decoder.name),
              file=sys.stderr)
        return

    fold_dir = _fold_dir_path(lconf, fold)
    if not os.path.exists(fold_dir):
        os.makedirs(fold_dir)
    args = FakeDecodeArgs(lconf, econf, fold)
    phrasebook = args_to_phrasebook(args)
    decoder = args_to_decoder(args)

    fold_attach, fold_relate =\
        att.decode.select_fold(dconf.attach, dconf.relate,
                               args, phrasebook)
    attach = DataAndModel(fold_attach,
                          load_model(args.attachment_model))
    relate = DataAndModel(fold_relate,
                          load_model(args.relation_model))
    threshold = args_to_threshold(attach.model, decoder,
                                  requested=args.threshold)
    config = DecoderConfig(phrasebook=phrasebook,
                           threshold=threshold,
                           post_labelling=False,
                           use_prob=args.use_prob)

    att.decode.main_for_harness(args, config, decoder, attach, relate)
    args.cleanup()


def _generate_fold_file(lconf, dconf):
    """
    Generate the folds file
    """
    args = FakeEnfoldArgs(lconf)
    att.enfold.main_for_harness(args, dconf.attach)
    args.cleanup()


def _mk_report(parent_dir, lconf, idx_file):
    "Generate reports for scores"
    score_prefix = _score_file_path_prefix(parent_dir, lconf)
    json_file = score_prefix + ".json"
    pretty_file = score_prefix + ".txt"

    with open(pretty_file, "w") as pretty_stream:
        call(["attelo", "report",
              idx_file,
              "--json", json_file],
             stdout=pretty_stream)

    print("Scores summarised in %s" % pretty_file,
          file=sys.stderr)


def _do_tuple(lconf, dconf, econf, fold):
    """
    Run a single combination of parameters (innermost block)
    Return a counts index entry
    """
    cfile = _counts_file_path(lconf, econf, fold)
    _maybe_learn(lconf, dconf, econf, fold)
    _decode(lconf, dconf, econf, fold)
    return {"config": econf.name,
            "fold": fold,
            "counts_file": cfile}


def _do_fold(lconf, dconf, fold, idx):
    """
    Run all learner/decoder combos within this fold
    """
    fold_dir = _fold_dir_path(lconf, fold)
    score_prefix = _score_file_path_prefix(fold_dir, lconf)
    if fp.exists(score_prefix + ".txt"):
        print("Skipping fold %d (already run)" % fold,
              file=sys.stderr)
        return

    print(_fold_banner(lconf, fold), file=sys.stderr)
    if not os.path.exists(fold_dir):
        os.makedirs(fold_dir)
    fold_idx_file = _index_file_path(fold_dir, lconf)
    with CountIndex(fold_idx_file) as fold_idx:
        for econf in EVALUATIONS:
            print(_eval_banner(econf, lconf, fold), file=sys.stderr)
            idx_entry = _do_tuple(lconf, dconf, econf, fold)
            idx.writerow(idx_entry)
            fold_idx.writerow(idx_entry)
    fold_dir = _fold_dir_path(lconf, fold)
    _mk_report(fold_dir, lconf, fold_idx_file)


def _do_corpus(lconf):
    "Run evaluation on a corpus"
    print(_corpus_banner(lconf), file=sys.stderr)

    attach_file = _eval_csv_path(lconf, "edu-pairs")
    relate_file = _eval_csv_path(lconf, "relations")
    if not os.path.exists(attach_file):
        _exit_ungathered()
    data_attach, data_relate =\
        read_data(attach_file, relate_file, verbose=True)
    dconf = DataConfig(attach=data_attach,
                       relate=data_relate)

    _generate_fold_file(lconf, dconf)

    with open(lconf.fold_file) as f_in:
        folds = frozenset(json.load(f_in).values())

    idx_file = _index_file_path(lconf.scratch_dir, lconf)
    with CountIndex(idx_file) as idx:
        for fold in folds:
            _do_fold(lconf, dconf, fold, idx)
    _mk_report(lconf.eval_dir, lconf, idx_file)

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


def _create_eval_dirs(args, data_dir):
    """
    Return eval and scatch directory paths
    """

    eval_current = fp.join(data_dir, "eval-current")
    scratch_current = fp.join(data_dir, "scratch-current")

    if args.resume:
        if not fp.exists(eval_current) or not fp.exists(scratch_current):
            sys.exit("No currently running evaluation to resume!")
        else:
            return eval_current, scratch_current
    else:
        tstamp = "TEST" if _DEBUG else timestamp()
        eval_dir = fp.join(data_dir, "eval-" + tstamp)
        if not fp.exists(eval_dir):
            os.makedirs(eval_dir)
            link_files(data_dir, eval_dir)
            force_symlink(fp.basename(eval_dir), eval_current)
        elif not _DEBUG:
            sys.exit("Try again in literally one second")

        scratch_dir = fp.join(data_dir, "scratch-" + tstamp)
        if not fp.exists(scratch_dir):
            os.makedirs(scratch_dir)
            force_symlink(fp.basename(scratch_dir), scratch_current)

        return eval_dir, scratch_dir


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    data_dir = latest_tmp()
    if not os.path.exists(data_dir):
        _exit_ungathered()
    eval_dir, scratch_dir = _create_eval_dirs(args, data_dir)

    with open(os.path.join(eval_dir, "versions.txt"), "w") as stream:
        call(["pip", "freeze"], stdout=stream)

    for corpus in EVALUATION_CORPORA:
        dataset = os.path.basename(corpus)
        fold_file = os.path.join(eval_dir,
                                 "folds-%s.json" % dataset)
        lconf = LoopConfig(eval_dir=eval_dir,
                           scratch_dir=scratch_dir,
                           fold_file=fold_file,
                           dataset=dataset)
        _do_corpus(lconf)