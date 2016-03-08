"""Split annotated file into two separate files for units and discourse.

"""

from __future__ import print_function

import argparse
import copy
from glob import glob
import itertools
import os
import sys

import educe.glozz
from educe.annotation import (Relation, RelSpan, Schema, Span)
from educe.stac.annotation import (addressees, DIALOGUE_ACTS, is_cdu, is_edu,
                                   is_preference, is_resource,
                                   is_relation_instance, is_turn)
from educe.stac.corpus import write_annotation_file


DIALOGUE_ACTS = DIALOGUE_ACTS + ['Strategic_comment']
# copied from educe.stac.edit.cmd.split_edu
# pylint: disable=fixme
_SPLIT_PREFIX = 'FIXME:'
# pylint: enable=fixme

def is_empty_dialogue_act(anno):
    """Return True if anno is an empty dialogue act.

    This is defined as:
    - having span length 0 or
    - no addressee and no surface act.

    Parameters
    ----------
    anno : Annotation
        Annotation to be tested

    Returns
    -------
    res : boolean
        True if `anno` is an empty dialogue act.
    """
    return (is_edu(anno) and
            anno.type in DIALOGUE_ACTS and
            addressees(anno) is None and
            (anno.features.get('Surface_act') == 'Please choose...'))
    

def fix_likely_annotation_errors(anno_doc, verbose=1):
    """Fix a document for likely annotation errors due to glozz UX.

    Likely errors are currently defined as:
    - units of span length 0 (delete),
    - empty dialogue acts (delete),
    - schemas with no member (delete),
    - overflowing units (fix span).

    Parameters
    ----------
    anno_doc : GlozzDocument
        Document to filter
    verbose : int
        Verbosity level

    Returns
    -------
    anno_doc : GlozzDocument
        Same document but filtered.
    """
    # units
    anno_units_err = [
        x for x in anno_doc.units
        if (x.span.char_start == x.span.char_end or
            (is_empty_dialogue_act(x) and
             any(y.encloses(x) for y in anno_doc.units
                 if y.text_span() != x.text_span() and is_edu(y))))
    ]
    # schemas
    anno_schms_err = [
        x for x in anno_doc.schemas
        if not x.members
    ]
    # relations
    # TODO
    anno_relas_err = []

    # warn about the ignored annotations
    if verbose:
        if anno_units_err or anno_schms_err or anno_relas_err:
            print('Likely errors due to glozz UX')
            print('-----------------------------')
        if anno_units_err:
            print('|-> Units')
            print('\n'.join('  [ ] {}'.format(str(x))
                            for x in anno_units_err))
        if anno_schms_err:
            print('|-> Schemas')
            print('\n'.join('  [ ] {}'.format(str(x))
                            for x in anno_schms_err))
        if anno_relas_err:
            print('|-> Relations')
            print('\n'.join('  [ ] {}'.format(str(x))
                            for x in anno_relas_err))

    # remove detected errors
    anno_units_err = set(anno_units_err)
    anno_doc.units = [x for x in anno_doc.units
                      if x not in anno_units_err]
    anno_schms_err = set(anno_schms_err)
    anno_doc.schemas = [x for x in anno_doc.schemas
                        if x not in anno_schms_err]
    anno_relas_err = set(anno_relas_err)
    anno_doc.relations = [x for x in anno_doc.relations
                          if x not in anno_relas_err]

    # fix span of units that overflow from their turn
    turns = [x for x in anno_doc.units if is_turn(x)]
    edus = [x for x in anno_doc.units if is_edu(x)]
    for edu in edus:
        enclosing_turns = [x for x in turns if x.encloses(edu)]
        if len(enclosing_turns) == 1:
            continue

        overlapping_turns = [x for x in turns if x.overlaps(edu)]
        if len(overlapping_turns) != 1:
            raise ValueError('No unique overlapping turn for {}'.format(edu))
        turn = overlapping_turns[0]
        if turn.overlaps(edu) != edu.text_span():
            edu.span = turn.overlaps(edu)
            if verbose:
                print('Fix span of overflowing unit: {}'.format(edu))

    return anno_doc


def approximate_cover(elts, tgt):
    """Returns True if elts covers tgt's span.

    This is approximate because we only check that:
    * the first and last elements respectively begin and end at the
      extremities of tgt.span,
    * consecutive elements don't overlap.

    Because of the second item, we assume that elts has been sorted
    by span.

    Parameters
    ----------
    elts : sorted list of Annotation
        Sequence of elements
    tgt : Annotation
        Target annotation

    Returns
    -------
    res : boolean
        True if elts approximately cover tgt.span
    """
    span_seq = Span(elts[0].span.char_start,
                    elts[-1].span.char_end)
    res = (span_eq(span_seq, tgt.text_span(), eps=1) and
           all(elt_cur.overlaps(elt_nxt) is None
               for elt_cur, elt_nxt
               in zip(elts[:-1], elts[1:])))
    return res


def span_eq(span_a, span_b, eps=0):
    """Span equality between `span_a` and `span_b`.

    Parameters
    ----------
    span_a : Span
        First annotation span
    span_b : Span
        Second annotation span
    eps : int, default 0
        Authorized margin to match annotation spans: 0 for strict matching,
        1 to include off-by-one etc.

    Returns
    -------
    res : boolean
        True if both annotation spans are considered to match.
    """
    return (abs(span_a.char_start - span_b.char_start) <= eps and
            abs(span_a.char_end - span_b.char_end) <= eps)


def infer_resegmentation(unanno_doc, anno_doc, verbose=0):
    """Infer resegmentation of EDUs.

    Parameters
    ----------
    anno_doc : GlozzDocument
        Document to filter
    verbose : int
        Verbosity level

    Returns
    -------
    anno_doc : GlozzDocument
        Filtered document, where the support of relations and schemas
        has been rewritten.
    """
    anno_map = dict()
    cautious_map = dict()
    new_cdus = []

    turns = [x for x in unanno_doc.units if is_turn(x)]
    for turn in turns:
        # `unannotated` was the starting point for the annotation process
        u_edus = [x for x in unanno_doc.units
                  if is_edu(x) and turn.span.encloses(x.span)]
        u_ids = set(x.local_id() for x in u_edus)

        # `annotated` is the result of the annotation process
        # find conflicts, as pair-wise overlaps between annotations
        # from `annotated`
        a_edus = [x for x in anno_doc.units
                  if is_edu(x) and turn.span.encloses(x.span)]
        # 1. map duplicate segments to their equivalent with dialogue act
        # annotation
        dup_items = [(elt_a, elt_b) for elt_a, elt_b
                     in itertools.combinations(
                         sorted(a_edus, key=lambda x: (
                             x.type in DIALOGUE_ACTS, x.local_id())),
                         2)
                     if (span_eq(elt_a.text_span(), elt_b.text_span(),
                                 eps=1) and
                         elt_a.type not in DIALOGUE_ACTS and
                         elt_b.type in DIALOGUE_ACTS)]
        anno_map.update(dup_items)
        # (locally) update the list of EDUs in anno_doc, so conflicts
        # are not computed on trivially mapped segments
        a_edus = [x for x in a_edus if x not in anno_map]

        # 2. list conflicts, then whitelist them progressively
        # NB: we sort EDUs in reverse using their local_ids, so that
        # conflict pairs are of the form (stac*, skar*) ; this is
        # admittedly a cheap, ad-hoc, trick to simulate an ordering
        # such that annotations already present in unannotated < annotations
        # introduced in annotated
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b
                        in itertools.combinations(
                            sorted(a_edus, key=lambda x: (
                                x.type in DIALOGUE_ACTS, x.local_id())),
                            2)
                        if elt_a.overlaps(elt_b)]

        # * Two cases are very close: EDU merges, and CDUs
        rels_support = set(anno_map.get(x, x)
                           for rel in anno_doc.relations
                           for x in [rel.source, rel.target])
        edu_merges = []  # list of (list of elt_a, elt_b)
        cdu_guess = []  # list of (list of elt_a, elt_b)
        for elt_b, pairs in itertools.groupby(pw_conflicts,
                                              key=lambda x: x[1]):
            sorted_a = sorted((y[0] for y in pairs),
                              key=lambda z: z.text_span())
            span_seq_a = Span(sorted_a[0].text_span().char_start,
                              sorted_a[-1].text_span().char_end)

            # we approximately check that the sequence of EDUs elts_a
            # fully covers the span of elt_b, from start to end, with
            # no overlap or that the whole sequence is enclosed in
            # the annotation from `annotated` (this happens when some but
            # not all of the merged EDUs have been deleted)
            if ((approximate_cover(sorted_a, elt_b) or
                 elt_b.text_span().encloses(span_seq_a))):
                # then, it is either an EDU merge or a CDU ;
                # if any element of the sequence supports a relation,
                # we take this as indicating a CDU
                if any(y in rels_support for y in sorted_a):
                    # broadcast type, features, metadata to the segments
                    for elt_a in sorted_a:
                        elt_a.type = _SPLIT_PREFIX + elt_b.type
                        elt_a.features = elt_b.features
                        elt_a.metadata = elt_b.metadata
                    # transform elt_b into a CDU
                    sch_relid = elt_b.local_id()
                    sch_units = set(y.local_id() for y in sorted_a)
                    sch_relas = set()
                    sch_schms = set()
                    sch_stype = 'Complex_discourse_unit'
                    sch_feats = elt_b.features
                    sch_metad = elt_b.metadata
                    new_cdu = Schema(sch_relid, sch_units, sch_relas,
                                     sch_schms, sch_stype, sch_feats,
                                     metadata=sch_metad)
                    new_cdus.append(new_cdu)
                    # map former (bad) segment to its proper CDU version
                    anno_map[elt_b] = new_cdu
                    cdu_guess.append((sorted_a, elt_b))
                    if verbose > 1:
                        print('CDU {}\nwas {}, from\n  {}'.format(
                            new_cdu, elt_b,
                            '\n  '.join(str(z) for z in sorted_a)))
                elif all(elt_a.local_id() in u_ids for elt_a in sorted_a):
                    edu_merges.append((sorted_a, elt_b))
                    if verbose > 1:
                        print('EDU merge {} from\n  {}'.format(
                            elt_b, '\n  '.join(str(z) for z in sorted_a)))
                else:
                    err_msg = 'Weird approximate cover:\n{}\n{}'
                    raise ValueError(err_msg.format(
                        ', '.join(str(y) for y in sorted_a),
                        elt_b
                    ))
        # map each of the segments to its CDU, so these pairs can be
        # removed from the list of conflicts later
        cdu_map = dict()
        for elts_a, elt_b in cdu_guess:
            map_items = [(elt_a, elt_b) for elt_a in elts_a]
            cdu_map.update(map_items)
            cautious_map.update(map_items)
        # map each of the merged segments to the new, bigger EDU + mark
        for elts_a, elt_b in edu_merges:
            map_items = [(elt_a, elt_b) for elt_a in elts_a]
            anno_map.update(map_items)
            cautious_map.update(map_items)
        # update list of conflicts: remove pairs that contain a segment
        # and its merged EDU, or a segment and its enclosing CDU
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                        if (anno_map.get(elt_a, elt_a) != elt_b and
                            cdu_map.get(elt_a, elt_a) != elt_b)]

        # * EDU splits
        edu_splits = dict()  # elt_a -> list of elt_b
        for elt_a, pairs in itertools.groupby(pw_conflicts,
                                              key=lambda x: x[0]):
            sorted_b = sorted((y[1] for y in pairs), key=lambda z: z.span)
            # we approximately check that the sequence of new EDUs
            # fully covers the span of elt_a, from start to end, with
            # no overlap
            if ((elt_a.local_id() in u_ids and
                 approximate_cover(sorted_b, elt_a))):
                edu_splits[elt_a] = sorted_b
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                        if elt_a not in set(edu_splits.keys())]
        # map the split segment to the first of the resulting EDUs + mark
        for elt_a, elts_b in edu_splits.items():
            map_items = [(elt_a, elts_b[0])]
            anno_map.update(map_items)
            cautious_map.update(map_items)
        
        if verbose:
            if pw_conflicts:
                print('Conflict:')
                print('\n'.join('  {}\t<>\t{}'.format(str(elt_a), str(elt_b))
                                for elt_a, elt_b in pw_conflicts))

    # update anno_doc using the computed mapping
    anno_map_id = {x.local_id(): y.local_id()
                   for x, y in anno_map.items()}
    cautious_map_id = {x.local_id(): y.local_id()
                       for x, y in cautious_map.items()}
    # * forget mapped units and segments rewritten as CDUs
    anno_doc.units = [x for x in anno_doc.units
                      if (not is_edu(x) or
                          x.local_id() not in anno_map_id)]
    # * add the new CDUs to the list of schemas
    anno_doc.schemas.extend(new_cdus)

    # rewrite the support of relations and schemas
    objects = {x.local_id(): x
               for x in itertools.chain(anno_doc.units, anno_doc.relations,
                                        anno_doc.schemas)}
    # * rewrite the support of relations
    for rel in anno_doc.relations:
        src = anno_map_id.get(rel.span.t1, rel.span.t1)
        tgt = anno_map_id.get(rel.span.t2, rel.span.t2)
        # update relation span, source, target
        rel.span = RelSpan(src, tgt)
        rel.source = objects[src]
        rel.target = objects[tgt]
        # if necessary, mark relation type for review
        if src in cautious_map_id or tgt in cautious_map_id:
            rel.type = _SPLIT_PREFIX + rel.type

    # * rewrite the support of schemas
    for sch in anno_doc.schemas:
        # sch.id = sch.id
        sch.units = set(anno_map_id.get(x, x) for x in sch.units)
        sch.relations = set(anno_map_id.get(x, x) for x in sch.relations)
        sch.schemas = set(anno_map_id.get(x, x) for x in sch.schemas)
        sch.type = sch.type
        # sch.features = sch.features
        # sch.metadata = sch.metadata
        sch.span = sch.units | sch.relations | sch.schemas
        sch.fleshout(objects)

    return anno_doc


def split_annotated(dir_orig, doc, verbose=0):
    """Do the split

    Parameters
    ----------
    dir_orig : string
        Folder of the annotated corpus
    doc : string
        Name of the document
    """
    # locate game folder
    dir_orig = os.path.abspath(dir_orig)
    game_dir_orig = os.path.join(dir_orig, doc)
    if not os.path.isdir(game_dir_orig):
        err_msg = 'Unable to find original files {}'.format(game_dir_orig)
        raise ValueError(err_msg)

    # check for unannotated subfolder
    unannotated_dir = os.path.join(game_dir_orig, 'unannotated')
    if not os.path.isdir(unannotated_dir):
        err_msg = 'Unable to find unannotated folder {}'.format(
            unannotated_dir)
        raise ValueError(err_msg)

    # check for annotated subfolder
    annotated_dir = os.path.join(game_dir_orig, 'annotated')
    if not os.path.isdir(annotated_dir):
        err_msg = 'Unable to find annotated folder {}'.format(
            annotated_dir)
        raise ValueError(err_msg)

    # create discourse/BRONZE and units/BRONZE (should it be skar?)
    disc_dir = os.path.join(game_dir_orig, 'discourse', 'BRONZE')
    if not os.path.isdir(disc_dir):
        os.makedirs(disc_dir)
        print('Creating folder {}'.format(disc_dir))
    units_dir = os.path.join(game_dir_orig, 'units', 'BRONZE')
    if not os.path.isdir(units_dir):
        os.makedirs(units_dir)
        print('Creating folder {}'.format(units_dir))

    # process each annotated file
    for anno_file in sorted(glob(os.path.join(annotated_dir, '*.aa'))):
        print('Processing {}'.format(os.path.basename(anno_file)))
        print('=================================')
        # matching text file
        text_file = os.path.splitext(anno_file)[0] + '.ac'

        # read and filter the `annotated` file
        anno_doc = educe.glozz.read_annotation_file(anno_file, text_file)
        anno_doc = fix_likely_annotation_errors(anno_doc, verbose=1)

        # read the `unannotated` file
        unanno_file = os.path.join(unannotated_dir,
                                   os.path.basename(anno_file))
        unanno_doc = educe.glozz.read_annotation_file(unanno_file, text_file)

        # infer resegmentation in `annotated`
        anno_doc = infer_resegmentation(unanno_doc, anno_doc, verbose=1)

        # create `units` doc from the cleaned `annotated`
        # port annotations: dialogue acts, resources, preferences
        units_doc = copy.deepcopy(anno_doc)
        # * keep all clean units
        # * relations: anaphors only
        units_doc.relations = [x for x in units_doc.relations
                               if x.type == 'Anaphor']
        # * schemas: 'Several_resources' only
        units_doc.schemas = [x for x in units_doc.schemas
                             if x.type == 'Several_resources']

        # create `discourse` from the cleaned `annotated`
        disc_doc = copy.deepcopy(anno_doc)
        # remove dialogue act annotation from segments, so that they revert
        # to being basic EDUs
        for x in disc_doc.units:
            if is_edu(x):
                x.type = 'Segment'
                x.features = {}
        # filter anaphoric relations
        disc_doc.relations = [x for x in disc_doc.relations
                              if x.type != 'Anaphor']
        # filter resources schemas
        disc_doc.schemas = [x for x in disc_doc.schemas
                            if x.type != 'Several_resources']

        # dump both files
        bname = os.path.basename(os.path.splitext(anno_file)[0])
        # discourse file
        disc_anno_file = os.path.join(disc_dir, bname + '.aa')
        write_annotation_file(disc_anno_file, disc_doc)
        # units file
        units_anno_file = os.path.join(units_dir, bname + '.aa')
        write_annotation_file(units_anno_file, units_doc)
        # create two symlinks to the same .ac file, for discourse and units
        ac_path = os.path.join(game_dir_orig, 'unannotated',
                               bname + '.ac')
        for subdir in [disc_dir, units_dir]:
            link_src = os.path.relpath(ac_path, subdir)
            link_name = os.path.join(subdir, os.path.basename(ac_path))
            if os.path.exists(link_name):
                os.unlink(link_name)
            try:
                os.symlink(link_src, link_name)
            except OSError:
                print('Unable to create symlink {} to {}'.format(
                    link_src, link_name
                ))
                raise

        # check that all annotations from the filtered annotated doc
        # have been ported to either units or discourse
        anno_all_annos = set(x.local_id() for x in itertools.chain(
            anno_doc.units, anno_doc.relations, anno_doc.schemas
        ))
        # gather all annotations from units_doc and disc_doc
        units_all_annos = set(x.local_id() for x in itertools.chain(
            units_doc.units, units_doc.relations, units_doc.schemas
        ))
        disc_all_annos = set(x.local_id() for x in itertools.chain(
            disc_doc.units, disc_doc.relations, disc_doc.schemas
        ))
        # do the check
        missing_annos = (anno_all_annos - units_all_annos - disc_all_annos)
        if missing_annos:
            print('Missing annotations from {}:\n  {}'.format(
                anno_file,
                '\n  '.join(str(x) for x
                            in set(anno_doc.units + anno_doc.relations +
                                   anno_doc.schemas)
                            if x.local_id() in missing_annos)
            ))
            print('unanno EDUs:\n  {}'.format(
                '\n  '.join(str(x) for x
                            in unanno_doc.units if is_edu(x))
            ))
            raise ValueError('Ho?')
        # pretty
        print()


def main():
    """Split an annotated file into two files for units and discourse."""
    parser = argparse.ArgumentParser(
        description='Split an annotated file into two files: units, discourse'
    )
    parser.add_argument('dir_orig', metavar='DIR',
                        help='folder of the annotated corpus')
    parser.add_argument('doc', metavar='DOC',
                        help='document')
    args = parser.parse_args()
    # do the job
    split_annotated(args.dir_orig, args.doc)


if __name__ == '__main__':
    main()
