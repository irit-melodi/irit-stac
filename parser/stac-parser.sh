#!/bin/bash
shopt -s nullglob

die () {
    errcode=$?
    echo "ARGH! Something went wrong..."
    exit $errcode
}
trap die ERR


pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

pushd $SCRIPT_DIR/../.. > /dev/null
STAC_DIR=$PWD
popd > /dev/null
CODE_DIR=$STAC_DIR/code
DATA_DIR=$STAC_DIR/data
SNAPSHOT_DIR="$DATA_DIR/SNAPSHOTS/latest"

SHIPPED_TAGGER=ark-tweet-nlp-0.3.2.jar
SHIPPED_PARSER=stanford-corenlp-full-2013-06-20

# how the model was built
ATTELO_LEARNERS="maxent bayes"
ATTELO_DECODERS="mst locallyGreedy local"
ATTELO_CONFIG="$SCRIPT_DIR/stac-features.config"

# which datasets the models were built on
# at some point in the future, we could probably just have one
# but for development, it can be useful to get some insight into
# how much the dataset influences things
DATASETS="all socl-season1 pilot"

if [ -e $STAC_DIR/lib/$SHIPPED_TAGGER ]; then
    TAGGER_JAR=$STAC_DIR/lib/$SHIPPED_TAGGER
else
    echo >&2 "Need $SHIPPED_TAGGER in $STAC_DIR/lib"
    echo >&2 "See http://www.ark.cs.cmu.edu/TweetNLP"
    exit 1
fi

if [ -e $STAC_DIR/lib/$SHIPPED_PARSER ]; then
    CORENLP_DIR=$STAC_DIR/lib/$SHIPPED_PARSER
else
    echo >&2 "Need $SHIPPED_PARSER in $STAC_DIR/lib"
    echo >&2 "See http://nlp.stanford.edu/software/corenlp.shtml"
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

## parser
python $CODE_DIR/run-3rd-party --live --corenlp $CORENLP_DIR $T $T

# extract features
python $CODE_DIR/queries/rel-info\
    --live\
    --experimental\
    $T $DATA_DIR/resources/lexicon $T


decode() {
    decoder=$1
    learner=$2
    dset=$3

    MODEL_INFO="$dset-$learner"
    PARSED="parsed-$MODEL_INFO-$decoder"
    mkdir $T/$PARSED
    pushd $T/$PARSED > /dev/null
    # TODO - not sure if we really need to feed different data for
    # attachments ande relations here (right now just duplicating
    attelo decode -C "$ATTELO_CONFIG"\
        -A "$SNAPSHOT_DIR/attach-$MODEL_INFO.model"\
        -R "$SNAPSHOT_DIR/relations-$MODEL_INFO.model"\
        -d "$decoder"\
        -o $T/$PARSED\
        "$T/extracted-features.csv"\
        "$T/extracted-features.csv"
    popd > /dev/null

    PARSED0=$(ls -1 $T/$PARSED/*.csv | head -n 1)
    if [ ! -z "$PARSED0" ]; then
        mkdir -p $OUTPUT_DIR
        head -n 1 $PARSED0 > $OUTPUT_DIR/$PARSED.csv
        for i in "$T/$PARSED/"*.csv; do
            tail -n +2 "$i" >> $OUTPUT_DIR/$PARSED.csv
        done
    fi

    $SCRIPT_DIR/parse-to-glozz $T $OUTPUT_DIR/$PARSED.csv $OUTPUT_DIR/$PARSED
    stac-util graph --live $OUTPUT_DIR/$PARSED --output $OUTPUT_DIR/$PARSED
    mv $OUTPUT_DIR/$PARSED/segmented/unannotated/segmented.svg $OUTPUT_DIR/$PARSED.svg
}

# run the decoder
#
# The reason we have a dataset loop is that the we have parts of the
# corpus that are annotated at sufficiently different times, that we
# can suspect there fundamental differences between them that could
# make it a bad idea to mix them
#
# Running on individual sections plus the combined one helps us to
# investigate this. If we want to use this in the real world, we would
# probably just focus on a single dataset (eg. the combined one).
for decoder in $ATTELO_DECODERS; do
    for learner in $ATTELO_LEARNERS; do
        for dset in $DATASETS; do
            decode $decoder $learner $dset
        done
    done
done

