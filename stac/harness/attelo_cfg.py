"""
Attelo command configuration
"""

from collections import namedtuple
from enum import Enum

import six

# pylint: disable=too-few-public-methods


def combined_key(variants):
    """return a key from a list of objects that have a
    `key` field each"""
    return '-'.join(v if isinstance(v, six.string_types) else v.key
                    for v in variants)


class DecodingMode(Enum):
    '''
    How to do decoding:

        * joint: predict attachment/relations together
        * post_label: predict attachment, then independently
                      predict relations on resulting graph
    '''
    joint = 1
    post_label = 2

class IntraStrategy(Enum):
    """
    Intrasentential decoding strategy

        * only: (mostly for debugging), do not attach
          sentences together at all
        * heads: attach heads of sentences to each other
        * soft: pass all nodes through to decoder, but
          assign intrasentential links from the sentence
          level decoder a probability of 1
    """
    only = 1
    heads = 2
    soft = 3


IntraFlag = namedtuple('IntraFlag',
                       ['strategy',
                        'intra_oracle',
                        'inter_oracle'])
"""
Sort of a virtual flag for enabling intrasentential decoding
"""


Settings = namedtuple('Settings',
                      ['key', 'intra', 'mode'])
"""
Global settings for decoding and for decoder construction
"""
