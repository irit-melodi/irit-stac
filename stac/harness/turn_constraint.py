'''
Turn constraint: experimental constraint in which edges are filtered
out if they

* point backwards
* do not have the same speaker

We rely on there being a feature 'same_speaker'
'''

SAME_SPEAKER = 'same_speaker=True'
'boolean feature for if two EDUs share a speaker'


def apply_turn_constraint(vocab, dpack):
    '''
    Select edges in the datapack that obey the turn constraint
    '''
    spkr_idx = vocab.index(SAME_SPEAKER)
    idxes = [i for i, (edu1, edu2) in enumerate(dpack.pairings)
             if edu2.span() > edu1.span()
             or dpack.data[i, spkr_idx]]
    return dpack.selected(idxes)
