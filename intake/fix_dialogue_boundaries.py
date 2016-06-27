"""Small utility script to fix dialogue boundaries in situated games.

For the first few games woven as situated, the weaving script was using
a poor strategy to shift and adjust dialogue boundaries.
This script aims at fixing existing woven games that have already been
annotated and reviewed by JH, NA, SK (in alphabetical order).
"""

from __future__ import print_function

import argparse
import copy
from functools import reduce
import itertools
import os

import numpy as np

from educe.annotation import Span
from educe.stac.annotation import game_turns, is_dialogue, is_turn
from educe.stac.corpus import Reader
from educe.stac.edit.cmd.split_dialogue import _set  # DIRTY !
from educe.stac.edit.cmd.merge_dialogue import _concatenate_features  # DIRTY
from educe.stac.util.glozz import TimestampCache
from educe.stac.util.output import save_document


def _fix_dialogue_boundaries(tcache, doc_ling, doc_situ):
    """Do the job.

    Parameters
    ----------
    tcache: TimestampCache
        Timestamp cache to generate unit identifiers for new dialogues.
    doc_ling: GlozzDocument
        Linguistic version of the game.
    doc_situ: GlozzDocument
        Situated version of the game.

    Returns
    -------
    doc_situ: GlozzDocument
        Fixed version of doc_situ.
    """
    doc_key = doc_situ.origin

    # 1. get the identifier of the first and last turn of each game turn
    # in _situ: these turns and those in between must end up in the same
    # dialogue
    turns_situ = sorted((x for x in doc_situ.units if is_turn(x)),
                        key=lambda x: x.span)
    turns_situ_tid = np.array([x.features['Identifier'] for x in turns_situ])
    turns_situ_beg = np.array([x.span.char_start for x in turns_situ])
    turns_situ_end = np.array([x.span.char_end for x in turns_situ])
    # * locate game turns (index of first and last turn)
    gturn_idc = game_turns(doc_situ, turns_situ, gen=3)
    gturn_idc_beg = np.array(gturn_idc)
    gturn_idc_end = np.array(
        [i - 1 for i in gturn_idc[1:]] + [len(turns_situ) - 1])
    # ... and finally
    gturn_situ_tid_beg = turns_situ_tid[gturn_idc_beg]
    gturn_situ_tid_end = turns_situ_tid[gturn_idc_end]
    # print('game turns in _situ', zip(gturn_situ_tid_beg, gturn_situ_tid_end))

    # 2. get the identifier of the first and last turn of each dialogue in
    # _ling: these turns and those in between must end up in the same
    # dialogue
    turns_ling = sorted((x for x in doc_ling.units if is_turn(x)),
                        key=lambda x: x.span)
    # DIRTY special processing for pilot02_01
    if doc_key.doc == 'pilot02' and doc_key.subdoc == '01':
        # ignore turns 26-27 that were moved down from _01 to _02
        turns_ling = turns_ling[:-2]
    turns_ling_tid = np.array([x.features['Identifier'] for x in turns_ling])
    turns_ling_beg = np.array([x.span.char_start for x in turns_ling])
    turns_ling_end = np.array([x.span.char_end for x in turns_ling])
    # align dialogue spans with turn spans
    dlgs_ling = sorted((x for x in doc_ling.units if is_dialogue(x)),
                       key=lambda x: x.span)
    # DIRTY
    if doc_key.doc == 'pilot02' and doc_key.subdoc == '01':
        # turns 26-27 are in the last dialogue in _01, in _ling
        dlgs_ling = dlgs_ling[:-1]
    dlgs_ling_beg = np.array([x.span.char_start for x in dlgs_ling])
    dlgs_ling_end = np.array([x.span.char_end for x in dlgs_ling])
    dlgs_ling_ti_beg = np.searchsorted(turns_ling_beg, dlgs_ling_beg)
    dlgs_ling_ti_end = np.searchsorted(turns_ling_end, dlgs_ling_end,
                                       side='right') - 1
    # ... and finally
    dlgs_ling_tid_beg = turns_ling_tid[dlgs_ling_ti_beg]
    dlgs_ling_tid_end = turns_ling_tid[dlgs_ling_ti_end]
    # print('dialogues in _ling', zip(dlgs_ling_tid_beg, dlgs_ling_tid_end))

    # 3. map _ling dialogues to _situ game turns
    # * locate the first and last turn of each _ling dialogue in the
    # list of turns in _situ
    # NB: we don't need indices in the list of turns from _ling anymore
    # hence it is safe to overwrite dlgs_ling_ti_{beg,end}
    dlgs_ling_ti_beg = np.array(
        [list(turns_situ_tid).index(x) for x in dlgs_ling_tid_beg])
    dlgs_ling_ti_end = np.array(
        [list(turns_situ_tid).index(x) for x in dlgs_ling_tid_end])
    # print('game turns (turn_idx)', zip(gturn_idc_beg, gturn_idc_end))
    # print('core dlgs (turn_idx)', zip(dlgs_ling_ti_beg, dlgs_ling_ti_end))
    # * align the beginning (resp. end) indices of game turns and _ling
    # dialogues
    dlg2gturn_beg = (np.searchsorted(gturn_idc_beg, dlgs_ling_ti_beg,
                                     side='right') - 1)
    dlg2gturn_end = np.searchsorted(gturn_idc_end, dlgs_ling_ti_end)
    # print('map from dlg to gturn', zip(dlg2gturn_beg, dlg2gturn_end))
    # * turn indices of the adjusted beginning and end of the _ling
    # dialogues
    # initialize along the boundaries of game turns
    dlg_ling_situ_abeg = [gturn_idc_beg[i] for i in dlg2gturn_beg]
    dlg_ling_situ_aend = [gturn_idc_end[i] for i in dlg2gturn_end]

    # 4. make dialogue boundaries coincide with game turn boundaries,
    # which occasionally implies merging dialogues from _ling

    # * compute a partition on dialogues such that any pair of
    # dialogues overlapping a given game turn are in the same
    # class
    dlg2grp = [0]
    for i, (gturn_end_cur, gturn_beg_nxt) in enumerate(zip(
            dlg2gturn_end[:-1], dlg2gturn_beg[1:])):
        if gturn_beg_nxt <= gturn_end_cur:
            # two _ling dialogues overlap a single game turn:
            # put in the same class (to merge dialogues)
            dlg2grp.append(dlg2grp[-1])
        else:
            dlg2grp.append(dlg2grp[-1] + 1)

    # remove all dialogues from the units in doc_situ,
    # they will be replaced with (hopefully) clean ones
    dlgs_situ = sorted((x for x in doc_situ.units if is_dialogue(x)),
                       key=lambda x: x.span)
    for dlg_situ in dlgs_situ:
        doc_situ.units.remove(dlg_situ)

    # create one dialogue for each class of dialogues
    for k, g in itertools.groupby(enumerate(dlg2grp),
                                  key=lambda x: x[1]):
        dlg_idc_merged = [x[0] for x in g]
        # adjust boundaries of the first dialogue of the group
        # index of first and last dialogues
        di_beg = dlg_idc_merged[0]
        di_end = dlg_idc_merged[-1]
        # index of first and last turns of these dialogues
        ti_beg = dlg_ling_situ_abeg[di_beg]
        ti_end = dlg_ling_situ_aend[di_end]
        # create dialogue, use the 1st _ling dialogue as basis then
        # customize
        dlg0 = dlgs_ling[di_beg]
        new_dlg = copy.deepcopy(dlg0)
        new_dlg.origin = doc_key
        new_dlg.span.char_start = turns_situ_beg[ti_beg]
        new_dlg.span.char_end = turns_situ_end[ti_end]
        dlgs_ling_merged = [dlgs_ling[i] for i in dlg_idc_merged]
        for feat in ['Trades', 'Gets', 'Dice_rolling']:
            new_dlg.features[feat] = _concatenate_features(
                dlgs_ling_merged, feat)
        # add the new dialogue to doc_situ
        doc_situ.units.append(new_dlg)

    # create a new dialogue for each unmatched (non-overlapping) game
    # turn
    gturns_matched = reduce(np.union1d,
                            (np.arange(x_beg, x_end + 1)
                             for x_beg, x_end
                             in zip(dlg2gturn_beg, dlg2gturn_end)))
    gturns_matched = set(gturns_matched)
    for i, (gturn_idx_beg, gturn_idx_end) in enumerate(zip(
            gturn_idc_beg, gturn_idc_end)):
        if i not in gturns_matched:
            new_dlg_span = Span(turns_situ_beg[gturn_idx_beg],
                                turns_situ_end[gturn_idx_end])
            # UGLY this works just like split_dialogue:
            # create a new dialogue by copying an existing dialogue,
            # re-assign it an annotation id and span using a timestamp
            # cache, then erase all features
            new_dlg = copy.deepcopy(dlgs_situ[0])
            _set(tcache, new_dlg_span, new_dlg)
            new_dlg.features = {}
            # ... "et voila": add this dialogue to the document
            doc_situ.units.append(new_dlg)

    # TODO restore dialogue features from the game events?
    return doc_situ


def fix_dialogue_boundaries(dir_ling, dir_situ, doc, seg_path=None):
    """Fix dialogue boundaries in a woven game.

    Dialogue boundaries are adjusted in the woven version, so they
    are tighter around the dialogues that existed in the annotated
    version.

    Parameters
    ----------
    dir_ling: filepath
        Path to the folder of the original version of the game.
    dir_situ: filepath
        Path to the folder of the woven version of the game.
    doc: string
        Name of the game.
    seg_path: TODO
        TODO ?
    """
    # select files for this game only, annotator GOLD
    is_interesting = lambda k: (k.doc == doc
                                and (k.annotator == 'GOLD'
                                     or k.annotator is None))

    # locate files
    dir_ling = os.path.abspath(dir_ling)
    reader_ling = Reader(dir_ling)
    files_ling = reader_ling.filter(reader_ling.files(), is_interesting)
    corpus_ling = reader_ling.slurp(cfiles=files_ling, verbose=True)

    dir_situ = os.path.abspath(dir_situ)
    reader_situ = Reader(dir_situ)
    files_situ = reader_situ.filter(reader_situ.files(), is_interesting)
    corpus_situ = reader_situ.slurp(cfiles=files_situ, verbose=True)
    # need a TimestampCache to generate unit_id for new dialogues
    tcache = TimestampCache()

    for key, doc_situ in sorted(corpus_situ.items()):
        doc_ling = corpus_ling[key]
        print(key)
        doc_situ_fixed = _fix_dialogue_boundaries(tcache, doc_ling, doc_situ)
        # DEBUG
        dlgs = sorted((x for x in doc_situ_fixed.units if is_dialogue(x)),
                      key=lambda x: x.span)
        dlg_beg = [x.span.char_start for x in dlgs]
        dlg_end = [x.span.char_end for x in dlgs]
        print(zip(dlg_beg, dlg_end))
        # end DEBUG
        save_document(dir_situ, key, doc_situ_fixed)


def main():
    """Fix dialogue boundaries in a woven game."""
    # parse command line
    parser = argparse.ArgumentParser(
        description='Fix dialogue boundaries in a woven game')
    parser.add_argument('dir_ling', metavar='DIR',
                        help='folder of the linguistic corpus')
    parser.add_argument('dir_situ', metavar='DIR',
                        help='folder for the situated corpus')
    parser.add_argument('doc', metavar='DOC',
                        help='document')
    # explicitly point to segmented (in case there is more than one in
    # the segmented/ folder)
    parser.add_argument('--segmented', metavar='FILE',
                        help='segmented file to use (if >1 in segmented/)')
    args = parser.parse_args()
    # do the job
    fix_dialogue_boundaries(args.dir_ling, args.dir_situ, args.doc,
                            seg_path=args.segmented)


if __name__ == '__main__':
    main()
