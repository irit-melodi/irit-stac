""" ILP decoding """
from __future__ import print_function

import os
import re
import itertools as itr
from os import path as fp
import numpy as np
from tempfile import mkdtemp
from shutil import rmtree
from subprocess import call

from educe.stac.annotation import SUBORDINATING_RELATIONS
from attelo.table import UNRELATED
from attelo.decoding import Decoder

ZPL_TEMPLATE_DIR = fp.join(fp.dirname(__file__), 'ilp')

# WIP seems to belong to stac.harness.local but...
SCIP_BIN_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..',
    'lib/scipoptsuite-3.2.0/scip-3.2.0/bin'))
"Folder containing the SCIP binary files (ILP parser)"
# end WIP


def pos_indexes(dpack):
    """ Returns indices of EDUs for each pairing

    Parameters
    ----------
    dpack: DataPack
        Datapack containing the pairings

    Returns
    -------
    tuple (numpy.ndarray, numpy.ndarray)
        Coordinates (x-axis and y-axis, respectively)
        of pairings in attachment/label matrices
    """
    edu_pos = dict((e, i) for i, e in enumerate(dpack.edus))
    pair_pos = np.vstack((edu_pos[u], edu_pos[v]) for u, v in dpack.pairings)

    return tuple(pair_pos.transpose())


def dump_scores_to_dat_files(dpack, tgt_dir=None, prefix='default', decoded=False):
    """ Dump classification scores for use in SCIP

    Default behavior is a dump of dpack.attach and dpack.label
    If decoded is True, dpack.prediction will be converted

    This creates two files:
    ``attach.dat`` contains the attachment prediction scores
    ``label.dat`` contains the label prediction scores

    Parameters
    ----------
    dpack: DataPack
        Datapack which data should be dumped

    tgt_dir: path
        Where the dump files should be placed.
        By default, a temporary directory will be created

    prefix: str
        Prefix for the dump files

    decoded: bool
        True if dpack.prediction should be dumped

    Returns
    -------
    path
        Directory receiving the dump files (see tgt_dir argument)
    """
    n_edus = len(dpack.edus)
    n_labels = len(dpack.labels)
    unrelated = dpack.label_number(UNRELATED)

    pair_pos = pos_indexes(dpack)

    tmpdir = mkdtemp() if tgt_dir is None else tgt_dir
    format_str = '{0:.0f}' if decoded else '{0:.2f}'

    # Attachments
    att_file = os.path.join(tmpdir, '{0}.attach.dat'.format(prefix))
    att_mat = np.zeros((n_edus, n_edus), dtype=float)
    if decoded:
        att_mat[pair_pos] = (
            np.array(dpack.graph.prediction != unrelated, dtype=int))
    else:
        att_mat[pair_pos] = dpack.graph.attach

    with open(att_file, 'w') as f:
        f.write('\n'.join(
                    ':'.join(format_str.format(p)
                    for p in row)
                for row in att_mat))
        f.write('\n')

    # Labels
    lab_file = os.path.join(tmpdir, '{0}.label.dat'.format(prefix))
    lab_tsr = np.zeros((n_edus, n_edus, n_labels), dtype=float)
    if decoded:
        attached_mask = (dpack.graph.prediction != unrelated)
        lab_tsr[pair_pos[0][attached_mask],
                pair_pos[1][attached_mask],
                dpack.graph.prediction[attached_mask]] = 1
    else:
        lab_tsr[pair_pos] = dpack.graph.label

    with open(lab_file, 'w') as f:
        f.write('\n'.join(
                    ' '.join(
                        ':'.join(format_str.format(p)
                        for p in tube)
                    for tube in row)
                for row in lab_tsr))
        f.write('\n')

    return tmpdir


def pretty_data(data):
    """ Formats a list of lists, with space and linebreaks separation

    Parameters
    ----------
    data: [[int]]
        Data to be formatted

    Returns
    -------
    str
        Formatted output.
        One line for each element along the first axis
        Inside a line, elements are separated by spaces
    """
    return '\n'.join(
                ' '.join(str(e) for e in lis)
            for lis in data)

def mk_zimpl_input(dpack, data_dir):
    """ Create ZIMPL input files tuned to a datapack

    This creates two files:
    ``turn.dat`` contains turn lengths, offsets and indexes for the document
    ``input.zpl`` contains the ZIMPL problem description, with a header
        specifiying EDU and turn counts.

    The template for ``input.zpl``, named ``template.zpl``, is located by
    ``ZPL_TEMPLATE_DIR``.

    Parameters
    ----------
    dpack: DataPack

    data_dir: path
        Where the created files will be placed

    Returns
    -------
    path
        The path of ``input.zpl``.
    """

    # Create turn information
    edus = sorted(dpack.edus, key=lambda x: x.span())
    turn_len = []   # Turn lengths
    turn_off = []   # Turn offsets
    edu_ind = []    # Turn indexes for EDUs
    c_off = 0
    turn_groups = itr.groupby(edus, lambda e: (e.grouping, e.subgrouping))
    for i, (k, turn) in enumerate(turn_groups):
        turn = list(turn)
        turn_len.append(len(turn))
        turn_off.append(c_off)
        c_off += len(turn)
        # Appends 1 1 1 1, then 2 2 2, for turns of lengths 4 & 3 resp.
        edu_ind.extend(itr.repeat(i + 1, len(turn)))

    data_path = fp.join(data_dir, 'turn.dat')
    with open(data_path, 'w') as f_data:
        print(pretty_data([turn_len, turn_off, edu_ind]), file=f_data)

    # Create speaker information
    speakers = []
    for i, e in enumerate(dpack.vocab):
        m = re.match('speaker_id_DU1=.*', e)
        if m:
            speakers.append(i)
    speakers = list(set(speakers))

    edu_speakers = dict()
    for (edu, _), feats in zip(dpack.pairings, dpack.data):
        if edu in edu_speakers:
            continue
        for si in speakers:
            if feats[0, si] == 1:
                edu_speakers[edu] = si
                break
        else:
            edu_speakers[edu] = -1

    sids = dict((s, i) for i, s in enumerate(speakers))
    current_last = dict()
    last_mat = np.zeros((len(edus), len(edus)), dtype=int)

    for i, edu in enumerate(edus):
        for plast in current_last.values():
            last_mat[plast][i] = 1;
        try:
            current_last[edu_speakers[edu]] = i
        except KeyError:
            pass

    data_path = fp.join(data_dir, 'mlast.dat')
    with open(data_path, 'w') as f_data:
        print(pretty_data(last_mat), file=f_data)

    # class indices that correspond to subordinating relations ;
    # required for the ILP formulation of the Right Frontier Constraint
    # in SCIP/ZIMPL
    subord_idc = [i for i, lbl in enumerate(dpack.labels, start=1)
                  if lbl in set(SUBORDINATING_RELATIONS)]

    header = '\n'.join((
        "param EDU_COUNT := {0} ;".format(len(edus)),
        "param TURN_COUNT := {0} ;".format(len(turn_off)),
        "param PLAYER_COUNT := {0} ;".format(len(speakers)),
        "param LABEL_COUNT := {0} ;".format(len(dpack.labels)),
        "set RSub := {{{0}}} ;".format(
            ', '.join(str(i) for i in subord_idc)),
        "param SUB_LABEL_COUNT := {0} ;".format(len(subord_idc)),
    ))

    template_path = fp.join(ZPL_TEMPLATE_DIR, 'template.zpl')
    input_path = fp.join(data_dir, 'input.zpl')

    with open(template_path) as f_template:
        template = f_template.read()

    with open(input_path, 'w') as f_input:
        print(header, file=f_input)
        print(template, file=f_input)

    return input_path


def load_scip_output(dpack, output_path):
    """ Load SCIP attachment output into datapack

    Parameters
    ----------
    dpack: DataPack

    output_path: path
        Path of SCIP output file

    Returns
    -------
    numpy.ndarray
        Indexes of attached pairings
    """

    def load_pairs():
        """ Convert SCIP output to attachment pairs """
        r = re.compile('x#(\d+)#(\d+)#(\d+)')
        pairs = []
        labels = []
        t_flag = False
        with open(output_path) as f:
            for line in f:
                m = r.match(line)
                if m:
                    # Start of triplets
                    t_flag = True
                elif t_flag:
                    # End of triplets
                    break
                else:
                    # Not reached triplets yet
                    continue
                si, sj, sr = m.groups()
                pairs.append((int(si) - 1, int(sj) - 1))
                labels.append(int(sr) - 1)
        return zip(*pairs), labels

    # Build map (EDU1, EDU2) -> pair_index
    n_edus = len(dpack.edus)
    pair_pos = pos_indexes(dpack)
    pair_map = np.zeros((n_edus, n_edus), dtype=int)
    pair_map[pair_pos] = np.arange(len(dpack.pairings))

    # Build indexes of attached pairs
    output_attach, output_labels = load_pairs()
    index_attached = pair_map[output_attach]
    assert(len(output_labels) == len(index_attached))

    # Build labels
    unrelated = dpack.label_number(UNRELATED)
    prediction = np.full(len(dpack), unrelated, dtype=np.int)
    prediction[index_attached] = output_labels

    return prediction


class ILPDecoder(Decoder):
    """ Use ILP to generate constrained structures

    Uses third-party tools (SCIP/ZIMPL)

    See ZPL_TEMPLATE_DIR for constraint set description
    """

    def decode(self, dpack, nonfixed_pairs=None):
        # TODO integrate nonfixed_pairs, maybe?
        tmpdir = mkdtemp()

        # Prepare ZIMPL template and data
        dump_scores_to_dat_files(dpack, tmpdir, 'raw')
        input_path = mk_zimpl_input(dpack, tmpdir)

        # Run SCIP
        param_path = fp.join(ZPL_TEMPLATE_DIR, 'scip.parameters')
        output_path = fp.join(tmpdir, 'output.scip')
        with open(output_path, 'w') as f_out:
            call([os.path.join(SCIP_BIN_DIR, 'scip'),
                  '-f', input_path,
                  '-s', param_path],
                 stdout=f_out, cwd=tmpdir)

        # Gather results
        prediction = load_scip_output(dpack, output_path)
        graph = dpack.graph.tweak(prediction=prediction)
        dpack = dpack.set_graph(graph)

        rmtree(tmpdir)
        return dpack
