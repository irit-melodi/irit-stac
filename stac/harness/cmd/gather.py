# Author: Eric Kow
# License: CeCILL-B (French BSD3-like)

"""
gather features
"""

from __future__ import print_function
import os
from os import path as fp

from attelo.harness.util import (call, force_symlink, makedirs)

from ..local import (TRAINING_CORPUS, LEX_DIR, ANNOTATORS)
from ..util import (current_tmp, latest_tmp)

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
    makedirs(tdir)
    # edu pair and single edu feature extraction
    extract_cmd = ["stac-learning", "extract", TRAINING_CORPUS, LEX_DIR,
                   tdir,
                   "--anno", ANNOTATORS]
    call(extract_cmd)
    call(extract_cmd + ["--single"])
    with open(os.path.join(tdir, "versions-gather.txt"), "w") as stream:
        call(["pip", "freeze"], stdout=stream)
    latest_dir = latest_tmp()
    force_symlink(fp.basename(tdir), latest_dir)
