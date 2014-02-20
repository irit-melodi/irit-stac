#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Eric Kow
# License: BSD3

import itertools
from nltk.metrics import precision, recall, f_measure

class Score:
    """
    Precision/recall type scores for a given data set.

    This class is really just about holding on to sets of things
    The actual maths is handled by NLTK.
    """
    def __init__(self, reference, test):
        self._reference = reference
        self._test      = test
        self._inter     = reference & test

        missing  = sorted(list(reference - test))
        spurious = sorted(list(test - reference))
        miss_spur = list(itertools.izip_longest(missing,spurious,fillvalue=None))

        self._missing  = [x for x,_ in miss_spur ]
        self._spurious = [y for _,y in miss_spur ]

    def precision(self):
        return precision(self._reference, self._test)

    def recall(self):
        return recall(self._reference, self._test)

    def f_measure(self):
        return f_measure(self._reference, self._test)

    def shared(self):
        return self._inter

    def missing(self):
        return self._missing

    def spurious(self):
        return self._spurious

def banner(t):
    return "\n".join([ "------------------------------------------------------------"
                     , t
                     , "------------------------------------------------------------"
                     , ""
                     ])

def show_pair(k, score):
    columns = list(k) + [score]
    return "\t".join([str(c) for c in columns])

def show_multi(k, score):
    # put score in second column when we have multiple authors for easier
    # post-processing
    #
    # yeah, the inconsistency is a bit awkward but in the multi-document case,
    # the idea is that the author list is really just an FYI, whereas in the
    # pair case it's a fundamental part of the key
    kl      = list(k)
    columns = [kl[0], score, "(%s)" % " ".join(k[1:])]
    return "\t".join([str(c) for c in columns])
