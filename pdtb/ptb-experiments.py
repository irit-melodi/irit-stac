import argparse

import nltk.corpus
from nltk.corpus.util   import LazyCorpusLoader
from nltk.corpus.reader import BracketParseCorpusReader
from nltk.tag.simplify  import simplify_wsj_tag

import educe.pdtb as pdtb

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

arg_parser = argparse.ArgumentParser(description='Playing around with reading the PTB')
arg_parser.add_argument('corpus', metavar='DIR',
                        help='Input directory')
args = arg_parser.parse_args()

#reader = BracketParseCorpusReader(args.corpus, r'../wsj_.*\.mrg',
#                                  tag_mapping_function=simplify_wsj_tag, encoding='ascii')

reader     = pdtb.Reader(args.corpus)
anno_files = reader.files()
corpus     = reader.slurp_subcorpus(anno_files, verbose=True)
for k in sorted(corpus):
    print "----- %s ------" % k.doc
    for r in corpus[k]:
        print unicode(r).encode('utf-8')
        print
