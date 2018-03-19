"""Transfer dialogue acts annotations from one version to the other.

The typical use case is to port "units" annotation from the linguistic
to the situated version.
"""
from __future__ import absolute_import, print_function

import argparse
import codecs
from glob import glob
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

from educe.glozz import _GLOZZ_DECL, _MINIDOM_ZERO
from educe.stac.annotation import DIALOGUE_ACTS


# helper
def subdoc_num(fpath):
    """Extract the subdoc number from a filepath.
    """
    return int(os.path.splitext(os.path.basename(fpath))[0].rsplit('_', 1)[1])


def transfer_acts(dir_from, dir_to):
    """Transfer acts from one version to the other.

    Parameters
    ----------
    dir_from : str
        Folder containing the annotated version.
    dir_to : str
        Folder containing the target version for the transfer.
    """
    # gather the segments and their annotation to be transferred,
    # in textual order
    annotated_segs = []
    # DIRTY assume the source version is GOLD
    dir_from = os.path.join(dir_from, 'units', 'GOLD')
    files_src_aa = sorted(glob(os.path.join(dir_from, '*.aa')),
                          key=subdoc_num)
    files_src_ac = sorted(glob(os.path.join(dir_from, '*.ac')),
                          key=subdoc_num)
    for file_aa, file_ac in zip(files_src_aa, files_src_ac):
        # accumulate segments and their annotation in each subdoc
        # print(file_aa, file_ac)
        text = codecs.open(file_ac, mode='rb', encoding='utf-8').read()
        xml_tree = ET.parse(file_aa)
        xml_root = xml_tree.getroot()
        #
        subdoc_segs = []
        for elt_unit in sorted(xml_root.findall('unit'),
                               key=lambda x: int(x.find('positioning/start/singlePosition').get('index'))):
            elt_type = elt_unit.find('characterisation/type').text
            if not elt_type in DIALOGUE_ACTS:
                continue
            seg_anno = {}
            # id
            seg_anno['id'] = elt_unit.get('id')
            seg_anno['type'] = elt_type
            # metadata: author, creation-date, lastModifier,
            # lastModificationDate
            seg_anno['metadata'] = dict(
                (x.tag, x.text)
                for x in elt_unit.find('metadata')
            )
            # characterisation: (type), featureSet
            seg_anno['features'] = dict(
                (x.get('name'), x.text)
                for x in elt_unit.findall('characterisation/featureSet/feature')
            )
            # positioning
            seg_anno['positioning'] = dict(
                (x, int(elt_unit.find('positioning/{x}/singlePosition'.format(x=x)).get('index')))
                for x in ('start', 'end')
            )
            # text
            seg_anno['text'] = text[int(seg_anno['positioning']['start']):
                                    int(seg_anno['positioning']['end'])]
            subdoc_segs.append(seg_anno)
        # sort segments by their starting position
        subdoc_segs = sorted(subdoc_segs,
                             key=lambda x: x['positioning']['start'])
        annotated_segs.extend(subdoc_segs)

    # update the target files on the fly
    # DIRTY assume the target version is BRONZE
    dir_to = os.path.join(dir_to, 'units', 'BRONZE')
    files_tgt_aa = sorted(glob(os.path.join(dir_to, '*.aa')),
                          key=subdoc_num)
    files_tgt_ac = sorted(glob(os.path.join(dir_to, '*.ac')),
                          key=subdoc_num)
    seg_src_idx = 0  # index of the annotated segment to match
    for file_aa, file_ac in zip(files_tgt_aa, files_tgt_ac):
        # accumulate segments and their annotation in each subdoc
        # print(file_aa, file_ac)
        text = codecs.open(file_ac, mode='rb', encoding='utf-8').read()
        xml_tree = ET.parse(file_aa)
        xml_root = xml_tree.getroot()
        #
        subdoc_segs = []
        for elt_unit in sorted(xml_root.findall('unit'),
                               key=lambda x: int(x.find('positioning/start/singlePosition').get('index'))):
            elt_type = elt_unit.find('characterisation/type').text
            if elt_type != 'Segment':
                # ignore all units that are not segments from the src XML ;
                # the segments from the non-linguistic turns are tagged
                # 'Other'
                continue
            # build the same descriptor for the current seg from tgt XML
            seg_anno = {}
            # id
            seg_anno['id'] = elt_unit.get('id')
            seg_anno['type'] = elt_type
            # metadata: author, creation-date, lastModifier,
            # lastModificationDate
            seg_anno['metadata'] = dict(
                (x.tag, x.text)
                for x in elt_unit.find('metadata')
            )
            # characterisation: (type), featureSet
            seg_anno['features'] = dict(
                (x.get('name'), x.text)
                for x in elt_unit.findall('characterisation/featureSet/feature')
            )
            # positioning
            seg_anno['positioning'] = dict(
                (x, int(elt_unit.find('positioning/{x}/singlePosition'.format(x=x)).get('index')))
                for x in ('start', 'end')
            )
            # text
            seg_anno['text'] = text[int(seg_anno['positioning']['start']):
                                    int(seg_anno['positioning']['end'])]
            # end of the common part

            # the current segment from the tgt XML should match the current
            # segment from the src XML
            seg_src = annotated_segs[seg_src_idx]
            if ((seg_src['text'] != seg_anno['text'] or
                 seg_src['id'] != seg_anno['id'] or
                 seg_src['metadata']['author'] != seg_anno['metadata']['author'] or
                 seg_src['metadata']['creation-date'] != seg_anno['metadata']['creation-date'])):
                err_msg = "Unexpected mismatch:\nsrc={}\ntgt={}"
                raise ValueError(err_msg.format(seg_src, seg_anno))
            seg_src_idx += 1
            # transfer the acts, update the metadata
            # TODO check
            elt_unit.find('metadata/lastModifier').text = seg_src['metadata']['lastModifier']
            elt_unit.find('metadata/lastModificationDate').text = seg_src['metadata']['lastModificationDate']
            elt_unit.find('characterisation/type').text = seg_src['type']
            elt_fs = elt_unit.find('characterisation/featureSet')
            assert len(elt_fs) == 0
            for fn, fv in seg_src['features'].items():
                feat = ET.SubElement(elt_fs, 'feature', attrib={'name': fn})
                feat.text = fv
                feat.tail = '\n'
        # write to another XML file
        out_aa = file_aa + '.fix'
        # copy'n'paste of educe.glozz.write_annotation_file()
        # with its two contortions (with minor adaptations)
        elem = xml_tree.getroot()  # adapted
        string1 = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(string1.replace('\n', ''))
        string2 = reparsed.toprettyxml(indent="", encoding='utf-8')
        with codecs.open(out_aa, mode='wb', encoding='utf-8') as fout:
            print(_GLOZZ_DECL, file=fout)
            out_str = string2[_MINIDOM_ZERO:].decode('utf-8')
            fout.write(out_str)
        # end copy'n'paste


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfer dialogue acts annotation."
    )
    parser.add_argument("game", metavar="game", help="Game")
    parser.add_argument("from_dir", metavar="dir", help="From folder")
    parser.add_argument("to_dir", metavar="dir", help="To folder")
    #
    args = parser.parse_args()
    # check that the arguments correspond to existing versions of a game
    abs_dir_from = os.path.abspath(os.path.join(args.from_dir, args.game))
    abs_dir_to = os.path.abspath(os.path.join(args.to_dir, args.game))
    if not os.path.isdir(abs_dir_from):
        raise ValueError("Unable to locate game in source folder: {}".format(
            abs_dir_from)
        )
    elif not os.path.isdir(abs_dir_to):
        raise ValueError("Unable to locate game in target folder: {}".format(
            abs_dir_to)
        )
    #
    transfer_acts(abs_dir_from, abs_dir_to)
    
