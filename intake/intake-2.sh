#!/bin/bash
shopt -s nullglob

# Second half of the intake process:
#
# Given manually segmented (eg. in Excel) CSV file,
# prepare Glozz XML, do decoupage, etc
pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

if [ $# -ne 1 ]; then
    echo >&2 "Usage: $0 file.soclog.csv"
    exit 1
fi

INPUT_FILE=$1
INPUT_DNAME=$(dirname  $INPUT_FILE)
# if this is run as a successor to the intake-1 script
if [ "$(basename $INPUT_DNAME)" == "segmented" ]; then
    cd ${INPUT_DNAME}/..
    INPUT_DNAME=segmented
    INPUT_FILE=${INPUT_DNAME}/$(basename $INPUT_FILE)
fi
INPUT_BNAME=$(basename $INPUT_FILE .soclog.seg.csv)


mkdir -p split unannotated units discourse
CSV2GLOZZ_DIR=$SCRIPT_DIR/../csv2glozz
pushd $CSV2GLOZZ_DIR > /dev/null
CSV2GLOZZ_DIR=$PWD
popd > /dev/null

python $CSV2GLOZZ_DIR/splitcsv.py $INPUT_FILE
mv ${INPUT_DNAME}/${INPUT_BNAME}_*.soclog.seg.csv split

python $SCRIPT_DIR/create-glozz-aam.py $INPUT_FILE $INPUT_BNAME.aam

echo >&2 "Now edit the decoupage in split/* by trimming lines"
echo >&2 "in your text editor, or moving them between files."
echo >&2 "You can add or delete files as needed"
echo >&2
echo >&2 "After that, run ./intake-3.sh on the split directory"
