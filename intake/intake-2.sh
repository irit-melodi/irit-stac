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

mkdir -p split unannotated units discourse

INPUT_FILE=$1
INPUT_DNAME=$(dirname  $INPUT_FILE)
INPUT_BNAME=$(basename $INPUT_FILE .soclog.seg.csv)

CSV2GLOZZ_DIR=$SCRIPT_DIR/../csv2glozz
pushd $CSV2GLOZZ_DIR > /dev/null
CSV2GLOZZ_DIR=$PWD
popd > /dev/null

python $CSV2GLOZZ_DIR/splitcsv.py $INPUT_FILE
mv ${INPUT_DNAME}/${INPUT_BNAME}_*.soclog.seg.csv split

for i in split/*.soclog.seg.csv; do
    python $CSV2GLOZZ_DIR/csvtoglozz.py -f $i
done
mv split/*.{aa,ac} unannotated
python $SCRIPT_DIR/create-glozz-aam.py $INPUT_FILE $INPUT_BNAME.aam
