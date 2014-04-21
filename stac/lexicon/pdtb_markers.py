#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cheap and cheerful phrasal lexicon format used in the STAC project.
Maps sequences of multiword expressions to relations they mark

     as            ; explanation explanation* background
     as a result   ; result result*
     for example   ; elaboration
     if:then       ; conditional
     on the one hand:on the other hand

One entry per line.  Sometimes you have split expressions, like
"on the one hand X, on the other hand Y" (we model this by saying
that we are working with sequences of expressions, rather than
single expressions).  Phrases can be associated with 0 to N
relations (interpreted as disjunction; if `\wedge` appears (LaTeX
for ⋀), it is ignored)
"""

import codecs
from collections import defaultdict
import sys

class Multiword:
    """
    A sequence of tokens representing a multiword expression.
    """
    def __init__(self, words):
        self.words = [ w.lower() for w in words ]

    def __str__(self):
        return " ".join(self.words)

# TODO: We need to implement comparison/hashing functions so that objects with
# same contents are treated as the same. I miss Haskell
class Marker:
    """
    A marker here is a sort of template consisting of multiword expressions
    and holes, eg. "on the one hand, XXX, on the other hand YYY".  We
    represent this is as a sequence of Multiword
    """
    def __init__(self, exprs):
        self.exprs = exprs

    def __str__(self):
        return " ... ".join(map(str, self.exprs))

    def appears_in(self, words, sep='#####'):
        """
        Given a sequence of words, return True if this marker appears in
        that sequence.

        We use a *very* liberal defintion here. In particular, if the marker
        has more than component (on the one hand X, on the other hand Y),
        we merely check that all components appear without caring what order
        they appear in.

        Note that this abuses the Python string matching functionality,
        and assumes that the separator substring never appears in the
        tokens
        """
        sentence = sep.join(words).lower()
        exprs    = frozenset(sep.join(e.words) for e in self.exprs)
        return all(sentence.find(e) >= 0 for e in exprs)

    @classmethod
    def any_appears_in(cls, markers, words, sep='#####'):
        """
        Return True if any of the given markers appears in the word
        sequence.

        See `appears_in` for details.
        """
        sentence = sep.join(words).lower()
        for m in markers:
            exprs = frozenset(sep.join(e.words) for e in m.exprs)
            if all(sentence.find(e) >= 0 for e in exprs):
                return True
        return False


def read_entry(s):
    """
    Return a Marker and a set of relations
    """
    blacklist = frozenset(['\\wedge'])
    fields    = [ x.strip() for x in s.split(';') ]
    if len(fields) > 0 and len(fields) <= 2:
        subexprs = []
        for se in [ se.strip() for se in fields[0].split(':') ] :
            subexprs.append(Multiword(se.split()))
        exprs = Marker(subexprs)
        if len(fields) == 2:
            rels_ = fields[1].split()
        else:
            rels_ = []
        rels = frozenset(rels_) - blacklist
        return exprs, rels

    elif len(fields) == 1:
        fields.append(None)
    else:
        raise Exception("Sorry, I didn't understand this PDTB marker lexicon entry: %s" % s)

def read_entries(xs):
    """
    Return a dictionary mapping each relation to the set of markers that
    indicate the presence of that relation
    """
    d_ = defaultdict(list)
    for x_ in xs:
        x = x_.strip()
        if len(x) < 1: continue
        marker, rels = read_entry(x)
        for r in rels:
            d_[r].append(marker)
    return { k : frozenset(v) for k,v in d_.items() }

def read_lexicon(filename):
    """
    Return a list of WordClass given a filename corresponding to a lexicon
    we want to read
    """
    with codecs.open(filename, 'r', 'utf-8') as f:
        return read_entries(f)

if __name__=="__main__":
    infile = sys.argv[1]
    words  = sys.argv[2].split()
    lex    = read_lexicon(infile)
    rdict  = rel_to_markers(lex)
    for marker, rels  in lex:
        print marker, ' => ', ', '.join(rels)
    for k in rdict:
        print k
        for m in rdict[k]:
            print ' ', '[%s]' % m, m.appears_in(words)
