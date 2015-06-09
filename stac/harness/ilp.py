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

from attelo.table import UNRELATED
from attelo.decoding import Decoder

ZPL_TEMPLATE_DIR = fp.join(fp.dirname(__file__), 'ilp')


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


def dump_scores(dpack, tgt_dir=None, prefix='default', decoded=False):
    """ Dump classification scores for use in SCIP

    Default behavior is a dump of dpack.attach and dpack.label
    If decoded is True, dpack.prediction will be converted

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
    ``turn.dat`` contains turn lenghts, offsets and indexes for the document
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

    header = '\n'.join((
        "param EDU_COUNT := {0} ;".format(len(edus)),
        "param TURN_COUNT := {0} ;".format(len(turn_off)),
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
        r = re.compile('x#(\d+)#(\d+)')
        pairs = []
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
                si, sj = m.groups()
                pairs.append((int(si) - 1, int(sj) - 1))
        return zip(*pairs)

    # Build map (EDU1, EDU2) -> pair_index
    n_edus = len(dpack.edus)
    pair_pos = pos_indexes(dpack)
    pair_map = np.zeros((n_edus, n_edus), dtype=int)
    pair_map[pair_pos] = np.arange(len(dpack.pairings))

    # Build indexes of attached pairs
    output_attach = load_pairs()
    index_attached = pair_map[output_attach]

    return index_attached


class ILPDecoder(Decoder):
    """ Use ILP to generate constrained structures

    Uses third-party tools (SCIP/ZIMPL)

    See ZPL_TEMPLATE_DIR for constraint set description
    """

    def decode(self, dpack):
        tmpdir = mkdtemp()

        # Prepare ZIMPL template and data
        dump_scores(dpack, tmpdir, 'raw')
        input_path = mk_zimpl_input(dpack, tmpdir)

        # Run SCIP
        param_path = fp.join(ZPL_TEMPLATE_DIR, 'scip.parameters')
        output_path = fp.join(tmpdir, 'output.scip')
        with open(output_path, 'w') as f_out:
            call(['scip', '-f', input_path, '-s', param_path],
                 stdout=f_out, cwd=tmpdir)

        # Gather results
        index_attached = load_scip_output(dpack, output_path)
        rmtree(tmpdir)
        return self.select(dpack, index_attached)
