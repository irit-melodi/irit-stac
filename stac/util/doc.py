# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
Utilities for large-scale changes to educe documents,
for example, moving a chunk of text from one document
to another
"""

from collections import defaultdict
import copy

from educe.annotation import Unit, Span

from stac.util.glozz import\
    anno_id_from_tuple,\
    anno_author, anno_date, set_anno_date


def evil_set_id(anno, author, date):
    """
    This is a bit evil as it's using undocumented functionality
    from the educe.annotation.Standoff object
    """
    anno._anno_id = anno_id_from_tuple((author, date))
    anno.metadata['author'] = author
    anno.metadata['creation-date'] = str(date)


def evil_set_text(doc, text):
    """
    This is a bit evil as it's using undocumented functionality
    from the educe.annotation.Document object
    """
    doc._text = text


def shift_annotations(doc, offset):
    """
    Return a deep copy of a document such that all annotations
    have been shifted by an offset.

    If shifting right, we pad the document with whitespace
    to act as filler. If shifting left, we cut the text
    """
    def shift(anno):
        "Shift a single annotation"
        if offset != 0 and isinstance(anno, Unit):
            anno2 = copy.deepcopy(anno)
            anno2.span = anno.span.shift(offset)
            return anno2
        else:
            return copy.deepcopy(anno)

    if offset > 0:
        padding = " " * offset
        txt2 = padding + doc.text()
    else:
        start = 0 - offset
        txt2 = doc.text()[start:]
    doc2 = copy.copy(doc)
    evil_set_text(doc2, txt2)
    doc2.units = map(shift, doc.units)
    doc2.schemas = map(shift, doc.schemas)
    doc2.relations = map(shift, doc.relations)
    return doc2


def compute_renames(avoid, incoming):
    """
    Given two sets of documents, return a dictionary which would
    allow us to rename ids in `incoming` so that they do not
    overlap with those in `avoid`.

    :rtype `author -> date -> date`
    """
    dates = defaultdict(list)
    renames = defaultdict(dict)
    for doc1 in avoid.values():
        for anno in doc1.annotations():
            author = anno_author(anno)
            date = anno_date(anno)
            dates[author].append(date)
    min_dates = {k: min(v) for k, v in dates.items()}
    max_dates = {k: max(v) for k, v in dates.items()}
    for doc2 in incoming.values():
        for anno in doc2.annotations():
            author = anno_author(anno)
            old_date = anno_date(anno)
            if author in dates and old_date in dates[author] and\
               not (author in renames and old_date in renames[author]):
                if old_date < 0:
                    new_date = min_dates[author] - 1
                    min_dates[author] = new_date
                else:
                    new_date = max_dates[author] + 1
                    max_dates[author] = new_date
                dates[author].append(new_date)
                renames[author][old_date] = new_date
    return renames


def enclosing_span(spans):
    """
    Return a span that stretches from one end of a collection of spans
    to the other end.
    """
    if len(spans) < 1:
        raise ValueError("must have at least one span")

    return Span(min(x.char_start for x in spans),
                max(x.char_end for x in spans))


def narrow_to_span(doc, span):
    """
    Return a deep copy of a document with only the text and
    annotations that are within the span specified by portion.
    """
    def slice_annos(annos):
        "Return a copy of all annotations within a span"
        return [copy.copy(anno) for anno in annos
                if span.encloses(anno.text_span())]

    offset = 0 - span.char_start
    doc2 = copy.copy(doc)
    doc2.units = slice_annos(doc.units)
    doc2.schemas = slice_annos(doc.schemas)
    doc2.relations = slice_annos(doc.relations)
    doc2 = shift_annotations(doc2, offset)
    evil_set_text(doc2, doc.text()[span.char_start:span.char_end])
    return doc2


def rename_ids(renames, doc):
    """
    Return a deep copy of a document, with ids reassigned
    according to the renames dictionary
    """
    doc2 = copy.deepcopy(doc)
    for anno in doc2.annotations():
        author = anno_author(anno)
        date = anno_date(anno)
        if author in renames and date in renames[author]:
            new_date = renames[author][date]
            set_anno_date(anno, new_date)
            evil_set_id(anno, author, new_date)
    return doc2


def move_portion(renames, src_doc, tgt_doc, src_span, prepend=False):
    """
    Return a copy of the documents such that the src_span has been moved
    from source to target
    """
    snipped = narrow_to_span(src_doc, src_span)
    src_txt = snipped.text()
    tgt_txt = tgt_doc.text()
    if prepend and tgt_txt[0] == ' ':
        old_len = len(tgt_txt)
        tgt_txt = tgt_txt.lstrip()
        pad_len = old_len - len(tgt_txt)
        src_offset = 0
        tgt_offset = len(src_txt) - pad_len
    elif not prepend and src_txt[0] == ' ':
        tgt_txt = tgt_txt.rstrip()
        src_offset = len(tgt_txt)
        tgt_offset = 0

    # TODO: err, is this correctly shifting the schema and relation
    # pointers?
    snipped = shift_annotations(snipped, src_offset)
    snipped = rename_ids(renames, snipped)

    new_tgt_doc = shift_annotations(tgt_doc, tgt_offset)
    new_tgt_doc.units = new_tgt_doc.units + snipped.units
    new_tgt_doc.relations = new_tgt_doc.relations + snipped.relations
    new_tgt_doc.schemas = new_tgt_doc.schemas + snipped.schemas

    if prepend:
        if src_span != snipped.text_span():
            print src_span
            print snipped.text_span()
            raise Exception("Not yet implemented: prepending from other " +
                            "than whole doc: %s" % src_span)
        # tgt_doc is on the right
        evil_set_text(new_tgt_doc, src_txt + tgt_txt)
        return None, new_tgt_doc
    else:
        if src_span.char_start != 0:
            raise Exception("Not yet implemented: moving from other " +
                            "than document start: %s" % src_span)
        # tgt_doc is on the left
        evil_set_text(new_tgt_doc, tgt_txt + src_txt)
        leftover_src_span = Span(src_span.char_end, len(src_doc.text()))
        new_src_doc = narrow_to_span(src_doc, leftover_src_span)
        return new_src_doc, new_tgt_doc
