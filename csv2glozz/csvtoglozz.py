#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
The program takes (optionally segmented) CSV files as inputs, processes the segment information (the "&"s) if applicable, and outputs an (.ac, .aa) pair of Glozz files.

The output files contain:
    - the .ac file will contain the text attributes of the dialogue turns (without the '&', one turn on a line).
    - the .aa file will contain:
        - a pre-annotation in terms of:
            - dialogue information:
                - cut at dice rollings;
                - trades,
                - dice rollings,
                - resource gettings.
            - turn information:
                - borders (implicit)
                - Identifier
                - Timestamp
                - Emitter
                - Resources
                - Developments
            - segment (UDE) information:
                - borders (implicit)
                - Shallow dialogue act: Question | Request | Assertion
                - Task dialogue act: Offer | Counteroffer | Accept | Refusal | Strategic_comment | Other

Usage:
>>> ./csvtoglozz.py -f <CSV file name>

@note: The output file names are formed by appending the .ac and .aa extensions to the input CSV file basename.
Example: for an input filename like document1.soclog.seg.csv, the pair  (document1.ac, document1.aa) is generated.
@note: The program supports filenames with empty spaces in them.
@note: Glozz is 0-indexed (but our .ac files systematically start with a space)
'''

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import copy
import csv, sys, codecs
import datetime, time

from stac.prettifyxml import prettify

def append_unit(root, unit_id, date, type, features, left, right):
    if right < left:
        raise Exception("Span with right boundary less than left")

    metadata = [ ('author'              , 'stac')
               , ('creation-date'       , str(date))
               , ('lastModifier'        , 'n/a' )
               , ('lastModificationDate', '0'   )
               ]
    elm_unit     = SubElement(root, 'unit', {'id':unit_id})
    elm_metadata = SubElement(elm_unit, 'metadata')
    for k,v in metadata:
        e = SubElement(elm_metadata, k)
        e.text = v
    elm_charact = SubElement(elm_unit, 'characterisation')
    elm_type    = SubElement(elm_charact, 'type')
    elm_type.text = type
    elm_features = SubElement(elm_charact, 'featureSet')
    for k,v in features:
        e = SubElement(elm_features, 'feature', {'name':k})
        e.text = v

    elm_pos   = SubElement(elm_unit, 'positioning')
    elm_start = SubElement(elm_pos, 'start')
    elm_end   = SubElement(elm_pos, 'end')
    SubElement(elm_start, 'singlePosition', {'index':str(left)})
    SubElement(elm_end  , 'singlePosition', {'index':str(right)})

class PlayerTurn:
    """
    High-level representation of a turn

    This is a refactor in progress of the main loop below.
    """
    def __init__(self, number, timestamp, emitter, res, builds, text, annot, comment):
        self.number    = number
        self.timestamp = timestamp
        self.emitter   = emitter
        self.res       = res
        self.builds    = builds
        self.text      = text
        self.annot     = annot
        self.comment   = comment

def read_row(row):
    """
    Either the contents of the row or None if it's server content
    """
    the_row = copy.copy(row)
    if len(the_row) >= 6 and len(the_row) < 8:
        padding = [''] * (8 - len(the_row))
        the_row.extend(padding)
    [turn_id, timestamp, emitter, res, builds, seg_text, annot, comment] = the_row
    if emitter != "Server":
        clean_text = seg_text.replace('&','')
        return PlayerTurn(number    = turn_id,
                          timestamp = timestamp,
                          emitter   = emitter,
                          res       = res,
                          builds    = builds,
                          text      = '%s : %s : %s ' % (turn_id, emitter, clean_text),
                          annot     = annot,
                          comment   = comment)
    else:
        return None

def whole_text(csvrows):
    """
    The text that we would use in an .ac file

    This duplicates the functionality in the main processing loop below, as that code
    is a bit complicated and there's a good chance my refactor would break something.
    """
    dialoguetext = ' ' # for the .ac file
    for i, row in enumerate(csvrows,1):
        try:
            turn = read_row(row)
        except ValueError:
            print >> sys.stderr, "Error on row %d: %s" % (i, the_row)
            raise
        if turn is not None:
            dialoguetext += turn.text
    return dialoguetext

def utf8_csv_reader(utf8_data, **kwargs):
    """
    Read utf-8 encoded CSV data as Unicode strings.

    The issue here is that the Python csv library seems to work on bytestrings.
    To work with arbitrary Unicode files, they do this thing where they encode
    the Unicode into UTF-8 on read (yes, encode), and decode it back.  This
    seems rather silly to do if you already know the encoding is UTF-8 and you
    just want the Unicode behind it.
    """
    csv_reader = csv.reader(utf8_data, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

# TODO: replace with XML declaration
root = Element('annotations', {'version':'1.0', 'encoding':'UTF-8', 'standalone':'no'})
root.append(Comment('Generated by csvtoglozz.py'))

import argparse
parser = argparse.ArgumentParser(description = '')
parser.add_argument('-f', '--file', dest = 'file', nargs = '+', help = "specify input file")
args = parser.parse_args(sys.argv[1:])
filename = ' '.join(args.file)

incsvfile = open(filename, 'rt') # bytestring
csvreader = utf8_csv_reader(incsvfile, delimiter='\t')
firstcsvrow = csvreader.next()
dialoguetext = ' ' # for the .ac file
i=0
nb_dialogues = 0
dialog_leftborders = []
dialog_rightborders = []
csvrows = list(csvreader)
r_old = 0

def mk_id():
    """
    Pair containing a brand new id and (false) creation-date
    """
    mk_id.counter += 1
    fake_timestamp = mk_id.starting_time + mk_id.counter
    the_id = '_'.join(['stac', str(fake_timestamp)])
    return (the_id, fake_timestamp)

# not sure why this is preferable to time.time()
# inherited it from the old version of the code
mk_id.starting_time = int(time.mktime(datetime.datetime.now().timetuple()))
mk_id.counter = 0

for r in range(0,len(csvrows)):
    i += 1
    if csvrows[r] != firstcsvrow:
        try:
            the_row = copy.copy(csvrows[r])
            if len(the_row) >= 6 and len(the_row) < 8:
                padding = [''] * (8 - len(the_row))
                the_row.extend(padding)
            [curr_turn_id, curr_turn_timestamp, curr_turn_emitter, curr_turn_res, curr_turn_builds, curr_turn_text, curr_turn_annot, curr_turn_comment] = the_row
        except ValueError:
            print >> sys.stderr, "Error on row %d: %s" % (i, the_row)
            raise
    if curr_turn_emitter != "Server":
        dialoguetext  +=curr_turn_id+' : '+curr_turn_emitter+' : '
        next_seg_left = len(dialoguetext)
        curr_turn_segments = [ x for x in curr_turn_text.split('&') if len(x) > 0 ]
        seg_spans  = []
        for tseg in curr_turn_segments:
            tseg_l        = tseg.lstrip()
            tseg_lr       = tseg_l.rstrip()
            padding_left  = len(tseg)   - len(tseg_l)
            padding_right = len(tseg_l) - len(tseg_lr)
            tmp_seg_left  = next_seg_left + padding_left
            tmp_seg_right = tmp_seg_left  + len(tseg_lr)
            next_seg_left = tmp_seg_right + padding_right
            seg_spans.append((tmp_seg_left, tmp_seg_right))

        # .ac buffer
        curr_turn_text = "".join(curr_turn_segments)
        dialoguetext  += curr_turn_text + ' '
        # .aa typographic annotations
        typid, typdate = mk_id()

        if dialoguetext.index(curr_turn_text) != 0:
            typstart = len(dialoguetext) - len(curr_turn_text) - len(curr_turn_id) - len(curr_turn_emitter) - 1 - 6
        else:
            typstart = 0
        typend = len(dialoguetext)-1

        append_unit(root,
                    unit_id  = typid,
                    date     = typdate,
                    type     = 'paragraph',
                    features = [],
                    left     = typstart,
                    right    = typend)

        # .aa actual pre-annotations (Turn ID, Timestamp, Emitter)
        # a "Dialogue" Unit should be added, that is, Turns between Server's contributions containing "rolled"
        unitid, creation_date = mk_id()

        # To parse and (re)present in a suitable manner !
        curr_parsed_turn_builds = ""
        if len(curr_turn_builds) > 0:
            for item in curr_turn_builds.split("];"):
                if ']' not in item:
                    item += ']'
                curr_parsed_turn_builds += item.split("=")[0]
                curr_parsed_turn_builds += "="
                curr_parsed_turn_builds += str(len(set(eval(item.split("=")[1].replace("; ", ",")))))
                curr_parsed_turn_builds += "; "
        curr_parsed_turn_builds = curr_parsed_turn_builds.strip("; ")

        features = [ ('Identifier', curr_turn_id)
                   , ('Timestamp' , curr_turn_timestamp)
                   , ('Emitter'   , curr_turn_emitter)
                   , ('Resources' , curr_turn_res.split("; unknown=")[0])
                   , ('Developments', curr_parsed_turn_builds)
                   , ('Comments', 'Please write in remarks...')
                   ]

        if dialoguetext.index(curr_turn_text) != 0:
            actualstpos = len(dialoguetext)-len(curr_turn_text)-len(curr_turn_id)-len(curr_turn_emitter)-1-6
        else:
            actualstpos = 0
        actualendpos = len(dialoguetext)-1

        append_unit(root,
                    unit_id  = unitid,
                    date     = creation_date,
                    type     = 'Turn',
                    features = features,
                    left     = actualstpos,
                    right    = actualendpos)

        # Segments information
        for sp in seg_spans:
            segment_id, screation_date = mk_id()
            append_unit(root,
                        unit_id  = segment_id,
                        date     = screation_date,
                        type     = 'Segment',
                        features = [],
                        left     = sp[0],
                        right    = sp[1])

    if curr_turn_emitter == "Server" and "rolled a" in curr_turn_text: # dialogue right boundary
    # hence, a dialogue is between the beginning and such a text (minus server's turns), or between such a text + 1 and another such text (minus server's turns).
        dice_rollings = []
        gets = []
        trades = ''
        #trades = []
        for rr in range(r+1,len(csvrows)):
            if csvrows[rr][2] == 'Server':
                if 'rolled a' in csvrows[rr][5]:
                    # append to Dice_rolling feature values
                    dice_rollings.append(csvrows[rr][5])
                if 'gets' in csvrows[rr][5]:
                    # append to Gets feature values
                    gets.append(csvrows[rr][5])
            else:
                break
        #print "r_old : " + str(r_old)
        for rrr in range(r, r_old-1, -1):
            if csvrows[rrr][2] == 'Server' and 'traded' in csvrows[rrr][5]:
                # append to Trades feature values
                trades = csvrows[rrr][5]
                break
#        print nb_dialogues
        #print dialog_leftborders
        #print dialog_rightborders
        r_old = r
        if nb_dialogues == 0:
            dialog_leftborders = [0]
            dialog_rightborders = [len(dialoguetext)-1]
        else:
            dialog_leftborders.append(dialog_rightborders[-1])
            dialog_rightborders.append(len(dialoguetext)-1)
        nb_dialogues += 1
        # Generate the actual annotation !
        if dialog_leftborders[-1] != dialog_rightborders[-1]:
            dialogue_id, dcreation_date = mk_id()

            # extra rollings
            delfDiceroll = curr_turn_text
            if len(dice_rollings) >= 1:
                for roll in range(0,len(dice_rollings)):
                    delfDiceroll += ' '+dice_rollings[roll]
            # extra gets
            delfGets = ''
            if len(gets) >= 1:
                for get in range(0,len(gets)):
                    delfGets += ' '+gets[get]
            # extra trades
            delfTrades = trades
            #if len(trades) >= 1:
            #    for trade in range(0,len(trades)):
            #        delfTrades.text += ' '+trades[trade]

            dfeatures = [ ('Dice_rolling', delfDiceroll)
                        , ('Gets'        , delfGets)
                        , ('Trades'      , delfTrades)
                        ]

            append_unit(root,
                        unit_id  = dialogue_id,
                        date     = dcreation_date,
                        type     = 'Dialogue',
                        features = dfeatures,
                        left     = dialog_leftborders[-1],
                        right    = dialog_rightborders[-1])

# last dialogue : only if it doesn't end in a Server's statement !!

if len(dialog_rightborders) == 0 or dialog_rightborders[-1] != len(dialoguetext)-1:

    unit_id, creation_date = mk_id()

    if len(dialog_rightborders) >= 1:
        span_left = dialog_rightborders[-1]
    else:
        span_left = 0
    span_right = len(dialoguetext)

    append_unit(root,
                unit_id    = unit_id,
                date       = creation_date,
                type       = 'Dialogue',
                features   = [],
                left       = span_left,
                right      = span_right)

#for b in range(0,len(dialog_leftborders)):
#    print ">>>>>>>>>>>"
#    print dialoguetext[dialog_leftborders[b]:dialog_rightborders[b]]
#    print "<<<<<<<<<<<"

basename=filename.split(".")[0]
outtxtfile = codecs.open(basename+".ac", "w", "utf-8")
outtxtfile.write(dialoguetext)
outtxtfile.close()
outxmlfile = codecs.open(basename+".aa", "w", "ascii")
outxmlfile.write(prettify(root))
outxmlfile.close()
