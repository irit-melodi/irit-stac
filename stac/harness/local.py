"""
Paths and settings used for this experimental harness
In the future we may move this to a proper configuration file.
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

from __future__ import print_function
import itertools as itr

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
from attelo.decoding.baseline import (LocalBaseline)
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

from sklearn.linear_model import (LogisticRegression,
                                  Perceptron as SkPerceptron,
                                  PassiveAggressiveClassifier as
                                  SkPassiveAggressiveClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


from .attelo_cfg import (combined_key,
                         DecodingMode,
                         IntraStrategy,
                         Settings,
                         IntraFlag)
from .turn_constraint import (mk_tc_decoder,
                              tc_learner)

# PATHS

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

TEST_EVALUATION_KEY = None
# TEST_EVALUATION_KEY = 'maxent-AD.L_jnt-mst-root'
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

def decoder_local(settings):
    "our instantiation of the local baseline decoder"
    use_prob = settings.mode != DecodingMode.post_label
    return LocalBaseline(0.2, use_prob)


def decoder_mst_l(settings):
    "our instantiation of the mst decoder"
    use_prob = settings.mode != DecodingMode.post_label
    return MstDecoder(MstRootStrategy.leftmost,
                      use_prob)


def decoder_mst(settings):
    "our instantiation of the mst decoder"
    use_prob = settings.mode != DecodingMode.post_label
    return MstDecoder(MstRootStrategy.fake_root,
                      use_prob)


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

_LOCAL_LEARNERS = [
    LearnerConfig(attach=attach_learner_oracle(),
                  relate=label_learner_oracle()),
    LearnerConfig(attach=attach_learner_maxent(),
                  relate=label_learner_maxent()),
    LearnerConfig(attach=tc_learner(attach_learner_maxent()),
                  relate=tc_learner(label_learner_maxent())),
#    LearnerConfig(attach=attach_learner_maxent(),
#                  relate=label_learner_oracle()),
#    LearnerConfig(attach=attach_learner_rndforest(),
#                  relate=label_learner_rndforest()),
#    LearnerConfig(attach=Keyed('sk-perceptron',
#                               SkPerceptron(n_iter=20)),
#                  relate=learner_maxent()),
#    LearnerConfig(attach=Keyed('sk-pasagg',
#                               SkPassiveAggressiveClassifier(n_iter=20)),
#                  relate=learner_maxent()),
#    LearnerConfig(attach=Keyed('dp-perc',
#                               Perceptron(d, LOCAL_PERC_ARGS)),
#                  relate=learner_maxent()),
#    LearnerConfig(attach=Keyed('dp-pa',
#                               PassiveAggressive(d, LOCAL_PA_ARGS)),
#                  relate=learner_maxent()),
]
"""Straightforward attelo learner algorithms to try

It's up to you to choose values for the key field that can distinguish
between different configurations of your learners.

"""

_STRUCTURED_LEARNERS = [
#    lambda d: LearnerConfig(attach=Keyed('dp-struct-perc',
#                                         StructuredPerceptron(d, STRUCT_PERC_ARGS)),
#                            relate=learner_maxent()),
#    lambda d: LearnerConfig(attach=Keyed('dp-struct-pa',
#                                         StructuredPassiveAggressive(d, STRUCT_PA_ARGS)),
#                            relate=learner_maxent()),
]

"""Attelo learners that take decoders as arguments.
We assume that they cannot be used relation modelling
"""


_CORE_DECODERS = [
    Keyed('local', decoder_local),
    #Keyed('mst-left', decoder_mst_l),
    Keyed('mst-root', decoder_mst),
    Keyed('tc-local', mk_tc_decoder(decoder_local)),
    Keyed('tc-mst-root', mk_tc_decoder(decoder_mst)),
    #Keyed('astar', decoder_astar),
]

"""Attelo decoders to try in experiment

Don't forget that you can parameterise the decoders ::

    Keyed('astar-3-best' decoder_astar(nbest=3))
"""

SETTINGS_JOINT = Settings(key='AD.L_jnt',
                          mode=DecodingMode.joint,
                          intra=None)
SETTINGS_POST = Settings(key='AD.L_pst',
                         mode=DecodingMode.post_label,
                         intra=None)
SETTINGS_BASIC = SETTINGS_POST


_SETTINGS = [
    SETTINGS_JOINT,
    SETTINGS_POST,
    ]
"""Variants on global settings that would generally apply
over all decoder combos.

    Variant(key="post-label",
            name=None,
            flags=["--post-label"])

The name field is ignored here.

Note that not all global settings may be applicable to
all decoders.  For example, some learners may only
supoort '--post-label' decoding.

You may need to write some fancy logic when building the
EVALUATIONS list below in order to exclude these
possibilities
"""

# -------------------------------------------------------------------------------
# maybe less to edit below but still worth having a glance
# -------------------------------------------------------------------------------


HARNESS_NAME = 'irit-stac'


def _is_junk(klearner, kdecoder):
    """
    Any configuration for which this function returns True
    will be silently discarded
    """
    # intrasential head to head mode only works with mst for now
    intra_flag = kdecoder.settings.intra
    if kdecoder.key != 'mst':
        if (intra_flag is not None and
                intra_flag.strategy == IntraStrategy.heads):
            return True

    # no need for intra/inter oracle mode if the learner already
    # is an oracle
    if klearner.key == 'oracle' and intra_flag is not None:
        if intra_flag.intra_oracle or intra_flag.inter_oracle:
            return True

    # skip any config which tries to use a non-prob learner with
    if not klearner.attach.payload.can_predict_proba:
        if kdecoder.settings.mode != DecodingMode.post_label:
            return True

    return False


def _mk_intra(mk_parser, settings):
    """
    Return an intra/inter parser that would be wrapped
    around a core parser
    """
    strategy = settings.strategy
    def _inner(lcfg):
        "the actual parser factory"
        oracle_cfg = LearnerConfig(attach=attach_learner_oracle(),
                                   relate=label_learner_oracle())
        intra_cfg = oracle_cfg if settings.intra_oracle else lcfg
        inter_cfg = oracle_cfg if settings.inter_oracle else lcfg
        parsers = IntraInterPair(intra=mk_parser(intra_cfg),
                                 inter=mk_parser(inter_cfg))
        if strategy == IntraStrategy.only:
            return SentOnlyParser(parsers)
        elif strategy == IntraStrategy.heads:
            return HeadToHeadParser(parsers)
        elif strategy == IntraStrategy.soft:
            return SoftParser(parsers)
        else:
            raise ValueError("Unknown strategy: " + str(strategy))
    return _inner


def _mk_parser_config(kdecoder, settings):
    """construct a decoder from the settings

    :type k_decoder: Keyed(Settings -> Decoder)

    :rtype: ParserConfig
    """
    decoder_key = combined_key([settings, kdecoder])
    decoder = kdecoder.payload(settings)
    if settings.mode == DecodingMode.joint:
        mk_parser = lambda t: JointPipeline(learner_attach=t.attach.payload,
                                            learner_label=t.relate.payload,
                                            decoder=decoder)
    elif settings.mode == DecodingMode.post_label:
        mk_parser = lambda t: PostlabelPipeline(learner_attach=t.attach.payload,
                                                learner_label=t.relate.payload,
                                                decoder=decoder)
    if settings.intra is not None:
        mk_parser = _mk_intra(mk_parser, settings.intra)

    return ParserConfig(key=decoder_key,
                        decoder=decoder,
                        payload=mk_parser,
                        settings=settings)


def _mk_evaluations():
    """
    Some things we're trying to capture here:

    * some (fancy) learners are parameterised by decoders

    Suppose we have decoders (local, mst, astar) and the learners
    (maxent, struct-perceptron), the idea is that we would want
    to be able to generate the models:

        maxent (no parameterisation with decoders)
        struct-perceptron-mst
        struct-perceptron-astar

    * in addition to decoders, there are variants on global
      decoder settings that we want to expand out; however,
      we do not want to expand this for purposes of model
      learning

    * if a learner is parameterised by a decoder, it should
      only be tested by the decoder it is parameterised
      against (along with variants on its global settings)

        - struct-perceptron-mst with the mst decoder
        - struct-perceptron-astar with the astar decoder

    * ideally (not mission-critical) we want to report all the
      struct-perceptron-* learners as struct-percepntron; but
      it's easy to accidentally do the wrong thing, so let's not
      bother, eh?

    This would be so much easier with static typing

    :rtype [(Keyed(learner), KeyedDecoder)]
    """

    kparsers = [_mk_parser_config(d, s)
                for d, s in itr.product(_CORE_DECODERS, _SETTINGS)]
    kparsers = [k for k in kparsers if k is not None]

    # all learner/decoder pairs
    pairs = []
    pairs.extend(itr.product(_LOCAL_LEARNERS, kparsers))
    for klearner in _STRUCTURED_LEARNERS:
        pairs.extend((klearner(x.decoder), x) for x in kparsers)

    # boxing this up a little bit more conveniently
    configs = []
    for klearner, kparser_ in pairs:
        if _is_junk(klearner, kparser_):
            continue
        kparser = ParserConfig(key=kparser_.key,
                               decoder=kparser_.decoder,
                               payload=kparser_.payload(klearner),
                               settings=kparser_.settings)
        cfg = EvaluationConfig(key=combined_key([klearner, kparser]),
                               settings=kparser.settings,
                               learner=klearner,
                               parser=kparser)
        configs.append(cfg)
    return configs


EVALUATIONS = _mk_evaluations()
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
