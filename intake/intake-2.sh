#!/bin/bash
shopt -s nullglob
set -e

# Second half of the intake process:
#
# Given manually segmented (eg. in Excel) CSV file,
# prepare Glozz XML, do decoupage, etc
pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

CODE_DIR=$SCRIPT_DIR/..
pushd $CODE_DIR > /dev/null
CODE_DIR=$PWD
popd > /dev/null

if [ $# -ne 1 ]; then
    echo >&2 "Usage: $0 file.soclog.seg.csv"
    exit 1
fi

INPUT_FILE=$1
INPUT_DNAME=$(dirname  $INPUT_FILE)
INPUT_BNAME=$(basename $INPUT_FILE .soclog.seg.csv)
# if this is run as a successor to the intake-1 script
if [ "$(dirname $INPUT_DNAME)" == "${INPUT_BNAME}" ]; then
    cd ${INPUT_DNAME}/..
    INPUT_DNAME=$(basename $INPUT_DNAME)
    INPUT_FILE=${INPUT_DNAME}/$(basename $INPUT_FILE)
    STANDARD_MODE=1
fi

mkdir -p sections unannotated units discourse

echo >&2 '== Splitting into sections == [sections/*.soclog.seg.csv]'
python $CODE_DIR/txt2csv/split_csv.py $INPUT_FILE
python $SCRIPT_DIR/rename-series.py $INPUT_FILE --verbose
mv ${INPUT_DNAME}/${INPUT_BNAME}_*.soclog.seg.csv sections

echo >&2 '== Writing Glozz am/ac files == [unannotated/*.{ac,aa}]'
for i in sections/*.soclog.seg.csv; do
    echo $i
    python $CODE_DIR/csv2glozz/csvtoglozz.py -f $i
done
mv sections/*.{aa,ac} unannotated

if [ "$STANDARD_MODE" == "1" ]; then
    echo >&2 '== Creating zip file for annotators =='
    cd ..
    mkdir -p for-annotators/$INPUT_BNAME
    cp $INPUT_BNAME/*.aam $INPUT_BNAME/unannotated/* for-annotators/$INPUT_BNAME
    cd for-annotators
    zip -r $INPUT_BNAME.zip $INPUT_BNAME
    cd ..
fi
