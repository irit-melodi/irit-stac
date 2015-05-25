"""
Paths and settings used for this experimental harness
In the future we may move this to a proper configuration file.
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

from __future__ import print_function
from collections import namedtuple
from os import path as fp
import itertools as itr
import six

import educe.stac.corpus
import numpy as np

from attelo.harness.config import (EvaluationConfig,
                                   LearnerConfig,
                                   ParserConfig,
                                   Keyed)

from attelo.decoding.astar import (AstarArgs,
                                   AstarDecoder,
                                   Heuristic,
                                   RfcConstraint)
from attelo.decoding.baseline import (LastBaseline,
                                      LocalBaseline)
from attelo.decoding.mst import (MstDecoder, MstRootStrategy)
from attelo.learning.perceptron import (Perceptron,
                                        PerceptronArgs,
                                        PassiveAggressive,
                                        StructuredPerceptron,
                                        StructuredPassiveAggressive)
from attelo.learning.local import (SklearnAttachClassifier,
                                   SklearnLabelClassifier)
from attelo.learning.oracle import (AttachOracle, LabelOracle)

from attelo.parser.intra import (HeadToHeadParser,
                                 IntraInterPair,
                                 SentOnlyParser,
                                 SoftParser)
from attelo.parser.full import (JointPipeline,
                                PostlabelPipeline)
from attelo.parser.pipeline import (Pipeline)
from attelo.util import (concat_l)

from sklearn.linear_model import (LogisticRegression,
                                  Perceptron as SkPerceptron,
                                  PassiveAggressiveClassifier as
                                  SkPassiveAggressiveClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


from .turn_constraint import (tc_decoder,
                              tc_learner)

# PATHS

CONFIG_FILE = fp.splitext(__file__)[0] + '.py'


LOCAL_TMP = 'TMP'
"""Things we may want to hold on to (eg. for weeks), but could
live with throwing away as needed"""

SNAPSHOTS = 'data/SNAPSHOTS'
"""Results over time we are making a point of saving"""


TRAINING_CORPUS = 'data/FROZEN/training-2015-04-02'
#TRAINING_CORPUS = 'data/tiny'
"""Corpora for use in building/training models and running our
incremental experiments. Later on we should consider using the
held-out test data for something, but let's make a point of
holding it out for now.

Note that by convention, corpora are identified by their basename.
Something like `data/socl-season1` would result
in a corpus named "socl-season1". This could be awkward if the basename
is used in more than one corpus, but we can revisit this scheme as
needed.
"""

TEST_CORPUS = None
# TEST_CORPUS = 'tiny'
"""Corpora for use in FINAL testing.

You should probably leave this set to None until you've tuned and
tweaked things to the point of being able to write up a paper.
Wouldn't want to overfit to the test corpus, now would we?

(If you leave this set to None, we will perform 10-fold cross
validation on the training data)
"""

# TEST_EVALUATION_KEY = None
TEST_EVALUATION_KEY = 'maxent-AD.L_pst-tc-mst-root'
"""Evaluation to use for testing.

Leave this to None until you think it's OK to look at the test data.
The key should be the evaluation key from one of your EVALUATIONS,
eg. 'maxent-C0.9-AD.L_jnt-mst'

(HINT: you can join them together from the report headers)
"""



LEX_DIR = "lexicon"
"""
Lexicons used to help feature extraction
"""

ANNOTATORS = educe.stac.corpus.METAL_STR
"""
Which annotators to read from during feature extraction
"""

FIXED_FOLD_FILE = None
# FIXED_FOLD_FILE = 'folds-TRAINING.json'
"""
Set this to a file path if you *always* want to use it for your corpus
folds. This is for long standing evaluation experiments; we want to
ensure that we have the same folds across different evaluate experiments,
and even across different runs of gather.

NB. It's up to you to ensure that the folds file makes sense
"""


Settings = namedtuple('Settings', ['key', 'intra'])
"""
Note that this is subclass of Keyed
"""

def combined_key(*variants):
    """return a key from a list of objects that have a
    `key` field each"""
    return '-'.join(v if isinstance(v, six.string_types) else v.key
                    for v in variants)

def decoder_last():
    "our instantiation of the mst decoder"
    return Keyed('last', LastBaseline())

def decoder_local():
    "our instantiation of the mst decoder"
    return Keyed('local', LocalBaseline(0.2, True))

def decoder_mst():
    "our instantiation of the mst decoder"
    return Keyed('mst', MstDecoder(MstRootStrategy.leftmost, True))


def attach_learner_oracle():
    "return a keyed instance of the oracle (virtual) learner"
    return Keyed('oracle', AttachOracle())


def label_learner_oracle():
    "return a keyed instance of the oracle (virtual) learner"
    return Keyed('oracle', LabelOracle())



def attach_learner_maxent():
    "return a keyed instance of maxent learner"
    return Keyed('maxent', SklearnAttachClassifier(LogisticRegression()))

def label_learner_maxent():
    "return a keyed instance of maxent learner"
    return Keyed('maxent', SklearnLabelClassifier(LogisticRegression()))



def attach_learner_dectree():
    "return a keyed instance of decision tree learner"
    return Keyed('dectree', SklearnAttachClassifier(DecisionTreeClassifier()))


def label_learner_dectree():
    "return a keyed instance of decision tree learner"
    return Keyed('dectree', SklearnLabelClassifier(DecisionTreeClassifier()))


def attach_learner_rndforest():
    "return a keyed instance of random forest learner"
    return Keyed('rndforest', SklearnAttachClassifier(RandomForestClassifier()))

def label_learner_rndforest():
    "return a keyed instance of decision tree learner"
    return Keyed('rndforest', SklearnLabelClassifier(RandomForestClassifier()))



LOCAL_PERC_ARGS = PerceptronArgs(iterations=20,
                                 averaging=True,
                                 use_prob=False,
                                 aggressiveness=np.inf)

LOCAL_PA_ARGS = PerceptronArgs(iterations=20,
                               averaging=True,
                               use_prob=False,
                               aggressiveness=np.inf)

STRUCT_PERC_ARGS = PerceptronArgs(iterations=50,
                                  averaging=True,
                                  use_prob=False,
                                  aggressiveness=np.inf)

STRUCT_PA_ARGS = PerceptronArgs(iterations=50,
                                averaging=True,
                                use_prob=False,
                                aggressiveness=np.inf)

ORACLE = LearnerConfig(attach=attach_learner_oracle(),
                       label=label_learner_oracle())

_LOCAL_LEARNERS = [
    #ORACLE,
    LearnerConfig(attach=attach_learner_maxent(),
                  label=label_learner_maxent()),
    LearnerConfig(attach=tc_learner(attach_learner_maxent()),
                  label=tc_learner(label_learner_maxent())),
#    LearnerConfig(attach=attach_learner_maxent(),
#                  label=label_learner_oracle()),
#    LearnerConfig(attach=attach_learner_rndforest(),
#                  label=label_learner_rndforest()),
#    LearnerConfig(attach=Keyed('sk-perceptron',
#                               SkPerceptron(n_iter=20)),
#                  label=learner_maxent()),
#    LearnerConfig(attach=Keyed('sk-pasagg',
#                               SkPassiveAggressiveClassifier(n_iter=20)),
#                  label=learner_maxent()),
#    LearnerConfig(attach=Keyed('dp-perc',
#                               Perceptron(d, LOCAL_PERC_ARGS)),
#                  label=learner_maxent()),
#    LearnerConfig(attach=Keyed('dp-pa',
#                               PassiveAggressive(d, LOCAL_PA_ARGS)),
#                  label=learner_maxent()),
]
"""Straightforward attelo learner algorithms to try

It's up to you to choose values for the key field that can distinguish
between different configurations of your learners.

"""

_STRUCTURED_LEARNERS = [
#    lambda d: LearnerConfig(attach=Keyed('dp-struct-perc',
#                                         StructuredPerceptron(d, STRUCT_PERC_ARGS)),
#                            label=learner_maxent()),
#    lambda d: LearnerConfig(attach=Keyed('dp-struct-pa',
#                                         StructuredPassiveAggressive(d, STRUCT_PA_ARGS)),
#                            label=learner_maxent()),
]

"""Attelo learners that take decoders as arguments.
We assume that they cannot be used relation modelling
"""


def mk_joint(klearner, kdecoder):
    "return a joint decoding parser config"
    settings = Settings(key='AD.L-jnt', intra=True)
    parser_key = combined_key(settings, kdecoder)
    key = combined_key(klearner, parser_key)
    parser = JointPipeline(learner_attach=klearner.attach.payload,
                           learner_label=klearner.label.payload,
                           decoder=kdecoder.payload)
    return EvaluationConfig(key=key,
                            settings=settings,
                            learner=klearner,
                            parser=Keyed(parser_key, parser))


def mk_post(klearner, kdecoder):
    "return a post label parser"
    settings = Settings('AD.L-pst', intra=False)
    parser_key = combined_key(settings, kdecoder)
    key = combined_key(klearner, parser_key)
    parser = PostlabelPipeline(learner_attach=klearner.attach.payload,
                               learner_label=klearner.label.payload,
                               decoder=kdecoder.payload)
    return EvaluationConfig(key=key,
                            settings=settings,
                            learner=klearner,
                            parser=Keyed(parser_key, parser))


def _core_parsers(klearner):
    """Our basic parser configurations
    """
    return [
        # joint
        mk_joint(klearner, decoder_last()),
        mk_joint(klearner, decoder_local()),
        mk_joint(klearner, decoder_mst()),
        mk_joint(klearner, tc_decoder(decoder_local())),
        mk_joint(klearner, tc_decoder(decoder_mst())),

        # postlabeling
        mk_post(klearner, decoder_last()),
        mk_post(klearner, decoder_local()),
        mk_post(klearner, decoder_mst()),
        mk_post(klearner, tc_decoder(decoder_local())),
        mk_post(klearner, tc_decoder(decoder_mst())),
    ]


_INTRA_INTER_CONFIGS = [
    Keyed('iheads', HeadToHeadParser),
    Keyed('ionly', SentOnlyParser),
    Keyed('isoft', SoftParser),
]


# -------------------------------------------------------------------------------
# maybe less to edit below but still worth having a glance
# -------------------------------------------------------------------------------


HARNESS_NAME = 'irit-stac'


def _mk_basic_intras(klearner, kconf):
    """Intra/inter parser based on a single core parser
    """
    def combine(econf):
        "return an intra/inter config out of a vanilla one"
        parsers = IntraInterPair(intra=econf.parser.payload,
                                 inter=econf.parser.payload)
        settings = Settings(key=combined_key(kconf, econf.settings),
                            intra=True)
        kparser = Keyed(combined_key(kconf, econf.parser),
                        kconf.payload(parsers))
        return EvaluationConfig(key=combined_key(econf.learner.key, kparser),
                                settings=settings,
                                learner=econf.learner,
                                parser=kparser)
    return [combine(x) for x in _core_parsers(klearner)]


def _mk_sorc_intras(klearner, kconf):
    """Intra/inter parsers based on a single core parser
    and a sentence oracle
    """
    def combine(econfs):
        "return the combination of the intra/inter parser"
        parsers = IntraInterPair(intra=econfs.intra.parser.payload,
                                 inter=econfs.inter.parser.payload)
        ikey = combined_key('sorc', kconf)
        settings = Settings(key=combined_key(ikey, econfs.inter.settings),
                            intra=True)
        kparser = Keyed(combined_key(ikey, econfs.inter.parser),
                        kconf.payload(parsers))
        return EvaluationConfig(key=combined_key(econfs.inter.learner.key,
                                                 kparser),
                                settings=settings,
                                learner=econfs.inter.learner,
                                parser=kparser)
    parsers = [IntraInterPair(intra=o, inter=p) for o, p in
               zip(_core_parsers(ORACLE), _core_parsers(klearner))]
    return [combine(p) for p in parsers]


def _mk_dorc_intras(klearner, kconf):
    """Intra/inter parsers based on a single core parser
    and a document oracle
    """
    def combine(econfs):
        "return the combination of the intra/inter parser"
        parsers = IntraInterPair(intra=econfs.intra.parser.payload,
                                 inter=econfs.inter.parser.payload)
        ikey = combined_key('dorc', kconf)
        settings = Settings(key=combined_key(ikey, econfs.intra.settings),
                            intra=True)
        kparser = Keyed(combined_key(ikey, econfs.intra.parser),
                        kconf.payload(parsers))
        return EvaluationConfig(key=combined_key(econfs.intra.learner.key,
                                                 kparser),
                                settings=settings,
                                learner=econfs.intra.learner,
                                parser=kparser)
    parsers = [IntraInterPair(intra=x, inter=y) for x, y in
               zip(_core_parsers(klearner), _core_parsers(ORACLE))]
    return [combine(p) for p in parsers]


def _mk_last_intras(klearner, kconf):
    """Intra/inter parsers based on a single core parser
    and the last baseline
    """
    econf_last = mk_joint(klearner, decoder_last())
    def combine(econf):
        "return the combination of the intra/inter parser"
        parsers = IntraInterPair(intra=econf_last.parser.payload,
                                 inter=econf.parser.payload)
        ikey = combined_key('last', kconf)
        settings = Settings(key=combined_key(ikey, econf.settings),
                            intra=True)
        kparser = Keyed(combined_key(ikey, econf.parser),
                        kconf.payload(parsers))
        return EvaluationConfig(key=combined_key(econf.learner.key,
                                                 kparser),
                                settings=settings,
                                learner=econf.learner,
                                parser=kparser)
    return [combine(p) for p in _core_parsers(klearner)]


_INTRA_PAIRS = list(itr.product(_LOCAL_LEARNERS, _INTRA_INTER_CONFIGS))


EVALUATIONS = concat_l([
    concat_l(_core_parsers(l) for l in _LOCAL_LEARNERS),
    concat_l(_mk_basic_intras(l, x) for l, x in _INTRA_PAIRS),
    #concat_l(_mk_sorc_intras(l, x) for l, x in _INTRA_PAIRS),
    #concat_l(_mk_dorc_intras(l, x) for l, x in _INTRA_PAIRS),
    concat_l(_mk_last_intras(l, x) for l, x in _INTRA_PAIRS),
    ])




"""Learners and decoders that are associated with each other.
The idea her is that if multiple decoders have a learner in
common, we will avoid rebuilding the model associated with
that learner.  For the most part we just want the cartesian
product, but some more sophisticated learners depend on the
their decoder, and cannot be shared
"""


GRAPH_DOCS = ['s2-league4-game1_07_stac_1396964826',
              's2-league4-game1_02_stac_1396964918',
              ]
"""Just the documents that you want to graph.
Set to None to graph everything
"""

DETAILED_EVALUATIONS = [e for e in EVALUATIONS if
                        'maxent' in e.learner.key and
                        ('mst' in e.parser.key or 'astar' in e.parser.key)
                        and 'jnt' in e.settings.key
                        and 'orc' not in e.settings.key]
"""
Any evalutions that we'd like full reports and graphs for.
You could just set this to EVALUATIONS, but this sort of
thing (mostly the graphs) takes time and space to build

HINT: set to empty list for no graphs whatsoever
"""

# -------------------------------------------------------------------------------
# settings for the standalone parser
# -------------------------------------------------------------------------------


"""
The configuration we would like to use for the standalone parser.
"""

DIALOGUE_ACT_LEARNER = Keyed('maxent', LogisticRegression())
"""
Classifier to use for dialogue acts
"""

TAGGER_JAR = 'lib/ark-tweet-nlp-0.3.2.jar'
"POS tagger jar file"


CORENLP_DIR = 'lib/stanford-corenlp-full-2013-06-20'
"CoreNLP directory"


CORENLP_SERVER_DIR = "lib/corenlp-server"
"corenlp-server directory (see http://github.com/kowey/corenlp-server)"


CORENLP_ADDRESS = "tcp://localhost:5900"
"0mq address to server"

# -------------------------------------------------------------------------------
# nothing to edit below :-)
# -------------------------------------------------------------------------------


def print_evaluations():
    """
    Print out the name of each evaluation in our config
    """
    for econf in EVALUATIONS:
        print(econf)
        print()
    print("\n".join(econf.key for econf in EVALUATIONS))

if __name__ == '__main__':
    print_evaluations()
