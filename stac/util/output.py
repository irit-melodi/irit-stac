# Author: Eric Kow
# License: BSD3

"""
Help writing out corpus files
"""

import copy
import os
from cStringIO import StringIO

from educe import glozz
from educe.stac import stac_output_settings, stac_unannotated_output_settings
import educe.stac

# ---------------------------------------------------------------------
# stac utilities
# ---------------------------------------------------------------------


def output_path_stub(odir, k):
    """
    Given an output directory and an educe corpus key, return a 'stub' output
    path in that directory. This is dirname and basename only; you probably
    want to tack a suffix onto it.

    Example: given something like "/tmp/foo" and a key
    like `{author:"bob", stage:units, doc:"pilot03", subdoc:"07"}` you might
    get something like `/tmp/foo/pilot03/units/pilot03_07`)
    """
    relpath = educe.stac.id_to_path(k)
    ofile_dirname = os.path.join(odir, os.path.dirname(relpath))
    ofile_basename = os.path.basename(relpath)
    return os.path.join(ofile_dirname, ofile_basename)


def mk_parent_dirs(filename):
    """
    Given a filepath that we want to write, create its parent directory as
    needed.
    """
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def save_document(output_dir, k, doc):
    """
    Save a document as a Glozz .ac/.aa pair
    """
    stub = output_path_stub(output_dir, k)
    mk_parent_dirs(stub)
    doc_bytes = doc.text().encode('utf-8')
    is_unannotated = k.stage == 'unannotated'

    # .aa file
    settings = stac_unannotated_output_settings\
        if is_unannotated else stac_output_settings
    out_doc = copy.copy(doc)
    out_doc.hashcode = glozz.hashcode(StringIO(doc_bytes))
    glozz.write_annotation_file(stub + ".aa", out_doc, settings=settings)

    # .ac file
    if is_unannotated:
        with open(stub + ".ac", 'wb') as fout:
            fout.write(doc_bytes)
