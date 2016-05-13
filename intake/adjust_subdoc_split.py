"""This script aims at adjusting subdoc splits in the "segmented" files.

In the first and second generations of the STAC corpus, the "segmented"
files contain Server turns that are not included in the glozz aa/ac
files.
Game portioning (a.k.a. subdoc split) frequently happens during a
player turn, causing the initial Server messages (dice roll, resources)
to belong to the preceding subdoc.
This is problematic for the third (and subsequent) generations of the
corpus, where non-linguistic events are included in the glozz aa/ac
files.
"""

from __future__ import print_function

import argparse
import csv
from glob import glob
import os


def adjust_split(corpus_dir, doc):
    """Do the job"""
    corpus_dir = os.path.abspath(corpus_dir)
    game_dir = os.path.join(corpus_dir, doc)
    if not os.path.isdir(game_dir):
        raise ValueError('Unable to find directory {}'.format(game_dir))
    # locate segmented file
    seg_dir = os.path.join(game_dir, 'segmented')
    seg_orig = glob(os.path.join(seg_dir,
                                 doc + '*.soclog.seg.csv'))
    if len(seg_orig) != 1:
        raise ValueError(
            'Unable to locate segmented file {}'.format(seg_orig))
    seg_orig = seg_orig[0]
    seg_new = seg_orig + '.new'
    # go through the file, line by line
    with open(seg_orig, 'rb') as seg_f:
        with open(seg_new, 'wb') as new_f:
            reader = csv.reader(seg_f, delimiter='\t')
            writer = csv.writer(new_f, delimiter='\t', lineterminator='\n')
            # leave header line
            line = reader.next()
            writer.writerow(line)
            # buffer sequences of "Server" messages immediately before a
            # subdoc split should be buffered so that the subdoc split
            # can be adjusted
            server_turns = []
            # regular lines
            for line in reader:
                if (not line
                    or not ''.join(line).strip()):
                    # empty line: subdoc split
                    server_turns_it = iter(server_turns)
                    # discharge the Server turns before and after the
                    # subdoc split
                    for server_turn in server_turns_it:
                        if 'rolled a' in server_turn[5]:
                            # split at the first dice roll, which is our
                            # best clue for the beginning of a new player
                            # turn in gen. 1-2 of the corpus
                            writer.writerow(line)
                            writer.writerow(server_turn)
                            break
                        # write before the subdoc split
                        writer.writerow(server_turn)
                    else:
                        # no dice roll in the buffered server turns, so
                        # write the empty line
                        writer.writerow(line)
                    # write remaining server turns (if any) after the
                    # subdoc split
                    for server_turn in server_turns_it:
                        writer.writerow(server_turn)
                    # reset buffer
                    server_turns = []
                elif line[2] == 'Server':
                    # Server turns: buffer them
                    server_turns.append(line)
                else:
                    # write buffered Server turns + the current
                    # non-Server turn
                    for server_turn in server_turns:
                        writer.writerow(server_turn)
                    # reset buffer
                    server_turns = []
                    # write non-Server turn
                    writer.writerow(line)
    # replace original segmented file with the clean one
    os.rename(seg_new, seg_orig)


def main():
    """Adjust subdoc split for a game."""
    parser = argparse.ArgumentParser(
        description="Adjust subdoc split in a game segmented file"
    )
    parser.add_argument('corpus_dir', metavar='DIR',
                        help='folder of the annotated corpus')
    parser.add_argument('doc', metavar='DOC',
                        help='document')
    args = parser.parse_args()
    adjust_split(args.corpus_dir, args.doc)


if __name__ == '__main__':
    main()
