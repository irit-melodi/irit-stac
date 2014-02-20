# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Experimental sandbox (ignore)
"""

import pprint

import educe.stac
import stac.edu
from stac.util.args import\
    add_usual_input_args, add_usual_output_args,\
    read_corpus

NAME = 'tmp'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    add_usual_input_args(parser)
    parser.set_defaults(func=main)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    corpus = read_corpus(args)
    postags = educe.stac.postag.read_tags(corpus, args.corpus)
    for k in corpus:
        print k
        doc = corpus[k]
        contexts = stac.edu.Context.for_edus(corpus[k], postags[k])
        for edu in filter(educe.stac.is_edu, doc.units):
            print "EDU: ", edu
            ctx = contexts[edu]
            print "Turn: ", ctx.turn
            print "Dialogue: ", ctx.dialogue
            print "Tokens? ", map(str, ctx.tokens)
