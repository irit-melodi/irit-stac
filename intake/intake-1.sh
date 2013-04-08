#!/bin/bash
set -e

# Second half of the intake process:
#
# Given manually segmented (eg. in Excel) CSV file,
# prepare Glozz XML, do decoupage, etc
pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

if [ $# -ne 2 ]; then
    echo >&2 "Usage: $0 file.soclog clean-name"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_BNAME=$2

pushd $SCRIPT_DIR/../txt2csv > /dev/null
TXT2CSV_DIR=$PWD
popd > /dev/null

mkdir -p unsegmented
mkdir -p segmented

TURNS_FILE=$OUTPUT_BNAME.turns
python $TXT2CSV_DIR/extract_turns.py $INPUT_FILE > $TURNS_FILE
python $TXT2CSV_DIR/extract_annot.py $TURNS_FILE
cp ${TURNS_FILE}csv unsegmented/${OUTPUT_BNAME}.soclog.csv
cp ${TURNS_FILE}csv segmented/${OUTPUT_BNAME}.soclog.seg.csv
rm $TURNS_FILE ${TURNS_FILE}csv

echo >&2 "Now edit segmented/$OUTPUT_BNAME.soclog.seg.csv (in eg. Excel)"
echo >&2 "When done, run $SCRIPT_DIR/intake-2.sh on it"
