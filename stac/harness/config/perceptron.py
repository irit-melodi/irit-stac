"""Configuration helpers for using perceptron based learners
"""

import numpy as np
from sklearn import linear_model as sk

from attelo.harness.config import (Keyed)

from attelo.learning.perceptron import (Perceptron,
                                        PerceptronArgs,
                                        PassiveAggressive,
                                        StructuredPerceptron,
                                        StructuredPassiveAggressive)
from attelo.learning.local import (SklearnAttachClassifier,
                                   SklearnLabelClassifier)


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

# ---------------------------------------------------------------------
# scikit
# ---------------------------------------------------------------------


def attach_learner_perc():
    "return a keyed instance of perceptron learner"
    learner = sk.Perceptron(n_iter=LOCAL_PERC_ARGS.iterations)
    return Keyed('perc', SklearnAttachClassifier(learner))


def label_learner_perc():
    "return a keyed instance of perceptron learner"
    learner = sk.Perceptron(n_iter=LOCAL_PERC_ARGS.iterations)
    return Keyed('perc', SklearnLabelClassifier(learner))


def attach_learner_pa():
    "return a keyed instance of passive aggressive learner"
    learner = sk.PassiveAggressiveClassifier(n_iter=LOCAL_PA_ARGS.iterations)
    return Keyed('pa', SklearnAttachClassifier(learner))


def label_learner_pa():
    "return a keyed instance of passive aggressive learner"
    learner = sk.PassiveAggressiveClassifier(n_iter=LOCAL_PA_ARGS.iterations)
    return Keyed('pa', SklearnLabelClassifier(learner))


# ---------------------------------------------------------------------
# dp
# ---------------------------------------------------------------------

def attach_learner_dp_perc():
    "return a keyed instance of perceptron learner"
    return Keyed('dp-perc',
                 SklearnAttachClassifier(Perceptron(LOCAL_PERC_ARGS)))


def label_learner_dp_perc():
    "return a keyed instance of perceptron learner"
    return Keyed('dp-perc',
                 SklearnLabelClassifier(Perceptron(LOCAL_PERC_ARGS)))


def attach_learner_dp_pa():
    "return a keyed instance of passive aggressive learner"
    return Keyed('dp-pa',
                 SklearnAttachClassifier(PassiveAggressive(LOCAL_PA_ARGS)))


def label_learner_dp_pa():
    "return a keyed instance of passive aggressive learner"
    return Keyed('dp-pa',
                 SklearnLabelClassifier(PassiveAggressive(LOCAL_PA_ARGS)))


def attach_learner_dp_struct_perc(decoder):
    "structured perceptron learning"
    learner = StructuredPerceptron(decoder, STRUCT_PERC_ARGS)
    return Keyed('dp-struct-perc', learner)


def attach_learner_dp_struct_pa(decoder):
    "structured passive-aggressive learning"
    learner = StructuredPassiveAggressive(decoder, STRUCT_PA_ARGS)
    return Keyed('dp-struct-pa', learner)
