#!/bin/bash
shopt -s nullglob

# Third automated step of the intake process:
#
# Given segmented and now split CSV files, prepare Glozz XML

pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

if [ $# -ne 1 ]; then
    echo >&2 "Usage: $0 split-dir"
    exit 1
fi

cd $(dirname  $1)
SPLIT_DIR=$(basename $1)
if [ ! -d "$SPLIT_DIR" ]; then
    echo >&2 "$1 is not a directory"
    exit 1
fi

mkdir -p unannotated units discourse

CSV2GLOZZ_DIR=$SCRIPT_DIR/../csv2glozz
pushd $CSV2GLOZZ_DIR > /dev/null
CSV2GLOZZ_DIR=$PWD
popd > /dev/null

for i in $SPLIT_DIR/*.soclog.seg.csv; do
    echo $i
    python $CSV2GLOZZ_DIR/csvtoglozz.py -f $i
done
mv $SPLIT_DIR/*.{aa,ac} unannotated
