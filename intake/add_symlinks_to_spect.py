"""Add links to games with no spectator message in the _spect folders.

"""

from __future__ import print_function

import argparse
import glob
import os


def main():
    """Add symlinks
    """
    # argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('src',
                        help='source folder')
    parser.add_argument('dst',
                        help='destination folder')
    args = parser.parse_args()

    # do the job: create a symlink for each match of the pattern
    src_folder = os.path.abspath(args.src)
    dst_folder = os.path.abspath(args.dst)
    os.chdir(dst_folder)

    for src in glob.glob(src_folder + '/*'):
        src = os.path.abspath(src)
        game_name = os.path.split(src)[-1]
        if not os.path.isdir(game_name):
            os.symlink(os.path.relpath(src), game_name)


if __name__ == '__main__':
    main()
