# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
gather features
"""

from __future__ import print_function
import os
from os import path as fp

from attelo.harness.util import call, force_symlink

from ..local import\
    ALL_CORPUS, TRAINING_CORPORA, LEX_DIR, ANNOTATORS, WINDOW
from ..util import\
    current_tmp, latest_tmp, merge_csv

NAME = 'gather'


def config_argparser(parser):
    """
    Subcommand flags.

    You should create and pass in the subparser to which the flags
    are to be added.
    """
    parser.set_defaults(func=main)


def main(_):
    """
    Subcommand main.

    You shouldn't need to call this yourself if you're using
    `config_argparser`
    """
    tdir = current_tmp()
    window = -1 if WINDOW is None else WINDOW
    # edu pair and single edu feature extraction
    for corpus in TRAINING_CORPORA:
        extract_cmd = ["stac-learning", "extract", corpus, LEX_DIR,
                       tdir,
                       "--anno", ANNOTATORS,
                       "--window", str(window)]
        call(extract_cmd)
        call(extract_cmd + ["--single"])
    # combine *.foo.csv files for all corpora into an all.foo.csv
    for ext in ["edu-pairs", "relations", "just-edus"]:
        if not TRAINING_CORPORA:
            break
        csv_path = lambda f:\
            fp.join(tdir,
                    "%s.%s.csv" % (fp.basename(f), ext))
        merge_csv(map(csv_path, TRAINING_CORPORA),
                  csv_path(ALL_CORPUS))
    # log the features we used and version numbers for our infrastrucutre
    with open(os.path.join(tdir, "features.txt"), "w") as stream:
        call(["stac-learning", "features", LEX_DIR], stdout=stream)
    with open(os.path.join(tdir, "versions-gather.txt"), "w") as stream:
        call(["pip", "freeze"], stdout=stream)
    latest_dir = latest_tmp()
    force_symlink(os.path.basename(tdir), latest_dir)
