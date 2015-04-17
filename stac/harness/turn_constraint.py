'''
Turn constraint: experimental constraint in which edges are filtered
out if they

* point backwards
* do not have the same speaker

We rely on there being a feature 'same_speaker'
'''
# pylint: disable=too-few-public-methods

from attelo.harness.config import (Keyed, LearnerConfig)
from attelo.decoding import (Decoder)


SAME_SPEAKER = 'same_speaker=True'
'boolean feature for if two EDUs share a speaker'


def apply_turn_constraint(dpack):
    '''
    Select edges in the datapack that obey the turn constraint
    '''
    spkr_idx = dpack.vocab.index(SAME_SPEAKER)
    idxes = [i for i, (edu1, edu2) in enumerate(dpack.pairings)
             if edu2.span() > edu1.span()
             or dpack.data[i, spkr_idx]]
    return dpack.selected(idxes)


# pylint: disable=invalid-name
class TC_LearnerConfig(LearnerConfig):
    '''
    Placeholder to indicate we want to apply the turn constraint as a
    filter on the data before learning
    '''
    def __new__(cls, attach, relate):
        attach = Keyed('tc_' + attach.key, attach.payload)
        relate = Keyed('tc_' + relate.key, relate.payload)
        return super(TC_LearnerConfig, cls).__new__(cls, attach, relate)


class TC_Decoder(Decoder):
    '''
    Placeholder to indicate we want to apply the turn constraint as a
    filter on the data before decoding
    '''
    def __init__(self, decoder):
        self._decoder = decoder
        self._whitelist = None

    def set_mpack(self, mpack):
        self._whitelist = set()
        for dpack in mpack.values():
            dpack = apply_turn_constraint(dpack)
            self._whitelist |= set(dpack.pairings)

    def decode(self, lpack):
        idxes = [i for i, row in enumerate(lpack.pairings)
                 if row in self._whitelist]
        lpack = lpack.selected(idxes)
        return self._decoder.decode(lpack)
# pylint: enable=invalid-name
