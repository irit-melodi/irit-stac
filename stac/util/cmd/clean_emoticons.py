# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Merge emoticon-only EDUs into preceding EDU (one-off cleanup)
"""

from __future__ import print_function
import collections
import copy

import educe.stac
from stac.edu import EnclosureGraph, sorted_first_widest

from stac.util.annotate import show_diff
from stac.util.glozz import\
    PseudoTimestamper, set_anno_author, set_anno_date,\
    anno_id_from_tuple
from stac.util.args import\
    add_usual_output_args,\
    get_output_dir, announce_output_dir
from stac.util.output import save_document


NAME = 'clean-emoticons'


class TimestampCache(object):
    """
    Generates and stores a unique timestamp entry for each turn id.

    The idea here is to ensure that timestamps from newly generated edus
    are the same across all documents in the same family.
    (family here is defined as same doc/subdoc)
    """

    def __init__(self):
        self.stamps = PseudoTimestamper()
        self.reset()

    def get(self, tid):
        """
        Return a timestamp for this turn id, either generating and
        caching (if unseen) or fetching from the cache
        """
        if tid not in self.cache:
            self.cache[tid] = self.stamps.next()
        return self.cache[tid]

    def reset(self):
        """
        Empty the cache (but maintain the timestamper state, so that
        different documents get different timestamps; the difference
        in timestamps is not mission-critical but potentially nice)
        """
        self.cache = {}


def custom_read_corpus(args, verbose=True):
    """
    Read the section of the corpus specified in the command line arguments.
    """
    is_interesting1 = educe.util.mk_is_interesting(args)
    args2 = copy.deepcopy(args)
    args2.stage = 'unannotated'
    args2.annotator = None
    is_interesting2 = educe.util.mk_is_interesting(args2)
    is_interesting = lambda x: is_interesting1(x) or is_interesting2(x)
    reader = educe.stac.Reader(args.corpus)
    anno_files = reader.filter(reader.files(), is_interesting)
    return reader.slurp(anno_files, verbose)


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    parser.add_argument('corpus', metavar='DIR', help='corpus dir')
    # don't allow stage control
    educe.util.add_corpus_filters(parser,
                                  fields=['doc', 'subdoc', 'annotator'])
    add_usual_output_args(parser)
    parser.set_defaults(func=main)


def is_just_emoticon(tokens):
    """
    Similar to the one in stac.features, but takes WrappedTokens
    """
    return len(tokens) == 1 and tokens[0].features["tag"] == 'E'


def has_links(doc, edu):
    """
    True if this edu is pointed to by any relations or included
    in any CDUs
    """
    return\
        any(x.source == edu or x.target == edu for x in doc.relations) or\
        any(edu in x.members for x in doc.schemas)


def sorted_turns(doc):
    """
    Turn annotations in a document, sorted by text span
    """
    return sorted_first_widest(filter(educe.stac.is_turn, doc.units))


def absorb_emoticon(doc, stamp, penult, last):
    """
    Given a timestamp, and two edus, @penult@ (the second to last edu
    in a turn annotation), and @last@ (an emoticon-only edu that follows it),
    absorb the latter into the former.

    This only mutates `penult` (and updates the timestamp generator), and
    does not return anything

    Note that we also have to update any relations/schemas in the document
    telling them to point to the annotation with the new id
    """
    old_id = penult.local_id()
    new_id = anno_id_from_tuple(("stacutil", stamp))
    penult.span = penult.text_span().merge(last.text_span())
    set_anno_date(penult, stamp)
    set_anno_author(penult, "stacutil")

    for rel in doc.relations:
        if rel.span.t1 == old_id:
            rel.span.t1 = new_id
            rel.source = penult
        if rel.span.t2 == old_id:
            rel.span.t2 = new_id
            rel.target = penult
    for schema in doc.schemas:
        if old_id in schema.units:
            schema.units = set(schema.units)
            schema.units.remove(old_id)
            schema.units.add(new_id)


def turns_with_final_emoticons(doc, tags):
    """
    Return a tuple of lists.

    Both lists contain the turns in a document that end with the
    pattern EDU emoticon-only-EDU.

    The first (main) list contains those that are not pointed to by any
    relations or schema. The second (warnings only) list contains those
    that have relations or schema pointing to them.

    The reason we distinguish between the two lists is that we don't
    want to touch those in the latter (out of conservatism, the idea
    of removing these from their relations, CDUs seems scary), but we
    want to know about them.
    """
    egraph = EnclosureGraph(doc, tags)
    affected_free_turns = []
    affected_linked_turns = []

    for turn in sorted_turns(doc):
        edus = sorted_first_widest(egraph.inside(turn))

        last_edu = edus[-1]
        if len(edus) > 1 and is_just_emoticon(egraph.inside(last_edu)):
            if has_links(doc, last_edu):
                affected_linked_turns.append(turn)
            else:
                affected_free_turns.append(turn)

    return affected_free_turns, affected_linked_turns


def merge_final_emoticons(tcache, turn_spans, doc, tags):
    """
    Given a timestamp cache and some text spans identifying
    turns with final emoticons in them, and a document:

    1. find the specified turns in the document
    2. absorb their emoticon EDUs into the one before it

    This modifies the document and does not return
    anything
    """
    egraph = EnclosureGraph(doc, tags)
    for turn in sorted_turns(doc):
        if turn.text_span() not in turn_spans:
            continue
        edus = sorted_first_widest(egraph.inside(turn))
        assert len(edus) > 1

        stamp = tcache.get(educe.stac.turn_id(turn))
        last_edu = edus[-1]
        penult_edu = edus[-2]
        absorb_emoticon(doc, stamp, penult_edu, last_edu)
        doc.units.remove(last_edu)


def family_banner(doc, subdoc, keys):
    """
    Header announcing the family we're working on
    """

    def show_member(k):
        "single key in the family"
        if k.annotator:
            return "%s/%s" % (k.annotator, k.stage)
        else:
            return k.stage

    fam = "%s [%s]" % (doc, subdoc)
    members = ", ".join(map(show_member, keys))

    return "========== %s =========== (%s)" % (fam, members)


def main(args):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    corpus = custom_read_corpus(args)
    postags = educe.stac.postag.read_tags(corpus, args.corpus)
    tcache = TimestampCache()
    output_dir = get_output_dir(args)

    families = collections.defaultdict(list)
    discourse_subcorpus = {}
    for k in corpus:
        fam = (k.doc, k.subdoc)
        families[fam].append(k)
        if k.stage == 'discourse':
            discourse_subcorpus[fam] = k

    for fam in sorted(families):
        print(family_banner(fam[0], fam[1], families[fam]))
        disc_k = discourse_subcorpus[fam]

        doc = corpus[disc_k]
        turns, warn_turns = turns_with_final_emoticons(doc, postags[disc_k])

        warnings = []
        if warn_turns:
            warnings.append("Note: These turns have emoticon-only EDUs that "
                            "I dare not touch because they either "
                            "participate in relations or CDUs: ")
            warnings.extend(" " + doc.text(x.text_span()) for x in warn_turns)
            warnings.append("If the "
                            "relations can be removed, or the CDUs reduced, "
                            "please do this by hand and re-run the script:")

        if not turns:
            warnings.append("Skipping %s (and related); no offending emoticons"
                            % disc_k)

        print("\n".join(warnings))

        if not turns:
            continue

        turn_spans = [x.text_span() for x in turns]
        for k in families[fam]:
            doc = copy.deepcopy(corpus[k])
            tags = postags[k]
            merge_final_emoticons(tcache, turn_spans, doc, tags)
            if k == discourse_subcorpus[fam]:
                for turn_span in turn_spans:
                    print(show_diff(corpus[k], doc, span=turn_span))
                    print()
            save_document(output_dir, k, doc)
        tcache.reset()
    announce_output_dir(output_dir)
