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
from educe.stac.annotation import (DIALOGUE_ACTS, is_cdu, is_edu,
                                   is_preference, is_resource,
                                   is_relation_instance)
from educe.stac.corpus import write_annotation_file


DIALOGUE_ACTS = DIALOGUE_ACTS + ['Strategic_comment']
# copied from educe.stac.edit.cmd.split_edu
# pylint: disable=fixme
_SPLIT_PREFIX = 'FIXME:'
# pylint: enable=fixme


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

    # read the annotated files
    for anno_file in sorted(glob(os.path.join(annotated_dir, '*.aa'))):
        # matching text file
        text_file = os.path.splitext(anno_file)[0] + '.ac'

        # GlozzDocument for annotated
        anno_doc = educe.glozz.read_annotation_file(anno_file, text_file)
        # GlozzDocument for unannotated
        unanno_file = os.path.join(unannotated_dir,
                                   os.path.basename(anno_file))
        unanno_doc = educe.glozz.read_annotation_file(unanno_file, text_file)

        # create units doc from unannotated
        units_doc = copy.deepcopy(unanno_doc)
        # units: dialogue acts, resources, preferences
        acts = [x for x in anno_doc.units if x.type in DIALOGUE_ACTS]
        # * backport dialogue act annotations to EDUs
        for edu in [x for x in units_doc.units if is_edu(x)]:
            # enclosing dialogue acts
            enclosing_acts = [y for y in acts if y.encloses(edu)]
            if not enclosing_acts:
                # no enclosing act is okay if there is no overlapping
                # act either (this EDU is just missing any sort of
                # unit annotation ; stac-check will detect and complain)
                overlapping_acts = [z for z in acts if z.encloses(edu)]
                if overlapping_acts:
                    # if overlapping act, complain now because we'll lose
                    # annotation
                    err_msg = ('No enclosing but overlapping dialogue acts'
                               'for {}'
                               '\n'.join('  ' + str(z)
                                         for z in overlapping_acts))
                    raise ValueError(err_msg.format(edu))
            elif len(enclosing_acts) == 1:
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
                if verbose:
                    print('Updated EDU: {}'.format(edu))
            else:  # > 1
                print('> 1 matching dialogue acts')
                print('\n'.join('  ' + str(y) for y in enclosing_acts))
        # * port resources and preferences
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
        # map these non-EDUs to standard EDUs
        # if there is no exact match, take the first enclosed EDU
        # TODO ? extend to handle relations and schemas as well
        # |- a priori, not necessary here because we start over from
        # |  unannotated, which is not supposed to contain any relation
        # |  or schema
        anno2edu = {}  # anno : (edu, is_exact_match)
        for anno_id, anno in strangers.items():
            m_edus = [edu_id for edu_id, edu in edus.items()
                      if anno.encloses(edu)]
            if not m_edus:
                err_msg = 'Unable to find EDU to replace {}'
                raise ValueError(err_msg.format(anno))
            elif len(m_edus) == 1:
                # mark the EDU as an exact match
                m_edu = m_edus[0]
                anno2edu[anno_id] = (m_edu, True)
            else:
                # mark the EDU as an inexact match
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
            print('Missing annotations from {}: {}'.format(
                anno_file, missing_annos))
            raise ValueError('Ho?')

        # dump both files
        bname = os.path.basename(os.path.splitext(anno_file)[0])
        # discourse file
        disc_anno_file = os.path.join(disc_dir, bname + '.aa')
        write_annotation_file(disc_anno_file, disc_doc)
        # units file
        units_anno_file = os.path.join(units_dir, bname + '.aa')
        write_annotation_file(units_anno_file, units_doc)
        # create symlinks to the .ac file
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
