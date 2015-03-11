"""
Attelo command configuration
"""

from collections import namedtuple

import six

# pylint: disable=too-few-public-methods


def combined_key(variants):
    """return a key from a list of objects that have a
    `key` field each"""
    return '-'.join(v if isinstance(v, six.string_types) else v.key
                    for v in variants)


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


KeyedDecoder = namedtuple('KeyedDecoder',
                          ['key',
                           'payload',
                           'settings'])
"""
A decoder and some decoder settings that together with it

Note that this is meant to be duck-type-compatible with
Keyed(Decoder)
"""


def _attelo_fold_args(lconf, fold):
    """
    Return flags for picking out the attelo fold file (and fold
    number), if relevant
    """
    if fold is None:
        return []
    else:
        return ["--fold", str(fold),
                "--fold-file", lconf.fold_file]
