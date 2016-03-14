#!/bin/bash
set -e

# First half of the intake process:
# Given input file name and nice output filename
# Prepare file for segmentation
pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

pushd $SCRIPT_DIR/.. > /dev/null
CODE_DIR=$PWD
popd > /dev/null

if [ $# -lt 2 ]; then
    echo >&2 "Usage: $0 file.soclog clean-name"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_BNAME=$2
GEN2_LING_ONLY=$3
BATCH=$4

mkdir -p $OUTPUT_BNAME/{soclog,unsegmented,segmented}
cp "$INPUT_FILE" $OUTPUT_BNAME/soclog

CLEAN_SOCLOG=$OUTPUT_BNAME/unsegmented/${OUTPUT_BNAME}.soclog.csv
if [ "$GEN2_LING_ONLY" ]; then
    python $CODE_DIR/intake/soclogtocsv.py "$INPUT_FILE" --output "$CLEAN_SOCLOG" --gen2-ling-only
else
    python $CODE_DIR/intake/soclogtocsv.py "$INPUT_FILE" --output "$CLEAN_SOCLOG"
fi

# create aam file
python $SCRIPT_DIR/create-glozz-aam.py $CLEAN_SOCLOG $OUTPUT_BNAME/$OUTPUT_BNAME.aam

# presegment automatically (human would still have to clean up)
python $CODE_DIR/segmentation/simple-segments  --csv\
    $OUTPUT_BNAME/unsegmented/${OUTPUT_BNAME}.soclog.csv\
    $OUTPUT_BNAME/segmented/${OUTPUT_BNAME}.soclog.seg.csv

if [ -z "$BATCH" ]; then
    echo >&2 "Now edit segmented/$OUTPUT_BNAME.soclog.seg.csv (in eg. Excel)"
    echo >&2 "When done, run $SCRIPT_DIR/intake-2.sh on it"
fi
