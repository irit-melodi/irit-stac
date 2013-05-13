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
import nltk.data

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def concat(xs):
    """
    Flatten a list of lists into a list.
    """
    return list(chain.from_iterable(xs))

def shift_span(start, sp):
    """
    Adjust a span's index to the right by adding the start value to it
    """
    return (sp[0] + start, sp[1] + start)

def span_text(text, sp):
    """
    Return the substring corresponding to a span
    """
    return text[sp[0]:sp[1]]

def segment_turn(orig_text):
    """
    Segment a piece of text corresponding to a STAC turn.
    This is a segment wrapper that chops off the turn number and
    emitter prefixes.
    """
    # hmm, interesting that the turn number is considered part of the text
    # for the annotations
    drop_turn_prefix = re.compile(r'^\d* : [^:]* : (.*)')
    match = drop_turn_prefix.match(orig_text)
    if match:
        text = match.group(1)
        post_process = lambda xs: [ shift_span(match.start(1), x) for x in xs ]
    else:
        text = orig_text
        post_process = lambda x: x
    return post_process(segment(text))

def segment(t):
    """
    Given a piece of text, return a list of text spans corresponding
    to segments of the text. The segments follow each other
    consecutively but there may be gaps (no guarantee of adjacency)
    """
    spans1 = tokenizer.span_tokenize(t)
    spans2 = concat([ resegment(t,s) for s in spans1 ])
    spans3 = fuse_segments(t,spans2)
    spans4 = ungap_segments(spans3)
    return spans4

def resegment(t,seg):
    """
    Apply hand-crafted segmentation rules. This is very crude: we hunt for
    entries that would correspond to the left and right hand sides of a split.
    For LHS splits, we also require a bit of separating punctuation between the
    two sides. We also allow an arbitrary number of LHS splits, whereas we only
    allow a single RHS split.
    """
    seg_start = seg[0]
    fragment  = span_text(t,seg)

    def sub_re(xs):
        return '(' + '|'.join(xs) + ')'

    def mk_group(name, *args):
        return '(?P<' + name + '>' + "".join(args) + ')'

    def get_span(m,group):
        return shift_span(seg_start,m.span(group))

    def from_match(m):
        lhs_span = get_span(m,'prefix')
        rhs_span = get_span(m,'suffix')
        return (lhs_span, rhs_span)

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
    match_lhs = lhs_re.match(fragment)

    # rhs things that trigger a split
    rhs_words  = [ 'sorry'
                 , 'thanks'
                 , 'haha', 'doh!'
                 #, r'[:;]-?[PD\(\)/\\]'
                 ]
    rhs       = mk_group('prefix', '.+\s')\
              + mk_group('suffix', sub_re(rhs_words), '.*$')
    rhs_re    = re.compile(rhs, flags=re.IGNORECASE)
    match_rhs = rhs_re.match(fragment)

    if match_lhs:
        (prefix, suffix)=from_match(match_lhs)
        return [prefix] + resegment(t,suffix)
    elif match_rhs:
        (prefix, suffix)=from_match(match_rhs)
        return [prefix, suffix]
    else:
        return [seg]

def fuse_segments(t,xs):
    """
    Given a list of adjacent segments, return a list of segments
    such that some things which have been wrongly broken into segments
    are fused back into one.
    """

    def bracket(s):
        return '(' + s + ')'
    def fuse(ys):
        return (ys[0][0],ys[-1][1])
    def txt(idx):
        return span_text(t,xs[idx])

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

    elif empty_re.match(txt(1)):
        fused = fuse(xs[0:2])
        return [fused] + fuse_segments(t,xs[2:])

    elif fusible_left_re.match(txt(1)):
        fused = fuse(xs[0:2])
        return [fused] + fuse_segments(t,xs[2:])

    elif fusible_right_re.match(txt(0)):
        head  = xs[0]
        rest  = fuse_segments(t,xs[1:])
        if len(rest) > 0:
            fused = fuse([head,rest[0]])
            return [fused] + rest[1:]
        else:
            return [head]

    else: # default case, just keep walking
        head  = xs[0]
        return [head] + fuse_segments(t,xs[1:])

def ungap_segments(xs):
    """
    Given a list of adjacent segments, anytime there is a gap between two segments
    L and R, absorb the gap into the right-hand segment
    """
    last=xs[0][1]
    if len(xs) > 1:
        ys=[xs[0]]
        for x in xs[1:]:
            if x[0] == last:
                ys.append((x[0],x[1]))
            if x[0] > last:
                ys.append((last,x[1]))
            elif x[0] < last:
                raise Exception("Segments unexpectedly out of order")
            last=x[1]
        return ys
    else:
        return xs
