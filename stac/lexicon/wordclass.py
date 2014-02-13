#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cheap and cheerful lexicon format used in the STAC project.
One entry per line, blanks ignored.  Each entry associates

 * some word with
 * some kind of category (we call this a "lexical class")
 * an optional part of speech (?? if unknown)
 * an optional subcategory blank if none

Here's an example with all four fields

    purchase:VBEchange:VB:receivable
    acquire:VBEchange:VB:receivable
    give:VBEchange:VB:givable

and one without the notion of subclass

    ought:modal:MD:
    except:negation:??:
"""

import codecs
from collections import defaultdict
import sys

class WordClass():
    def __init__(self, word, lex_class, pos, subclass):
        self.word      = word
        self.lex_class = lex_class
        self.pos       = pos      if pos !=     '??' else None
        self.subclass  = subclass if subclass != ''  else None

    @classmethod
    def read_entry(cls, s):
        """
        Return a WordClass given the string corresponding to an entry,
        or raise an exception if we can't parse it
        """
        fields = s.split(':')
        if len(fields) == 4:
            return cls(*fields)
        elif len(fields) == 3:
            fields.append(None)
            return cls(*fields)
        else:
            raise Exception("Sorry, I didn't understand this lexicon entry: %s" % s)

    @classmethod
    def read_entries(cls, xs):
        """
        Return a list of WordClass given an iterable of entry strings, eg. the
        stream for the lines in a file. Blank entries are ignored
        """
        return [ cls.read_entry(x.strip()) for x in xs if len(x.strip()) > 0 ]

    @classmethod
    def read_lexicon(cls, filename):
        """
        Return a list of WordClass given a filename corresponding to a lexicon
        we want to read
        """
        with codecs.open(filename, 'r', 'utf-8') as f:
            return cls.read_entries(f)

def class_dict(xs):
    """
    Given a list of WordClass, return a dictionary mapping lexical classes
    to words that belong in that class
    """
    d = defaultdict(dict)
    for x in xs:
        d[x.lex_class][x.word] = x.subclass
    return d

if __name__=="__main__":
    infile = sys.argv[1]
    d = class_dict(WordClass.read_lexicon(infile))
    for k in d:
        print "===== ", k, "====="
        print d[k]
