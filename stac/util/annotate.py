# Author: Eric Kow
# License: BSD3

"""
Readable text dumps of educe annotations.

The idea here is to dump the text to screen, and use some
informal text markup to show annotations over the text.
There's a limit to how much we can display, but just
breaking things up into paragraphs and [segments] seems to
go a long way.
"""

import copy
import itertools
import textwrap

import educe.stac

import stac.edu

DEFAULT_INSERTS = {'Turn': ('\n', ''),
                   'Dialogue': ('\n', ''),
                   'Segment': ('[', ']')}


def rough_type(anno):
    """
    Simplify STAC annotation types
    """
    if anno.type == 'Segment' or educe.stac.is_edu(anno):
        return 'Segment'
    else:
        return anno.type


def annotate(txt, annotations, inserts=None):
    """
    Decorate a text with arbitrary bracket symbols, as a visual
    guide to the annotations on that text. For example, in a
    chat corpus, you might use newlines to indicate turn
    boundaries and square brackets for segments.

    :param inserts
    :type  inserts a dictionary from annotation type to pair of
           its opening/closing bracket

    FIXME: this needs to become a standard educe utility,
    maybe as part of the educe.annotation layer?
    """
    inserts = inserts or DEFAULT_INSERTS
    if not annotations:
        return txt

    def is_visible(anno):
        """
        Is this annotation one we intend to display?
        """
        return rough_type(anno) in inserts

    def add_endpoints(endpoints, buf, pos):
        """
        Insert any pending closing annotations (eg. right bracket)
        into the text
        """
        endpoints2 = []
        buf2 = buf
        for pos2, rparen in endpoints:
            if pos == pos2:
                buf2 = buf2 + rparen
            else:
                endpoints2.append((pos2, rparen))
        return endpoints2, buf2

    s_annos = stac.edu.sorted_first_widest(filter(is_visible, annotations))
    endpoints = []
    buf = ""
    for i in range(0, len(txt)):
        char = txt[i]
        endpoints, buf = add_endpoints(endpoints, buf, i)
        while s_annos:
            nxt = s_annos[0]
            span = nxt.text_span()
            if span.char_start == i:
                lparen, rparen = inserts[rough_type(nxt)]
                buf = buf + lparen
                endpoints.insert(0, (span.char_end, rparen))  # lifo
                del s_annos[0]
            else:
                break
        buf = buf + char

    _, buf = add_endpoints(endpoints, buf, len(txt))
    return buf


# ---------------------------------------------------------------------
# differences
# ---------------------------------------------------------------------


def _concat(iters):
    """
    Flatten a list of lists into a list.
    """
    return list(itertools.chain.from_iterable(iters))


def reflow(text, width=40):
    """
    Wrap some text, at the same time ensuring that all original
    linebreaks are still in place
    """

    def wrap(line):
        """
        Wrap a single line of text. If empty, return a blank line
        rather that no lines at all
        """
        return textwrap.wrap(line, width) or ['']

    return _concat(wrap(t) for t in text.split("\n"))


def annotate_doc(doc, span=None):
    """
    Pretty print an educe document and its annotations.

    See the lower-level `annotate` for more details
    """
    if span:
        units_ = [u for u in doc.units if span.encloses(u.span)]
        units = copy.deepcopy(units_)
        for unit in units:
            unit.span = unit.span.relative(span)
    else:
        units = doc.units
    return annotate(doc.text(span), units).strip()


def show_diff(doc_before, doc_after, span=None):
    """
    Display two educe documents (presumably two versions of the "same")
    side by side
    """
    lines_before = reflow(annotate_doc(doc_before, span))
    lines_after = reflow(annotate_doc(doc_after, span))
    pairs = itertools.izip_longest(lines_before, lines_after, fillvalue='')
    return "\n".join("%-40s | %-40s" % p for p in pairs)
