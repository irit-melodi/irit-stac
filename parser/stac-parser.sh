#!/bin/bash
shopt -s nullglob
set -e

pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

pushd $SCRIPT_DIR/../.. > /dev/null
STAC_DIR=$PWD
popd > /dev/null
CODE_DIR=$STAC_DIR/code
DATA_DIR=$STAC_DIR/data

SHIPPED_TAGGER=ark-tweet-nlp-0.3.2.jar

if [ -e $STAC_DIR/lib/$SHIPPED_TAGGER ]; then
    TAGGER_JAR=$1
else
    echo >&2 "Need $SHIPPED_TAGGER in $STAC_DIR/lib"
    echo >&2 "See http://www.ark.cs.cmu.edu/TweetNLP"
    exit 1
fi

if [ $# -lt 2 ]; then
    echo >&2 "Usage: $0 file.soclog output-dir"
    exit 1
fi

INPUT_FILE=$1
OUTPUT_DIR=$2
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
python $CODE_DIR/run-3rd-party --live --ark-tweet-nlp $TAGGER_JAR $T $T

# extract features
python $CODE_DIR/queries/rel-info --live $T $DATA_DIR/resources/lexicon $T

# TODO
echo >&2 "TODO: feed $T/extracted-features.csv to the parser"
