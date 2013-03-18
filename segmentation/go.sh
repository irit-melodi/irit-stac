#!/bin/bash
# Setup segmentation workbench (if needed) and (re)run segmenter
set -e
HERE_DIR=$PWD
pushd $(dirname $0) > /dev/null
SCRIPT_DIR=$PWD
pushd ../.. > /dev/null
ROOT_DIR=$PWD
popd > /dev/null
popd > /dev/null

# set up the workbench if it doesn't already exist
if [ ! -d unsegmented -o $1 == '--setup' ]; then
    mkdir -p orig/{csv,segmented}
    mkdir -p {unsegmented,manually-segmented}
    for i in $(find $ROOT_DIR/data/pilot -name '*.soclog.csv'); do
        bn2=$(basename $i)
        cp $i orig/csv
        python $SCRIPT_DIR/simple-segments --no-seg $i unsegmented/$bn2
    done
    for i in $(find $ROOT_DIR/data/pilot -name '*.soclog.seg.csv'); do
        bn2=$(basename $i .seg.csv).csv
        cp $i orig/segmented/$bn2
        python $SCRIPT_DIR/simple-segments --no-seg $i manually-segmented/$bn2
    done

    # this normalisation step isn't entirely necessary; mostly there for
    # comparison purposes
    python $SCRIPT_DIR/normalise-csv orig/csv       unsegmented.csv
    python $SCRIPT_DIR/normalise-csv orig/segmented manually-segmented.csv
fi

mkdir -p nltk-segmented nltk-segmented.csv
for i in unsegmented.csv/*.csv; do
    python $SCRIPT_DIR/simple-segments $i nltk-segmented/$(basename $i)
    python $SCRIPT_DIR/simple-segments --csv $i nltk-segmented.csv/$(basename $i)
done

diff -r -y --suppress-common-lines manually-segmented nltk-segmented > diffs || :
echo -n "Differences between manual/auto segmentation: "
wc -l diffs | awk '{print $1}'

echo >&2 "HINT: opendiff manually-segmented nltk-segmented"
echo >&2 "(meld on Linux)"
