# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
build models for standalone parser
"""

from __future__ import print_function
from os import path as fp
from collections import namedtuple
import cPickle
import os
import sys

from attelo.args import\
    DEFAULT_DECODER,\
    DEFAULT_HEURISTIC,\
    DEFAULT_NIT,\
    DEFAULT_RFC
from attelo.io import read_data
import attelo.cmd as att
import Orange.data

from attelo.harness.util import\
    call, force_symlink

from ..local import\
    DIALOGUE_ACT_LEARNER,\
    SNAPSHOTS, EVALUATION_CORPORA, MODELERS, ATTELO_CONFIG_FILE
from ..util import\
    exit_ungathered, latest_tmp, latest_snap, link_files,\
    snap_model_path, snap_dialogue_act_model_path

NAME = 'model'

#pylint: disable=pointless-string-statement
LoopConfig = namedtuple("LoopConfig",
                        ["snap_dir",
                         "dataset"])
"that which is common to outerish loops"


DataConfig = namedtuple("DataConfig", "attach relate")
"data tables we have read"
#pylint: enable=pointless-string-statement

# ---------------------------------------------------------------------
# user feedback
# ---------------------------------------------------------------------


def _model_banner(econf, lconf):
    """
    Which combo of eval parameters are we running now?
    """
    rname = econf.learner.relate
    learner_str = econf.learner.attach + (":" + rname if rname else "")
    return "\n".join(["----------" * 3,
                      "%s" % lconf.dataset,
                      "learner(s): %s" % learner_str,
                      "----------" * 3])


def _corpus_banner(lconf):
    "banner to announce the corpus"
    return "\n".join(["==========" * 7,
                      lconf.dataset,
                      "==========" * 7])


# ---------------------------------------------------------------------
# attelo config
# ---------------------------------------------------------------------


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class FakeLearnArgs(object):
    """
    Fake argparse object (to be subclassed)
    Things in common between attelo learn/decode
    """
    def __init__(self, lconf, econf):
        model_file_a = snap_model_path(lconf, econf, "attach")
        model_file_r = snap_model_path(lconf, econf, "relate")

        self.config = ATTELO_CONFIG_FILE
        self.data_attach = _data_path(lconf, "edu-pairs"),
        self.data_relations = _data_path(lconf, "relations")
        self.attachment_model = model_file_a
        self.relation_model = model_file_r
        self.fold_file = None
        self.fold = None
        self.threshold = None
        self.use_prob = None
        self.heuristics = DEFAULT_HEURISTIC
        self.rfc = DEFAULT_RFC
        self.quiet = False

        self.decoder = econf.decoder.decoder\
            if econf.decoder is not None else DEFAULT_DECODER
        self.learner = econf.learner.attach
        self.relation_learner = econf.learner.relate
        self.nit = DEFAULT_NIT
        self.averaging = False

    # pylint: disable=no-self-use
    def cleanup(self):
        "Tidy up any open file handles, etc"
        return
    # pylint: enable=no-self-use
# pylint: enable=too-many-instance-attributes, too-few-public-methods


# ---------------------------------------------------------------------
# model building
# ---------------------------------------------------------------------


def _data_path(lconf, ext):
    """
    Path to data file in the evaluation dir
    """
    return os.path.join(lconf.snap_dir,
                        "%s.%s.csv" % (lconf.dataset, ext))


def _decode_output_path(lconf, econf):
    "Model for a given loop/eval config and fold"
    return os.path.join(lconf.snap_dir,
                        ".".join(["output", econf.name]))


def _learn(lconf, dconf, econf):
    """
    Run the learner unless the model files already exist
    """
    args = FakeLearnArgs(lconf, econf)
    att.learn.main_for_harness(args, dconf.attach, dconf.relate)
    args.cleanup()


def _save_dialogue_act_model(lconf):
    """
    Build a model from the single EDU features and save to disk
    """
    data = Orange.data.Table(_data_path(lconf, "just-edus"))
    model = DIALOGUE_ACT_LEARNER(data)
    model_file = snap_dialogue_act_model_path(lconf, raw=True)
    with open(model_file, "wb") as fstream:
        cPickle.dump(model, fstream)


def _do_corpus(lconf):
    "Build models for a corpus"
    print(_corpus_banner(lconf), file=sys.stderr)

    attach_file = _data_path(lconf, "edu-pairs")
    relate_file = _data_path(lconf, "relations")
    if not os.path.exists(attach_file):
        exit_ungathered()
    data_attach, data_relate =\
        read_data(attach_file, relate_file, verbose=True)
    dconf = DataConfig(attach=data_attach,
                       relate=data_relate)

    for econf in MODELERS:
        print(_model_banner(econf, lconf), file=sys.stderr)
        _learn(lconf, dconf, econf)

    # dialogue acts model
    _save_dialogue_act_model(lconf)
    os.rename(snap_dialogue_act_model_path(lconf, raw=True),
              snap_dialogue_act_model_path(lconf, raw=False))


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
    return snap_dir


def main(_):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    data_dir = latest_tmp()
    if not os.path.exists(data_dir):
        exit_ungathered()
    snap_dir = _create_snapshot_dir(data_dir)

    with open(os.path.join(snap_dir, "versions-model.txt"), "w") as stream:
        call(["pip", "freeze"], stdout=stream)

    for corpus in EVALUATION_CORPORA:
        dataset = os.path.basename(corpus)
        lconf = LoopConfig(snap_dir=snap_dir,
                           dataset=dataset)
        _do_corpus(lconf)
