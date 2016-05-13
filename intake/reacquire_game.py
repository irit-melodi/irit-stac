"""Script to re-acquire a game, porting over existing annotations.

This script enables to generate different versions of a game corresponding
to different generations of corpus annotation, and to preserve the existing
annotation.
"""

from __future__ import print_function

import argparse
import csv
from glob import glob
import os
import subprocess
import sys

from educe.stac.annotation import parse_turn_id


# path to the folder containing the intake scripts (including this one)
PATH_TO_INTAKE = os.path.dirname(os.path.abspath(__file__))


def read_portioning(seg_file):
    """Read portioning in the segmented csv file.

    Parameters
    ----------
    seg_file : string
        TODO

    Returns
    -------
    first_idx : list of parse_turn_id
        Identifier of the first turn of each portion.
    """
    first_idx = []
    with open(seg_file, 'rb') as seg_f:
        reader = csv.reader(seg_f, delimiter='\t')
        # leave header line
        line = reader.next()
        grab_next = True
        # regular lines
        for line in reader:
            # if empty line, be ready to start a new portion
            if ((not line or
                 not ''.join(line).strip())):
                grab_next = True
                continue
            # new portion
            if grab_next:
                first_idx.append(parse_turn_id(line[0]))
                grab_next = False
    return first_idx


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
    first_idx : list of parse_turn_id
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
                fidx = parse_turn_id(line.split(':', 1)[0].strip())
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
            writer = csv.writer(seg_f_res, delimiter='\t',
                                lineterminator='\n')
            # leave header line
            line = reader.next()
            writer.writerow(line)
            # regular lines
            for line in reader:
                # keep existing empty lines
                if ((not line or
                     not ''.join(line).strip())):
                    writer.writerow(line)
                    continue
                # insert an empty line just before a starting turn
                # (except for the turn starting the first portion)
                if parse_turn_id(line[0]) in first_idx[1:]:
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
    writer_res = csv.writer(f_res, delimiter='\t',
                            lineterminator='\n')

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
        while (not line_orig or
               not ''.join(line_orig).strip()):
            line_orig = reader_orig.next()

        if parse_turn_id(line_orig[0]) != parse_turn_id(line_dest[0]):
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
        Version of the file with higher priority (typically, the
        currently annotated version).
    f_dest : File
        Version of the file with lower priority (typically, the
        unannotated but finer-grained version).
    f_res : File
        `f_dest` with turns transfered from `f_orig`.
    verbose : int
        Verbosity level.
    """
    reader_orig = csv.reader(f_orig, delimiter='\t')
    reader_dest = csv.reader(f_dest, delimiter='\t')
    writer_res = csv.writer(f_res, delimiter='\t',
                            lineterminator='\n')

    # read and write header
    header_orig = reader_orig.next()
    header_dest = reader_dest.next()
    writer_res.writerow(header_dest)

    # read and write content
    for line_dest in reader_dest:
        # _orig exhausted means new turns in _dest
        try:
            line_orig = reader_orig.next()
        except StopIteration:
            writer_res.writerow(line_dest)
            continue

        # easy case: keep lines that are identical on both sides
        if line_orig == line_dest:
            writer_res.writerow(line_dest)
            continue

        # otherwise:
        # * empty lines mark subdoc split:
        #   we need to be careful to avoid splitting inside chunks of
        #   game messages
        buff_orig = []
        while (not line_orig
               or not ''.join(line_orig).strip()):
            # TODO? get rid of spurious empty lines
            # look ahead for the next turn in _orig
            buff_orig.append(line_orig)
            line_orig = reader_orig.next()
        # adjust subdoc split: append extra turns from _dest until
        # either we reach a safe split point
        # or all extra turns have been consumed
        if buff_orig:
            try:  # why try/catch: cf. DEBUG below
                turn_id_orig = parse_turn_id(line_orig[0])
            except ValueError:
                print([i for i, c in enumerate(line_orig[0])
                       if c == '\t'])
                print('\n'.join(line_orig))
                print(line_orig[0].split('\t'))
                raise
            # new turns in _dest should be appended to the current subdoc,
            # until we reach "It's X's turn to roll the dice." (or none
            # remains)
            try:
                turn_id_dest = parse_turn_id(line_dest[0])
            except ValueError:
                print([i for i, c in enumerate(line_dest[0])
                       if c == '\t'])
                print('\n'.join(line_dest))
                print(line_dest[0].split('\t'))
                raise
            while (turn_id_dest < turn_id_orig
                   and not (
                       line_dest[2] == 'Server'
                       and line_dest[5].endswith('turn to roll the dice.'))):
                writer_res.writerow(line_dest)
                # read next turn from _dest
                line_dest = reader_dest.next()
                try:
                    turn_id_dest = parse_turn_id(line_dest[0])
                except ValueError:
                    print([i for i, c in enumerate(line_dest[0])
                           if c == '\t'])
                    print('\n'.join(line_dest))
                    print(line_dest[0].split('\t'))
                    raise
            # finally, write the (buffered) subdoc split
            for buff_line in buff_orig:
                writer_res.writerow(buff_line)

        # write extra turns from _dest
        # DEBUG
        # FIXME csv reader (doublequote=True) fails to split fields on
        # if one field contains a doubled double quote (supposedly read
        # as one double-quote)
        try:
            parse_turn_id(line_orig[0])
        except ValueError:
            print([i for i, c in enumerate(line_orig[0])
                   if c == '\t'])
            print('\n'.join(line_orig))
            print(line_orig[0].split('\t'))
            raise
        # end DEBUG
        if parse_turn_id(line_orig[0]) < parse_turn_id(line_dest[0]):
            err_msg = 'Weird state that should never be reached: {}\t{}'
            raise ValueError(err_msg.format(line_orig, line_dest))

        # new turns in _dest: write as they are
        while parse_turn_id(line_orig[0]) > parse_turn_id(line_dest[0]):
            writer_res.writerow(line_dest)
            line_dest = reader_dest.next()

        if parse_turn_id(line_orig[0]) != parse_turn_id(line_dest[0]):
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


def augment_game(dir_orig, dir_dest, doc, gen, steps='all', seg_path=''):
    """Do the augmentation

    Parameters
    ----------
    dir_orig : string
        Folder of the annotated corpus
    dir_dest : string
        Folder for the augmented corpus
    doc : string
        Name of the document
    gen : int
        Generation to use for turn extraction from the soclog.
    steps : string, optional
        Specify which steps should be executed ; defaults to 'all'.
        This is useful when you have to backport crappy editions from
        segmented to unsegmented to make intake2 and subsequent processes
        happy ; Of course, this slightly corrupts the corpus but we'll fix
        this later (and then hopefully get rid of or modify the purpose of
        this option).
    seg_path : string, optional
        Path to the segmented file we should use ; This is necessary when
        there are more than one file under segmented/.
    """
    # 1. locate original folder (existing version of the game) with files:
    # * for identical copy: soclog, pos-tagged, parsed
    # * for injection/weaving: unsegmented, segmented, unannotated,
    #     discourse, units?
    # the original folder can follow one of two known layout conventions
    dir_orig = os.path.abspath(dir_orig)
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
    if seg_path:
        seg_orig = os.path.abspath(seg_path)
        if not os.path.isfile(seg_orig):
            raise ValueError('Unable to locate segmented file {}'.format(
                seg_path))
    else:
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

    # subdirs: unannotated, discourse, units
    udis_dir_orig = os.path.join(game_dir_orig, 'unannotated')
    # dis_dir_orig = os.path.join(game_dir_orig, 'discourse')
    # uni_dir_orig = os.path.join(game_dir_orig, 'units')
    # TODO ?

    # locate destination folder
    dir_dest = os.path.abspath(dir_dest)
    if not os.path.isdir(dir_dest):
        os.mkdir(dir_dest)
        print('Creating destination folder {}'.format(dir_dest))
    # move to destination folder to call intake scripts (legacy)
    caller_cwd = os.getcwd()
    os.chdir(dir_dest)
    # generate file names in destination folder
    doc_dir_dest = os.path.join(dir_dest, doc)
    # in new layout: ./unsegmented/<game>.soclog.csv
    useg_dest = os.path.join(doc_dir_dest, 'unsegmented',
                             doc + '.soclog.csv')
    seg_dest = os.path.join(doc_dir_dest, 'segmented',
                            doc + '.soclog.seg.csv')
    if steps in ['all', 'intake1']:
        # intake-1
        # * creates dir_dest/{soclog,unsegmented,segmented}
        # * copies soclog
        # * calls intake/soclogtocsv to extract unsegmented
        # * creates .aam file
        # * calls segmentation/simple-segments to presegment automatically
        # into segmented
        intake1_cmd = [os.path.join(PATH_TO_INTAKE, 'intake-1.sh'),
                       soclog_orig, doc, str(gen), "batch"]
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

        # read doc portioning from segmented
        portion_idx = read_portioning(seg_orig)
        if len(portion_idx) == 1:
            # no portioning in segmented: infer from the glozz files
            # a doc split takes place immediately before the first turn of
            # the next section
            # FIXME maybe it should rather split after its last turn?
            portion_idx = infer_portioning(udis_dir_orig)
            backport_portioning(seg_dest, portion_idx)

    if steps in ['all', 'intake2']:
        # intake-2: segmented => unannotated aa/ac
        intake2_cmd = [os.path.join(PATH_TO_INTAKE, 'intake-2.sh'),
                       # this argument should be seg_dest
                       # and subprocess.check_call() should not have any 'cwd'
                       # parameter, but the current version of intake-2 writes
                       # its files into the current working directory...
                       os.path.join('segmented', doc + '.soclog.seg.csv'),
                       str(gen)]
        subprocess.check_call(intake2_cmd, cwd=doc_dir_dest)

    # move back to the original working dir to call the weaving script
    os.chdir(caller_cwd)
    if steps in ['all', 'weave']:
        # weaving
        weave_cmd = ['stac-oneoff', 'weave',
                     dir_dest, dir_orig,
                     '--doc', doc,
                     '--annotator', '[GOLD|SILVER|BRONZE]',
                     '-o', dir_dest]
        subprocess.check_call(weave_cmd)

    # create symlinks to unannotated/*.ac in each of the subdirs in
    # discourse and units
    for ac_path in glob(doc_dir_dest + '/unannotated/*.ac'):
        for tgt_dir in ['discourse', 'units']:
            for subdir in glob('{}/{}/*/'.format(doc_dir_dest, tgt_dir)):
                os.symlink(
                    os.path.relpath(ac_path, subdir),
                    os.path.join(subdir, os.path.basename(ac_path))
                )


def main():
    """Re-acquire a game, porting over the existing annotation."""
    # parse command line
    parser = argparse.ArgumentParser(
        description='Re-acquire a game, porting over the annotation')
    parser.add_argument('dir_orig', metavar='DIR',
                        help='folder of the annotated corpus')
    parser.add_argument('dir_dest', metavar='DIR',
                        help='folder for the augmented corpus')
    parser.add_argument('doc', metavar='DOC',
                        help='document')
    # select generation
    parser.add_argument('--gen', metavar='N', type=int, default=2,
                        help='max generation of turns to include (1, 2, 3)')
    # select steps
    parser.add_argument('--steps', metavar='steps',
                        choices=['all', 'intake1', 'intake2', 'weave'],
                        default='all',
                        help='intake steps to take')
    # explicitly point to segmented (in case there is more than one in
    # the segmented/ folder)
    parser.add_argument('--segmented', metavar='FILE',
                        help='segmented file to use (if >1 in segmented/)')
    args = parser.parse_args()
    # do the job
    augment_game(args.dir_orig, args.dir_dest, args.doc, args.gen,
                 steps=args.steps,
                 seg_path=args.segmented)


if __name__ == '__main__':
    main()
