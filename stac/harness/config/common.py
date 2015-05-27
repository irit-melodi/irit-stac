"""Commonly used configuration options"""

from collections import namedtuple
import six
# from attelo.decoding.astar import (AstarArgs,
#                                    AstarDecoder,
#                                    Heuristic,
#                                    RfcConstraint)
from attelo.decoding.baseline import (LastBaseline,
                                      LocalBaseline)
from attelo.harness.config import (EvaluationConfig,
                                   LearnerConfig,
                                   Keyed)
from attelo.learning.oracle import (AttachOracle, LabelOracle)
from attelo.parser.full import (JointPipeline,
                                PostlabelPipeline)


def combined_key(*variants):
    """return a key from a list of objects that have a
    `key` field each"""
    return '-'.join(v if isinstance(v, six.string_types) else v.key
                    for v in variants)


Settings = namedtuple('Settings',
                      ['key', 'intra', 'oracle', 'children'])
"""
Note that this is subclass of Keyed

The settings are used for config management only, for example,
if we want to filter in/out configurations that involve an
oracle.

Parameters
----------
intra: bool
    If this config uses intra/inter decoding

oracle: bool
    If parser should be considered oracle-based

children: container(Settings)
    Any nested settings (eg. if intra/inter, this would be the
    the settings of the intra and inter decoders)
"""

# ---------------------------------------------------------------------
# oracles
# ---------------------------------------------------------------------


def attach_learner_oracle():
    "return a keyed instance of the oracle (virtual) learner"
    return Keyed('oracle', AttachOracle())


def label_learner_oracle():
    "return a keyed instance of the oracle (virtual) learner"
    return Keyed('oracle', LabelOracle())


ORACLE = LearnerConfig(attach=attach_learner_oracle(),
                       label=label_learner_oracle())

# ---------------------------------------------------------------------
# baselines
# ---------------------------------------------------------------------


def decoder_last():
    "our instantiation of the mst decoder"
    return Keyed('last', LastBaseline())


def decoder_local(threshold):
    "our instantiation of the mst decoder"
    return Keyed('local', LocalBaseline(threshold, True))

# ---------------------------------------------------------------------
# pipelines
# ---------------------------------------------------------------------


def _core_settings(key, klearner):
    "settings for basic pipelines"
    return Settings(key=key,
                    intra=False,
                    oracle='oracle' in klearner.key,
                    children=None)


def mk_joint(klearner, kdecoder):
    "return a joint decoding parser config"
    settings = _core_settings('AD.L-jnt', klearner)
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
    settings = _core_settings('AD.L-pst', klearner)
    parser_key = combined_key(settings, kdecoder)
    key = combined_key(klearner, parser_key)
    parser = PostlabelPipeline(learner_attach=klearner.attach.payload,
                               learner_label=klearner.label.payload,
                               decoder=kdecoder.payload)
    return EvaluationConfig(key=key,
                            settings=settings,
                            learner=klearner,
                            parser=Keyed(parser_key, parser))
