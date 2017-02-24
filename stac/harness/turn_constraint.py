"""Turn constraint: experimental constraint in which edges are filtered
out if they:
* point backwards or
* do not have the same speaker.

We rely on there being a feature 'same_speaker', one-hot-encoded as
'same_speaker=True'.
"""
# pylint: disable=too-few-public-methods

import numpy as np

from attelo.harness.config import (Keyed)
from attelo.parser import (Parser)
from attelo.parser.pipeline import (Pipeline)

SAME_SPEAKER = 'same_speaker=True'
'boolean feature for if two EDUs share a speaker'


def turn_constraint_safe(dpack):
    """Get the indices of edges that respect the turn constraint.

    Parameters
    ----------
    dpack : DataPack
        DataPack that contains the edges.

    Returns
    -------
    res : list of int
        Indices of selected edges.
    """
    spkr_idx = dpack.vocab.index(SAME_SPEAKER)
    return [i for i, (edu1, edu2) in enumerate(dpack.pairings)
            if edu2.span() > edu1.span() or
            dpack.data[i, spkr_idx]]


def apply_turn_constraint(dpack, target):
    """Select edges in the datapack that obey the turn constraint.

    Parameters
    ----------
    dpack : DataPack
        Original datapack.

    target : list of edge predictions
        Original list of edge predictions.

    Returns
    -------
    dpack_sel : DataPack
        Selected datapack.

    target_sel : list of edge predictions
        Selected list of edge predictions.
    """
    idxes = turn_constraint_safe(dpack)
    return dpack.selected(idxes), target[idxes]


# pylint: disable=invalid-name
class TC_LearnerWrapper(object):
    """Placeholder to indicate we want to apply the turn constraint as a
    filter on the data before learning.
    """

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

    def fit(self, dpacks, targets, nonfixed_pairs=None):
        """apply the turn constraint before learning"""
        tc_safe_pairs = [turn_constraint_safe(dpack) for dpack in dpacks]
        # restrict dpacks and targets to keep only tc safe edges
        dpacks = [dpack.selected(idxes) for dpack, idxes
                  in zip(dpacks, tc_safe_pairs)]
        targets = [target[idxes] for target, idxes
                   in zip(targets, tc_safe_pairs)]
        # get indices of nonfixed_pairs in tc_safe_pairs
        if nonfixed_pairs is not None:
            nonfixed_ix = [np.in1d(idxes, nf_pairs) for idxes, nf_pairs
                           in zip(tc_safe_pairs, nonfixed_pairs)]
            nonfixed_pairs = [np.where(nf_ix)[0] for nf_ix in nonfixed_ix]
        self._learner.fit(dpacks, targets, nonfixed_pairs=nonfixed_pairs)
        return self

    def transform(self, dpack, nonfixed_pairs=None):
        """pass through to inner learner"""
        # no turn constraint here; we just wanted them for learning with
        return self._learner.transform(dpack, nonfixed_pairs=nonfixed_pairs)

    def predict_score(self, dpack, nonfixed_pairs=None):
        """pass through to inner learner"""
        # no turn constraint here; we just wanted them for learning with
        return self._learner.predict_score(dpack, nonfixed_pairs=nonfixed_pairs)


class TC_Pruner(Parser):
    """Trivial parser that should be run right before a decoder in a
    parsing pipeline.
    """
    def fit(self, dpacks, targets, nonfixed_pairs=None, cache=None):
        return self

    def transform(self, dpack, nonfixed_pairs=None):
        return self.select(dpack, turn_constraint_safe(dpack))
# pylint: enable=invalid-name


def tc_decoder(kdecoder):
    "turn constrained version of any decoder constructor"
    steps = [('tc_filter', TC_Pruner()),
             ('decode', kdecoder.payload)]
    return Keyed(key='tc-' + kdecoder.key,
                 payload=Pipeline(steps=steps))


def tc_learner(klearner):
    "turn constrained version of a learner"
    return Keyed(key='tc-' + klearner.key,
                 payload=TC_LearnerWrapper(klearner.payload))
