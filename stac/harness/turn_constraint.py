'''
Turn constraint: experimental constraint in which edges are filtered
out if they

* point backwards
* do not have the same speaker

We rely on there being a feature 'same_speaker'
'''
# pylint: disable=too-few-public-methods

import numpy as np

from attelo.harness.config import (Keyed)
from attelo.parser import (Parser)
from attelo.parser.pipeline import (Pipeline)

SAME_SPEAKER = 'same_speaker=True'
'boolean feature for if two EDUs share a speaker'


def turn_constraint_safe(dpack):
    '''
    Given a datapack, return the indices that correspond to edges
    that respect the turn constraint
    '''
    spkr_idx = dpack.vocab.index(SAME_SPEAKER)
    return [i for i, (edu1, edu2) in enumerate(dpack.pairings)
            if edu2.span() > edu1.span() or
            dpack.data[i, spkr_idx]]


def apply_turn_constraint(dpack, target):
    '''
    Select edges in the datapack that obey the turn constraint
    '''
    idxes = turn_constraint_safe(dpack)
    return dpack.selected(idxes), target[idxes]


# pylint: disable=invalid-name
class TC_LearnerWrapper(object):
    '''
    Placeholder to indicate we want to apply the turn constraint as a
    filter on the data before learning
    '''
    def __init__(self, learner):
        self._learner = learner
        self.can_predict_proba = self._learner.can_predict_proba

    @staticmethod
    def dzip(fun, dpacks, targets):
        """
        Copied from Parser
        """
        pairs = [fun(d, t) for d, t in zip(dpacks, targets)]
        return zip(*pairs)

    def important_features(self, top_n):
        """If possible, return a list of important features with
        their weights.

        Note: we assume here that the underlying learner supports
        this function
        """
        if hasattr(self._learner, 'important_features'):
            return self._learner.important_features(top_n)
        else:
            return None

    def important_features_multi(self, top_n):
        """If possible, return a dictionary mapping class indices
        to important features
        """
        if hasattr(self._learner, 'important_features_multi'):
            return self._learner.important_features_multi(top_n)
        else:
            return None

    def fit(self, dpacks, targets):
        "apply the turn constraint before learning"
        dpacks, targets = self.dzip(apply_turn_constraint, dpacks, targets)
        self._learner.fit(dpacks, targets)
        return self

    def transform(self, dpack):
        "pass through to inner learner"
        # no turn constraint here; we just wanted them for learning with
        return self._learner.transform(dpack)

    def predict_score(self, dpack):
        "pass through to inner learner"
        # no turn constraint here; we just wanted them for learning with
        return self._learner.predict_score(dpack)


class TC_Pruner(Parser):
    '''
    Trivial parser that should be run right before a decoder
    in a parsing pipeline
    '''
    def fit(self, dpacks, targets, cache=None):
        return self

    def transform(self, dpack):
        safe = turn_constraint_safe(dpack)
        unsafe = np.ones_like(dpack.graph.attach, dtype=bool)
        unsafe[safe] = False
        return self.deselect(dpack, unsafe)
# pylint: enable=invalid-name


def tc_decoder(kdecoder):
    "turn constrained version of any decoder constructor"
    steps = [('tc filter', TC_Pruner()),
             ('decode', kdecoder.payload)]
    return Keyed(key='tc-' + kdecoder.key,
                 payload=Pipeline(steps=steps))


def tc_learner(klearner):
    "turn constrained version of a learner"
    return Keyed(key='tc-' + klearner.key,
                 payload=TC_LearnerWrapper(klearner.payload))
