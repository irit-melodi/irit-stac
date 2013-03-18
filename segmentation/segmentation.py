#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Eric Kow
# License: BSD3

"""
Helper functions for EDU segmentation
"""

from   itertools import chain
import re
import sys

from nltk.tokenize import sent_tokenize

def concat(xs):
    """
    Flatten a list of lists into a list.
    """
    return list(chain.from_iterable(xs))

def segment(t):
    """
    Given a piece of text, return a list of segments where each segment
    is an infix of the text.

    Note that this is currently a bit lossy wrt whitespace around the
    segments, so we can't guarantee that

         # no!
         "".join(segment(x)) == x

    But we can at least say

         delete_whitespace("".join(segments)) == delete_whitespace(x)

    Where delete_whitespace is a hypothetical function that does something
    like `s/\s//g`
    """
    segments1 = sent_tokenize(t)
    segments2 = concat(map(resegment, segments1))
    segments3 = fuse_segments(segments2)
    return segments3

def resegment(t):
    """
    Apply hand-crafted segmentation rules. This is very crude: we hunt for
    entries that would correspond to the left and right hand sides of a split.
    For LHS splits, we also require a bit of separating punctuation between the
    two sides. We also allow an arbitrary number of LHS splits, whereas we only
    allow a single RHS split.

    Possible invariant:

        concat(resegment(t)) == resegment(t)
    """
    def sub_re(xs):
        return '(' + '|'.join(xs) + ')'

    def mk_group(name, *args):
        return '(?P<' + name + '>' + "".join(args) + ')'

    def from_match(m):
        return (m.group('prefix').rstrip(), m.group('suffix').lstrip())

    # lhs things that trigger a split
    lhs_words = [ 'yeah', 'sure', 'ok', 'okay', 'no(pe)?'
                , 'right', 'well'
                , '(sorry|apologies)'
                , 'tch', '[ao]h well', 'uh oh'
                ]
    lhs_punct = [ ',', '\.\.\.', '!', ' -' ]
    lhs       = mk_group('prefix', r'\s*', sub_re(lhs_words), sub_re(lhs_punct))\
              + mk_group('suffix', '.+$')
    lhs_re    = re.compile(lhs, flags=re.IGNORECASE)
    match_lhs = lhs_re.match(t)

    # rhs things that trigger a split
    rhs_words  = [ 'sorry'
                 , 'thanks'
                 , 'haha', 'doh!'
                 , r'[:;]-?[PD\(\)/\\]'
                 ]
    rhs       = mk_group('prefix', '.+\s')\
              + mk_group('suffix', sub_re(rhs_words), '.*$')
    rhs_re    = re.compile(rhs, flags=re.IGNORECASE)
    match_rhs = rhs_re.match(t)

    if match_lhs:
        (prefix, suffix)=from_match(match_lhs)
        return [prefix] + resegment(suffix)
    elif match_rhs:
        (prefix, suffix)=from_match(match_rhs)
        return [prefix, suffix]
    else:
        return [t]

def fuse_segments(xs):
    """
    Given a list of segments, return a list of segments such that
    some things which have been wrongly broken into segments are
    fused back into one.
    """

    def bracket(s):
        return '(' + s + ')'
    def fuse(ys):
        return " ".join(ys)

    empty          = r'((^$)|^[\?\.!]*$)'
    empty_re       = re.compile(empty)

    resource_alloc = r'(.* gets \d* (wheat|wood|clay|sheep|ore)[,\.])'
    interjections  = [ r'a+r*g*h+'
                     , 'bah'
                     , 'eww'
                     , 'huh'
                     , 'oh' # notice this cancels out the 'oh' split above
                     , 'woo'
                     , 'wow'
                     ]
    interjection   = r'(^' + '|'.join(map(bracket, interjections)) + '$)'

    # should be fused with its left neighbour
    fusible_left     = [r'^XXXXXXXXXXXXXX$']
    fusible_left_re  = re.compile('|'.join(fusible_left), flags=re.IGNORECASE)

    # should be fused with its right neighbour
    fusible_right    = [resource_alloc, interjection]
    fusible_right_re = re.compile('|'.join(fusible_right), flags=re.IGNORECASE)

    if len(xs) < 2:
        return xs

    elif empty_re.match(xs[1]): # no space between fused segments
        fused = "".join(xs[0:2])
        return [fused] + fuse_segments(xs[2:])

    elif fusible_left_re.match(xs[1]):
        fused = fuse(xs[0:2])
        return [fused] + fuse_segments(xs[2:])

    elif fusible_right_re.match(xs[0]):
        head  = xs[0]
        rest  = fuse_segments(xs[1:])
        if len(rest) > 0:
            fused = fuse([head,rest[0]])
            return [fused] + rest[1:]
        else:
            return [head]

    else: # default case, just keep walking
        head  = xs[0]
        return [head] + fuse_segments(xs[1:])
