#!/bin/bash
shopt -s nullglob
set -e

pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

pushd $SCRIPT_DIR/.. > /dev/null
CODE_DIR=$PWD
popd > /dev/null

pushd $CODE_DIR/../data > /dev/null
DATA_DIR=$PWD
popd > /dev/null

if [ $# -lt 3 ]; then
    echo >&2 "Usage: $0 ark-tweet-nlp.jar file.soclog output-dir"
    exit 1
fi

TAGGER_JAR=$1
INPUT_FILE=$2
OUTPUT_DIR=$3
T=$(mktemp -d -t stac.XXXX)

# Note that much of this replicates the functionality in code/intake
# If there is any divergeance that can't be easily justified (ie.
# maybe it's just bitrot), you should probably treat code/intake
# as canonical.

# from soclog to csv (sorry)
TURNS_FILE=$T/turns
python $CODE_DIR/txt2csv/extract_turns.py "$INPUT_FILE" > $TURNS_FILE
python $CODE_DIR/txt2csv/extract_annot.py $TURNS_FILE
UNSEGMENTED=$T/unsegmented.csv
SEGMENTED=$T/segmented.csv
mv ${TURNS_FILE}csv $UNSEGMENTED
rm ${TURNS_FILE}

# run segmenter
python $CODE_DIR/segmentation/simple-segments --csv $UNSEGMENTED $SEGMENTED

# convert to glozz format
pushd $T > /dev/null
python $CODE_DIR/csv2glozz/csvtoglozz.py -f segmented.csv
popd > /dev/null

# pos tag
python $CODE_DIR/pos-tag --live --ark-tweet-nlp $TAGGER_JAR $T $T

# extract features
python $CODE_DIR/queries/rel-info --live $T $DATA_DIR/resources/lexicon $T

# TODO
echo >&2 "TODO: feed $T/extracted-features.csv to the parser"
