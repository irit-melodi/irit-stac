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
from educe.annotation import (Relation, RelSpan, Schema)
from educe.stac.annotation import (addressees, DIALOGUE_ACTS, is_cdu, is_edu,
                                   is_preference, is_resource,
                                   is_relation_instance, is_turn)
from educe.stac.corpus import write_annotation_file


DIALOGUE_ACTS = DIALOGUE_ACTS + ['Strategic_comment']
# copied from educe.stac.edit.cmd.split_edu
# pylint: disable=fixme
_SPLIT_PREFIX = 'FIXME:'
# pylint: enable=fixme


def filter_likely_annotation_errors(anno_doc, verbose=1):
    """Filter a document by removing likely annotation errors.

    Filter out likely errors due to the terrible glozz UX.
    Likely errors are currently defined as:
    - units of span length 0,
    - dialogue acts with no addressee and no surface act
    - schemas with no member

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
            (is_edu(x) and
             x.type in DIALOGUE_ACTS and
             addressees(x) is None and
             (x.features.get('Surface_act') == 'Please choose...')))
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
        print('== Likely errors due to glozz UX ==')
        if anno_units_err:
            print('----- Units -----')
            print('\n'.join('[ ] {}'.format(str(x))
                            for x in anno_units_err))
        if anno_schms_err:
            print('----- Schemas -----')
            print('\n'.join('[ ] {}'.format(str(x))
                            for x in anno_schms_err))
        if anno_relas_err:
            print('----- Relations -----')
            print('\n'.join('[ ] {}'.format(str(x))
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
    res = (elts[0].span.char_start == tgt.span.char_start and
           elts[-1].span.char_end == tgt.span.char_end and
           all(elt_cur.overlaps(elt_nxt) is None
               for elt_cur, elt_nxt
               in zip(elts[:-1], elts[1:])))
    return res


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
        # 1. remove duplicate new annotations
        # (EDUs that are introduced in `annotated` twice, as a segment
        # and a dialogue act)
        new_edus = [x for x in a_edus if x.local_id() not in u_ids]
        a_dups = [(elt_a, elt_b) for elt_a, elt_b
                  in itertools.combinations(
                      sorted(new_edus, key=lambda x: x.local_id(),
                             reverse=True), 2)
                  if (elt_a.span == elt_b.span and
                      ((elt_a.type in DIALOGUE_ACTS and
                        elt_b.type not in DIALOGUE_ACTS) or
                       (elt_a.type not in DIALOGUE_ACTS and
                        elt_b.type in DIALOGUE_ACTS)))]
        a_edus_useless = set(x[0] if x[0].type not in DIALOGUE_ACTS else x[1]
                             for x in a_dups)
        # TODO create map from duplicates to their original version,
        # to update relations and schemas later
        a_edus = [x for x in a_edus if x not in a_edus_useless]

        # 2. list conflicts, then whitelist them progressively
        # NB: we sort EDUs in reverse using their local_ids, so that
        # conflict pairs are of the form (stac*, skar*) ; this is
        # admittedly a cheap, ad-hoc, trick
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b
                        in itertools.combinations(
                            sorted(a_edus, key=lambda x: x.local_id(),
                                   reverse=True), 2)
                        if elt_a.overlaps(elt_b)]
        # exact matches where the first member is an EDU from `unannotated`
        # and the second member is a dialogue act on the same span
        # FIXME replace span equality with span equality +- 1 (off-by-one)
        # => write as a function, call it here
        # RESUME HERE RESUME HERE RESUME HERE (do the FIXME)
        exact_matches = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                         if (elt_a.local_id() in u_ids and
                             elt_a.span == elt_b.span)]
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                        if (elt_a, elt_b) not in set(exact_matches)]
        # exact matches purely on new annotations, i.e. a new segment +
        # a new discourse act on the same span
        anno_matches = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                        if (elt_a.span == elt_b.span and
                            elt_a.local_id() not in u_ids and
                            elt_b.local_id() not in u_ids and
                            len([x for x in (elt_a, elt_b)
                                 if x.type in DIALOGUE_ACTS]) == 1 and
                            len([x for x in (elt_a, elt_b)
                                 if x.type not in DIALOGUE_ACTS]) == 1)]
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                        if (elt_a, elt_b) not in set(anno_matches)]
        # find EDU merges
        edu_merges = dict()  # elt_b -> list of elt_a
        for elt_b, pairs in itertools.groupby(pw_conflicts,
                                              key=lambda x: x[1]):
            sorted_a = sorted((y[0] for y in pairs), key=lambda z: z.span)
            # we approximately check that the sequence of original EDUs
            # fully covers the span of elt_b, from start to end, with
            # no overlap
            if ((all(elt_a.local_id() in u_ids for elt_a in sorted_a) and
                 approximate_cover(sorted_a, elt_b))):
                edu_merges[elt_b] = sorted_a
        pw_conflicts = [(elt_a, elt_b) for elt_a, elt_b in pw_conflicts
                        if elt_b not in set(edu_merges.keys())]
        # find EDU splits
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

        if verbose:
            if pw_conflicts:
                print('Conflict:')
                print('\n'.join('  {}\t<>\t{}'.format(str(elt_a), str(elt_b))
                                for elt_a, elt_b in pw_conflicts))


    # backport unit annotation to original segment if they have the same span

    # filter out redundant or obsolete EDUs

    # rewrite the support of schemas and relations using anno_map

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
        # matching text file
        text_file = os.path.splitext(anno_file)[0] + '.ac'

        # read and filter the `annotated` file
        anno_doc = educe.glozz.read_annotation_file(anno_file, text_file)
        anno_doc = filter_likely_annotation_errors(anno_doc, verbose=1)

        # read the `unannotated` file
        unanno_file = os.path.join(unannotated_dir,
                                   os.path.basename(anno_file))
        unanno_doc = educe.glozz.read_annotation_file(unanno_file, text_file)

        # infer resegmentation in `annotated`
        anno_doc = infer_resegmentation(unanno_doc, anno_doc, verbose=1)
        raise ValueError('Stop here')

        # map annotations from annotated to unannotated
        unanno_edus = {x.local_id(): x for x in unanno_doc.units if is_edu(x)}
        anno_edus = {x.local_id(): x for x in anno_doc.units if is_edu(x)}
        unanno_edus2anno_edus = {x_id:
                                 [y_id for y_id, y in anno_edus.items()
                                  if y.encloses(x) or x.encloses(y)]
                                 for x_id, x in unanno_edus.items()}
        ambig_items = {
            x_id: y_ids
            for x_id, y_ids in unanno_edus2anno_edus.items()
            if (len([y_id for y_id in y_ids
                     if anno_edus[y_id].type in DIALOGUE_ACTS]) > 1 or
                len([y_id for y_id in y_ids
                     if anno_edus[y_id].type not in DIALOGUE_ACTS]) > 1)
        }
        # resolve ambiguities
        # * if the ambiguity is on a sequence of non-overlapping EDUs
        # whose beginning and end match the unannotated EDU's, it means
        # there was an EDU split
        print('Ambiguous EDU matchings in {}:'.format(anno_file))
        for unanno_id, anno_ids in ambig_items.items():
            unanno_edu = unanno_edus[unanno_id]
            # EDU split manifests as an annotated sequence of dialogue acts
            m_acts = [(y_id, anno_edus[y_id]) for y_id in anno_ids
                      if anno_edus[y_id].type in DIALOGUE_ACTS]
            if len(m_acts) > 1:
                # check whether they form a non-overlapping sequence
                # that covers the span, as this would indicate an EDU split
                m_acts = sorted(m_acts, key=lambda x: x[1].span)
                if ((m_acts[0][1].span.char_start != unanno_edu.span.char_start or
                     m_acts[-1][1].span.char_end != unanno_edu.span.char_end or
                     any(elt_a[1].span.overlaps(elt_b[1].span)
                         for elt_a, elt_b
                         in itertools.product(m_acts, m_acts)
                         if elt_a != elt_b))):
                    # for the moment, just print them
                    print('{}\n  {}'.format(
                        unanno_edu,
                        '\n  '.join(str(y) for y_id, y in m_acts)
                    ))
                else:
                    print('{}\nis split into\n  {}'.format(
                        unanno_edu,
                        '\n  '.join(str(y) for y_id, y in m_acts)
                    ))
            # segments
            m_segs = [(y_id, anno_edus[y_id]) for y_id in anno_ids
                      if anno_edus[y_id].type not in DIALOGUE_ACTS]
            if len(m_segs) > 1:
                # check whether they form a non-overlapping sequence
                # that covers the span, as this would indicate an EDU split
                m_segs = sorted(m_segs, key=lambda x: x[1].span)
                if ((m_segs[0].span.char_start != unanno_edu.span.char_start or
                     m_segs[-1].span.char_end != unanno_edu.span.char_end or
                     any(elt_a[1].span.overlaps(elt_b[1].span)
                         for elt_a, elt_b
                         in itertools.product(m_segs, m_segs)
                         if elt_a != elt_b))):
                    # for the moment, just print them
                    print('{}\n  {}'.format(
                        unanno_edu,
                        '\n  '.join(str(y) for y_id, y in m_segs)
                    ))
                    print(m_segs[0][1].span.char_start != unanno_edu.span.char_start)
                else:
                    print('{}\nis split into\n  {}'.format(
                        unanno_edu,
                        '\n  '.join(str(y) for y_id, y in m_segs)
                    ))
        raise ValueError('Check me')
        anno_edus2unanno_edus = {y.local_id():
                                 [x.local_id() for x in unanno_edus
                                  if y.encloses(x) or x.encloses(y)]
                                 for y in anno_edus}
        # RESUME HERE
        # map schemas to EDUs
        # anno_schs2anno_edus = {y.local_id():
                               
        anno2edu = {}  # anno : (edu, is_exact_match)

        # create units doc from unannotated:
        # port annotations: dialogue acts, resources, preferences
        units_doc = copy.deepcopy(unanno_doc)
        # * EDUs (dialogue acts and other EDUs)
        # * dialogue acts: merge them into the regular EDUs
        acts = [x for x in anno_doc.units if x.type in DIALOGUE_ACTS]
        for edu in [x for x in units_doc.units if is_edu(x)]:
            # enclosing dialogue acts
            enclosing_acts = [y for y in acts if y.encloses(edu)]
            if len(enclosing_acts) == 1:
                # unique: backport its type and features
                act = enclosing_acts[0]
                # mark span mismatch for additional reviewing
                if act.text_span() != edu.text_span():
                    edu.type = _SPLIT_PREFIX + act.type
                    edu.features.update(
                        {k: _SPLIT_PREFIX + v
                         for k, v in act.features.items()}
                    )
                else:
                    edu.type = act.type
                    edu.features.update(act.features)
                # update the mapping from annotations to basic EDUs
                anno2edu[act.local_id()] = (edu.local_id(), True)
            elif len(enclosing_acts) > 1:
                print('> 1 matching dialogue acts')
                print('\n'.join('  ' + str(y) for y in enclosing_acts))

        # * port resources and preferences
        # * port resources as they are
        units_doc.units.extend(x for x in anno_doc.units
                               if is_resource(x) or is_preference(x))
        # * port anaphors
        units_doc.relations.extend(x for x in anno_doc.relations
                                   if x.type == 'Anaphor')
        # * port 'Several_resources' schemas
        units_doc.schemas.extend(x for x in anno_doc.schemas
                                 if x.type == 'Several_resources')

        # create discourse from unannotated
        disc_doc = copy.deepcopy(unanno_doc)
        edus = {x.local_id(): x for x in disc_doc.units if is_edu(x)}
        # gather annotations in the support of CDUs and relations
        # that are not basic EDUs
        relations = [x for x in anno_doc.relations if is_relation_instance(x)]
        cdus = [x for x in anno_doc.schemas if is_cdu(x)]
        strangers = dict()
        for rel in relations:
            strangers.update({
                x.local_id(): x for x in [rel.source, rel.target]
                if x.local_id() not in edus
            })
        for cdu in cdus:
            strangers.update({
                x.local_id(): x for x in cdu.members
                if x.local_id() not in edus
            })

        # second step to map these non-EDUs to standard EDUs:
        # if there is no exact match, take the first enclosed or
        # enclosing EDU
        # TODO ? extend to handle relations and schemas as well?
        # |- a priori, not necessary here because we start over from
        # |  unannotated, which is not supposed to contain any relation
        # |  or schema
        for anno_id, anno in strangers.items():
            m_edus = [edu_id for edu_id, edu in edus.items()
                      if anno.encloses(edu) or edu.encloses(anno)]
            if not m_edus:
                err_msg = 'Unable to find EDU to replace {}'
                raise ValueError(err_msg.format(anno))
            elif len(m_edus) == 1:
                # mark the EDU as an exact match
                m_edu = m_edus[0]
                anno2edu[anno_id] = (m_edu, True)
            else:
                # several options: pick the first and mark the EDU as an
                # inexact match
                m_edu = m_edus[0]
                anno2edu[anno_id] = (m_edu, False)
                if verbose:
                    print('Inexact match for {}'.format(anno))
                    print(', '.join(str(edu) for edu_id, edu in edus.items()
                                    if anno.encloses(edu)))

        # * port relations
        for relation in relations:
            # relation id is carried from relation
            rel_id = relation.local_id()

            # "relation span" (tricky)
            add_prefix = False
            # source annotation
            src = relation.source.local_id()
            if src in anno2edu:
                m_edu, exact_match = anno2edu[src]
                src = m_edu
                add_prefix = add_prefix or not exact_match
            # target annotation
            tgt = relation.target.local_id()
            if tgt in anno2edu:
                m_edu, exact_match = anno2edu[tgt]
                tgt = m_edu
                add_prefix = add_prefix or not exact_match
            # finally create relation span
            rspan = RelSpan(src, tgt)

            # relation type, add prefix if necessary
            rtype = relation.type
            if add_prefix:
                rtype = _SPLIT_PREFIX + rtype

            # features and metadata are carried from relation
            features = relation.features
            metadata = relation.metadata

            # create new relation
            new_rel = Relation(rel_id, rspan, rtype, features,
                               metadata=metadata)
            new_rel.fleshout(edus)

            # add to discourse doc
            disc_doc.relations.append(new_rel)

        # * port CDUs
        for sch in cdus:
            # schema id is carried from sch
            sch_id = sch.local_id()
            # schema members: units, relations, schemas
            add_prefix = False
            # units
            new_units = []
            for x in sch.units:
                new_x = x
                if x in anno2edu:
                    m_edu, exact_match = anno2edu[x]
                    new_x = m_edu
                    add_prefix = add_prefix or not exact_match
                new_units.append(new_x)
            new_units = set(new_units)
            # relations
            new_relations = []
            for x in sch.relations:
                new_x = x
                if x in anno2edu:
                    m_edu, exact_match = anno2edu[x]
                    new_x = m_edu
                    add_prefix = add_prefix or not exact_match
                new_relations.append(new_x)
            new_relations = set(new_relations)
            # schemas
            new_schemas = []
            for x in sch.schemas:
                new_x = x
                if x in anno2edu:
                    m_edu, exact_match = anno2edu[x]
                    new_x = m_edu
                    add_prefix = add_prefix or not exact_match
                new_schemas.append(new_x)
            new_schemas = set(new_schemas)
            # add prefix on schema type if necessary
            stype = sch.type
            if add_prefix:
                stype = _SPLIT_PREFIX + stype
            # features and metadata are carried from sch
            features = sch.features
            metadata = sch.metadata
            # create new schema
            new_schema = Schema(sch_id, new_units, new_relations, new_schemas,
                                stype, features, metadata=metadata)
            new_schema.fleshout(edus)
            disc_doc.schemas.append(new_schema)

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

        # check that all annotations have been ported
        # gather all annotations from anno_doc
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
        # and all the annotations from annotated that were mapped
        mapped_annos = set(anno2edu.keys())
        # do the check
        missing_annos = (anno_all_annos -
                         (units_all_annos | disc_all_annos | mapped_annos))
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
