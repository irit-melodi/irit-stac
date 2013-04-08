#!/bin/bash
set -e

# Second half of the intake process:
#
# Given manually segmented (eg. in Excel) CSV file,
# prepare Glozz XML, do decoupage, etc
pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

if [ $# -ne 1 ]; then
    echo >&2 "Usage: $0 mapping"
    exit 1
fi

pushd $SCRIPT_DIR/../txt2csv > /dev/null
TXT2CSV_DIR=$PWD
popd > /dev/null
pushd $SCRIPT_DIR/../segmentation > /dev/null
SEGMENTATION_DIR=$PWD
popd > /dev/null

MAPPING_FILE=$1
while IFS=, read original clean; do
    mkdir -p $clean/soclog
    cp "$original" $clean/soclog

    mkdir -p $clean/{unsegmented,segmented}
    TURNS_FILE=$clean/turns
    python $TXT2CSV_DIR/extract_turns.py "$original" > $TURNS_FILE
    python $TXT2CSV_DIR/extract_annot.py $TURNS_FILE
    mv ${TURNS_FILE}csv $clean/unsegmented/${clean}.soclog.csv
    # presegment automatically (human would still have to clean up)
    python $SEGMENTATION_DIR/simple-segments  --csv\
        $clean/unsegmented/${clean}.soclog.csv\
        $clean/segmented/${clean}.soclog.seg.csv
    rm ${TURNS_FILE}
done < $MAPPING_FILE

#echo >&2 "Now edit segmented/$OUTPUT_BNAME.soclog.seg.csv (in eg. Excel)"
#echo >&2 "When done, run $SCRIPT_DIR/intake-2.sh on it"
