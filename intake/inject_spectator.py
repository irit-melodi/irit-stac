"""Functions to augment an annotated game with spectator messages.

"""

from __future__ import print_function

import argparse
import csv
from glob import glob
import os
import subprocess
import sys


# path to the folder containing the intake scripts (including this one)
PATH_TO_INTAKE = os.path.dirname(__file__)


def infer_portioning(disc_dir):
    """Infer the portioning of a game given the glozz files in `disc_dir`.

    Parameters
    ----------
    disc_dir : string
        Path to a discourse folder containing one glozz .ac file per
        portion of the game ; `unannotated` seems the most convenient
        choice.

    Returns
    -------
    first_idx : list of float
        Identifier of the first turn of each portion.
    """
    ac_files = glob(os.path.join(disc_dir, '*.ac'))
    if not ac_files:
        err_msg = 'Unable to locate any glozz .ac file in {}'.format(disc_dir)
        raise ValueError(err_msg)

    first_idx = []
    for ac_file in ac_files:
        with open(ac_file, 'rb') as ac_file:
            for line in ac_file:
                fidx = float(line.split(':', 1)[0])
                first_idx.append(fidx)
    return sorted(first_idx)


def backport_portioning(seg_file, first_idx):
    """Encode game portioning in `seg_file`, according to `first_idx`.

    Parameters
    ----------
    seg_file : string
        Path to the segmented version of the CSV file for the game.
    first_idx : list of int
        Identifier of the first turn of each portion.
    """
    seg_file_res = seg_file + '.fut'
    with open(seg_file, 'rb') as seg_f:
        with open(seg_file_res, 'w') as seg_f_res:
            reader = csv.reader(seg_f, delimiter='\t')
            writer = csv.writer(seg_f_res, delimiter='\t')
            # leave header line
            line = reader.next()
            writer.writerow(line)
            # regular lines
            for line in reader:
                # keep existing empty lines
                if not line:
                    writer.writerow(line)
                    continue
                # insert an empty line just before a starting turn
                # (except for the turn starting the first portion)
                if float(line[0]) in first_idx[1:]:
                    writer.writerow([])
                # write the normal line
                writer.writerow(line)
    # replace the original segmented file
    os.rename(seg_file_res, seg_file)


def _backport_turn_text(f_orig, f_dest, f_res, verbose=0):
    """Backport turn text from `f_orig` to `f_dest` to produce `f_res`.

    Segment delimiters are stripped from the turn text in `f_orig`.

    Parameters
    ----------
    f_orig : File
        Version of the file with higher priority.
    f_dest : File
        Version of the file with lower priority.
    f_res : File
        `f_dest` with turns transfered from `f_orig`.
    verbose : int
        Verbosity level.
    """
    reader_orig = csv.reader(f_orig, delimiter='\t')
    reader_dest = csv.reader(f_dest, delimiter='\t')
    writer_res = csv.writer(f_res, delimiter='\t')

    # read and write header
    header_orig = reader_orig.next()
    header_dest = reader_dest.next()
    writer_res.writerow(header_dest)

    # read and write content
    for line_dest in reader_dest:
        # TODO? handle exhaustion of f_orig (try...except?)
        line_orig = reader_orig.next()

        # easy case: keep lines that are identical on both sides
        if line_orig == line_dest:
            writer_res.writerow(line_dest)
            continue

        # skip additional empty lines from f_orig
        while not line_orig:
            line_orig = reader_orig.next()

        if float(line_orig[0]) != float(line_dest[0]):
            err_msg = 'Weird state that should never be reached: {}\t{}'
            raise ValueError(err_msg.format(line_orig, line_dest))

        # matching turns: transfer line from _orig, without '&'
        txt_orig = line_orig[5]
        # optional warnings for differing texts
        if verbose:
            txt_dest = line_dest[5]
            raw_text_orig = ''.join(txt_orig.split('&'))
            raw_text_dest = ''.join(txt_dest.split('&'))
            if raw_text_orig != raw_text_dest:
                err_msg = [
                    "W: texts differ at turn {}".format(line_orig[0]),
                    "< " + txt_orig,
                    "> " + txt_dest,
                ]
                print('\n'.join(err_msg), file=sys.stderr)
        # finally, write the line without '&'
        new_line_dest = line_orig
        new_line_dest[5] = txt_orig.replace('&', '')
        writer_res.writerow(new_line_dest)


def backport_turn_text(file_orig, file_dest):
    """Replace turn text in `file_dest` using their version in `file_orig`.

    Typically used to force the text in `unsegmented` to match the text in
    `segmented`. We should ideally not do this and conform the text in
    `segmented` to the original one from the soclog, but this mess is
    legacy and we'll clean it later.
    I hope to be able to deprecate this function in the near future.

    Parameters
    ----------
    file_orig : string
        Path to file whose lines must be transferred.
    file_dest : string
        Path to file into which lines must be transferred ; its content
        is changed.
    """
    file_res = file_dest + '.fut'
    with open(file_orig, 'rb') as f_orig, open(file_dest, 'rb') as f_dest:
        with open(file_res, 'w') as f_res:
            _backport_turn_text(f_orig, f_dest, f_res, verbose=1)
    # replace file_dest
    os.rename(file_res, file_dest)


def _transfer_turns(f_orig, f_dest, f_res, verbose=0):
    """Transfer turns from `f_orig` to `f_dest` to produce `f_res`.

    Parameters
    ----------
    f_orig : File
        Version of the file with higher priority.
    f_dest : File
        Version of the file with lower priority.
    f_res : File
        `f_dest` with turns transfered from `f_orig`.
    verbose : int
        Verbosity level.
    """
    reader_orig = csv.reader(f_orig, delimiter='\t')
    reader_dest = csv.reader(f_dest, delimiter='\t')
    writer_res = csv.writer(f_res, delimiter='\t')

    # read and write header
    header_orig = reader_orig.next()
    header_dest = reader_dest.next()
    writer_res.writerow(header_dest)

    # read and write content
    for line_dest in reader_dest:
        # TODO? handle exhaustion of f_orig (try...except?)
        line_orig = reader_orig.next()

        # easy case: keep lines that are identical on both sides
        if line_orig == line_dest:
            writer_res.writerow(line_dest)
            continue

        # transfer empty lines, they mark subdoc split
        # TODO? get rid of spurious empty lines
        while not line_orig:
            writer_res.writerow(line_orig)  # transfer split
            line_orig = reader_orig.next()

        if float(line_orig[0]) < float(line_dest[0]):
            err_msg = 'Weird state that should never be reached: {}\t{}'
            raise ValueError(err_msg.format(line_orig, line_dest))

        # new turns in _dest: write as they are
        while float(line_orig[0]) > float(line_dest[0]):
            writer_res.writerow(line_dest)
            line_dest = reader_dest.next()

        if float(line_orig[0]) != float(line_dest[0]):
            err_msg = 'Weird state that should never be reached: {}\t{}'
            raise ValueError(err_msg.format(line_orig, line_dest))

        # matching turns: transfer line from _orig, with manually segmented
        # text
        # optional warnings for differing texts
        if verbose:
            txt_orig = line_orig[5]
            txt_dest = line_dest[5]
            raw_text_orig = ''.join(txt_orig.split('&'))
            raw_text_dest = ''.join(txt_dest.split('&'))
            if raw_text_orig != raw_text_dest:
                err_msg = [
                    "W: texts differ at turn {}".format(line_orig[0]),
                    "< " + txt_orig,
                    "> " + txt_dest,
                ]
                print('\n'.join(err_msg), file=sys.stderr)
        # finally, write the line
        writer_res.writerow(line_orig)


def transfer_turns(file_orig, file_dest):
    """Replace turns in `file_dest` using their version in `file_orig`.

    Parameters
    ----------
    file_orig : string
        Path to file whose lines must be transferred.
    file_dest : string
        Path to file into which lines must be transferred ; its content
        is changed.
    """
    file_res = file_dest + '.fut'
    with open(file_orig, 'rb') as f_orig, open(file_dest, 'rb') as f_dest:
        with open(file_res, 'w') as f_res:
            _transfer_turns(f_orig, f_dest, f_res, verbose=1)
    # replace file_dest
    os.rename(file_res, file_dest)


def augment_game(dir_orig, dir_dest, doc, resume_at_intake2=False):
    """Do the augmentation

    Parameters
    ----------
    dir_orig : string
        Folder of the annotated corpus
    dir_dest : string
        Folder for the augmented corpus
    doc : string
        Name of the document
    resume_at_intake2 : boolean, optional
        If True, resume execution just before intake-2. This is useful
        when you have to backport crappy editions from segmented to
        unsegmented to make intake2 and subsequent processes happy ;
        Of course, this slightly corrupts the corpus but we'll fix this
        later (and then hopefully get rid of or modify the purpose of this
        option).
    """
    # 1. locate original folder (existing version of the game) with files:
    # * for identical copy: soclog, pos-tagged, parsed
    # * for injection/weaving: unsegmented, segmented, unannotated,
    #     discourse, units?
    # the original folder can follow one of two known layout conventions
    game_dir_orig = os.path.join(dir_orig, doc)
    if not os.path.isdir(game_dir_orig):
        err_msg = 'Unable to find original files {}'.format(game_dir_orig)
        raise ValueError(err_msg)

    # soclog
    soclog_orig = glob(os.path.join(game_dir_orig, 'soclog', '*.soclog'))
    if len(soclog_orig) != 1:
        raise ValueError('Unable to locate soclog {}'.format(soclog_orig))
    soclog_orig = soclog_orig[0]

    # unsegmented: in ./unsegmented or ./csv
    useg_dir_orig = os.path.join(game_dir_orig, 'unsegmented')
    if not os.path.isdir(useg_dir_orig):
        useg_dir_orig = os.path.join(game_dir_orig, 'csv')
        if not os.path.isdir(useg_dir_orig):
            err_msg = 'The original game does not follow a known layout'
            raise ValueError(err_msg)
    useg_orig = glob(os.path.join(useg_dir_orig,
                                  doc + '*.soclog.csv'))
    if len(useg_orig) != 1:
        err_msg = 'Unable to locate unsegmented file {}'.format(useg_orig)
        raise ValueError(err_msg)
    useg_orig = useg_orig[0]
    # paranoid check
    if not os.path.isfile(useg_orig):
        err_msg = 'Weird error on locating unsegmented file {}'.format(
            useg_orig)
        raise ValueError(err_msg)

    # segmented: in ./segmented
    seg_dir_orig = os.path.join(game_dir_orig, 'segmented')
    seg_orig = glob(os.path.join(seg_dir_orig,
                                 doc + '*.soclog.seg.csv'))
    if len(seg_orig) != 1:
        err_msg = 'Unable to locate segmented file {}'.format(seg_orig)
        raise ValueError(err_msg)
    seg_orig = seg_orig[0]
    # paranoid check
    if not os.path.isfile(seg_orig):
        err_msg = 'Weird error on locating segmented file {}'.format(
            seg_orig)
        raise ValueError(err_msg)

    # pos-tagged
    # TODO

    # parsed
    # TODO

    # unannotated
    udis_dir_orig = os.path.join(game_dir_orig, 'unannotated')
    # TODO ?

    # discourse
    # TODO

    # units
    # TODO

    # locate destination folder
    if dir_dest != '.':
        err_msg = 'Please call this script from dir_dest (intake-1.sh legacy)'
        raise ValueError(err_msg)

    if not os.path.isdir(dir_dest):
        os.mkdir(dir_dest)
        print('Creating destination folder {}'.format(dir_dest))

    doc_dir_dest = os.path.join(dir_dest, doc)
    # in new layout: ./unsegmented/<game>.soclog.csv
    useg_dest = os.path.join(doc_dir_dest, 'unsegmented',
                             doc + '.soclog.csv')
    seg_dest = os.path.join(doc_dir_dest, 'segmented',
                            doc + '.soclog.seg.csv')
    if not resume_at_intake2:
        # intake-1
        # * creates dir_dest/{soclog,unsegmented,segmented}
        # * copies soclog
        # * calls intake/soclogtocsv to extract unsegmented
        # * creates .aam file
        # * calls segmentation/simple-segments to presegment automatically
        # into segmented
        intake1_cmd = [os.path.join(PATH_TO_INTAKE, 'intake-1.sh'),
                       soclog_orig, doc, "gen2-ling-only", "batch"]
        subprocess.check_call(intake1_cmd)

        # reinject edited lines from the previous version into the newly
        # extracted one ; this transfers crappy manual editions as well
        # as (the intended) segmentation
        # 1. reinject edited text from old to new `unsegmented`
        print('== Transfer edited turns from {} to {} =='.format(
            useg_orig, useg_dest))
        transfer_turns(useg_orig, useg_dest)
        # 2. reinject edited text and segmentation from old to new
        # `segmented`
        print('== Transfer edited turns from {} to {} =='.format(
            seg_orig, seg_dest))
        transfer_turns(seg_orig, seg_dest)
        # 3. reinject edited text from new `segmented` to new `unsegmented`
        # so that they match and intake-2 does not complain
        print('== Conform turn text from {} to {} =='.format(
            seg_dest, useg_dest))
        backport_turn_text(seg_dest, useg_dest)

        # TODO infer portioning from the glozz files: a doc split takes place
        # immediately before the first turn of the next section
        portion_idx = infer_portioning(udis_dir_orig)
        backport_portioning(seg_dest, portion_idx)
        

    # intake-2: segmented => unannotated aa/ac
    intake2_cmd = [os.path.join(PATH_TO_INTAKE, 'intake-2.sh'),
                   # this argument should be seg_dest
                   # and subprocess.check_call() should not have any 'cwd'
                   # parameter, but the current version of intake-2 writes
                   # its files into the current working directory...
                   os.path.join('segmented', doc + '.soclog.seg.csv'),
                   "gen2-ling-only"]
    subprocess.check_call(intake2_cmd, cwd=doc_dir_dest)

    # weaving


def main():
    """Augment an annotated game with spectator messages."""
    # parse command line
    parser = argparse.ArgumentParser(
        description='Augment an annotated game with spectator messages')
    parser.add_argument('dir_orig', metavar='DIR',
                        help='folder of the annotated corpus')
    parser.add_argument('dir_dest', metavar='DIR',
                        help='folder for the augmented corpus')
    parser.add_argument('doc', metavar='DOC',
                        help='document')
    # typical use case: 
    parser.add_argument('--resume_at_intake2', action='store_true',
                        help='resume execution just before intake2')
    args = parser.parse_args()
    # do the job
    augment_game(args.dir_orig, args.dir_dest, args.doc,
                 resume_at_intake2=args.resume_at_intake2)


if __name__ == '__main__':
    main()
