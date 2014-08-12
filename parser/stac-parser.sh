#!/bin/bash
shopt -s nullglob

die () {
    errcode=$?
    echo "ARGH! Something went wrong..."
    echo "See logs in directory: /tmp/stac-parser-tmp/logs"
    exit $errcode
}
trap die ERR

VERBOSE=1
announce_start () {
    if [ "$VERBOSE" -ne 0 ]; then
        echo -n >&2 "[stac] $1... "
    fi
}

announce_end () {
    if [ "$VERBOSE" -ne 0 ]; then
        echo >&2 "done"
    fi
}


ZERO_DIR=$(dirname "$0")
pushd "$ZERO_DIR" > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

pushd "$SCRIPT_DIR/../.." > /dev/null
STAC_DIR=$PWD
popd > /dev/null
CODE_DIR=$STAC_DIR/code
DATA_DIR=$STAC_DIR/data
SNAPSHOT_DIR="$DATA_DIR/SNAPSHOTS/latest"

SHIPPED_TAGGER=ark-tweet-nlp-0.3.2.jar
SHIPPED_PARSER=stanford-corenlp-full-2013-06-20

# how the model was built
ATTELO_LEARNERS="bayes maxent"
ATTELO_DECODERS="last local locallyGreedy mst"
ATTELO_CONFIG="$SCRIPT_DIR/stac-features.config"

# which datasets the models were built on
# at some point in the future, we could probably just have one
# but for development, it can be useful to get some insight into
# how much the dataset influences things
DATASETS="all socl-season1 pilot"

if [ -e "$STAC_DIR/lib/$SHIPPED_TAGGER" ]; then
    TAGGER_JAR=$STAC_DIR/lib/$SHIPPED_TAGGER
else
    echo >&2 "Need $SHIPPED_TAGGER in $STAC_DIR/lib"
    echo >&2 "See http://www.ark.cs.cmu.edu/TweetNLP"
    exit 1
fi

if [ -e "$STAC_DIR/lib/$SHIPPED_PARSER" ]; then
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
mkdir "$T/logs"

# convenient path for inspection of the pipeline
rm -rf /tmp/stac-parser-tmp
ln -s "$T" /tmp/stac-parser-tmp

TMP_STUB=$(basename "$INPUT_FILE" | tr _ -)
TMP_STUB="${TMP_STUB%.*}"
TMP_CORPUS_DIR="$T/minicorpus"
TMP_DOC_DIR="$TMP_CORPUS_DIR/$TMP_STUB"

# Note that much of this replicates the functionality in code/intake
# If there is any divergeance that can't be easily justified (ie.
# maybe it's just bitrot), you should probably treat code/intake
# as canonical.

# from soclog to csv (sorry)
announce_start "Converting (soclog -> stac csv)"
TURNS_FILE=$T/turns
python "$CODE_DIR/txt2csv/extract_turns.py" "$INPUT_FILE" > "$TURNS_FILE"
python "$CODE_DIR/txt2csv/extract_annot.py" "$TURNS_FILE"\
    > "$T/logs/0100-extract_annot.txt"
UNSEGMENTED=$T/unsegmented.csv
SEGMENTED=$T/segmented.csv
mv "${TURNS_FILE}csv" "$UNSEGMENTED"
rm "${TURNS_FILE}"
announce_end

# run segmenter
announce_start "Segmenting"
python "$CODE_DIR/segmentation/simple-segments" --csv "$UNSEGMENTED" "$SEGMENTED"
announce_end

announce_start "Converting (stac csv -> glozz)"
UNANNOTATED_DIR="$TMP_DOC_DIR/unannotated"
UNANNOTATED_STUB="$UNANNOTATED_DIR/${TMP_STUB}_0"

# convert to glozz format
pushd "$T" > /dev/null
python "$CODE_DIR/csv2glozz/csvtoglozz.py" -f segmented.csv\
    2> "$T/logs/0200-csv2glozz.txt"
mkdir -p "$UNANNOTATED_DIR"
mv segmented.aa "$UNANNOTATED_STUB.aa"
mv segmented.ac "$UNANNOTATED_STUB.ac"
popd > /dev/null
announce_end

# pos tag
announce_start "POS taggging"
python "$CODE_DIR/run-3rd-party"\
    --ark-tweet-nlp "$TAGGER_JAR"\
    "$TMP_CORPUS_DIR" "$TMP_CORPUS_DIR"\
    2> "$T/logs/0300-pos-tagging.txt"
announce_end

# parser
announce_start "Parsing (NB: CoreNLP is slow to start; can remove)"
python "$CODE_DIR/run-3rd-party" --corenlp "$CORENLP_DIR"\
    "$TMP_CORPUS_DIR" "$TMP_CORPUS_DIR"\
    2> "$T/logs/0400-parsing.txt"
announce_end

# annotate dialogue acts
announce_start "Dialogue act annotation"
python "$CODE_DIR/parser/dialogue-acts" annotate\
    -C "$ATTELO_CONFIG"\
    "$TMP_CORPUS_DIR"\
    "$DATA_DIR/resources/lexicon"\
    --model "$SNAPSHOT_DIR/all.dialogue-acts.model"\
    --output "$TMP_CORPUS_DIR"\
    2> "$T/logs/0500-dialogue-acts.txt"
announce_end

TMP_DA_DIR=$(ls -d "$TMP_DOC_DIR"/units/*)
if [ -z "$TMP_DA_DIR" ]; then
    echo >&2 "No dialogue annotation output found"
    exit 1
fi

# extract features
announce_start "Feature extraction"
stac-learning extract --parsing\
    --experimental\
    "$TMP_CORPUS_DIR"\
    "$DATA_DIR/resources/lexicon"\
    "$T"\
    2> "$T/logs/0600-features.txt"
announce_end

decode() {
    trap die ERR
    decoder=$1
    learner=$2
    dset=$3
    learner_file_name=$(echo "$learner" | sed -e 's/:/-/')

    MODEL_INFO="$dset.$learner_file_name"
    PARSED_STUB="$MODEL_INFO-$decoder"
    TMP_PARSED="$T/tmp-parsed/$PARSED_STUB"
    mkdir -p "$TMP_PARSED" "$T/parsed"
    pushd "$TMP_PARSED" > /dev/null
    # TODO - not sure if we really need to feed different data for
    # attachments ande relations here (right now just duplicating
    attelo decode -C "$ATTELO_CONFIG"\
        -A "$SNAPSHOT_DIR/$MODEL_INFO.attach.model"\
        -R "$SNAPSHOT_DIR/$MODEL_INFO.relate.model"\
        -d "$decoder"\
        -o .\
        "$T/extracted-features.csv"\
        "$T/extracted-features.csv"\
        >> "$T/logs/0700-decoding.txt" 2>&1
    popd > /dev/null

    PARSED_COMBINED="$T/parsed/$PARSED_STUB".csv
    csvs=( "$TMP_PARSED"/*.csv )
    PARSED0=${csvs[0]}
    if [ ! -z "$PARSED0" ]; then
        head -n 1 "$PARSED0" > "$PARSED_COMBINED"
        for i in "$TMP_PARSED/"*.csv; do
            tail -n +2 "$i" >> "$PARSED_COMBINED"
        done
    fi

    # symlink units so that we see dialogue acts in output graphs
    mkdir -p "$TMP_DOC_DIR/units/$PARSED_STUB"
    ln "$TMP_DA_DIR"/* "$TMP_DOC_DIR/units/$PARSED_STUB"

    # parsed csv to glozz
    "$SCRIPT_DIR/parse-to-glozz" "$UNANNOTATED_DIR" "$PARSED_COMBINED"\
        "$TMP_DOC_DIR/discourse/$PARSED_STUB"\
        >> "$T/logs/0700-decoding.txt" 2>&1
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
touch "$T/logs/0700-decoding.txt"
for dset in $DATASETS; do
    for learner in $ATTELO_LEARNERS; do
        for decoder in $ATTELO_DECODERS; do
            announce_start "Decoding $dset (learner: $learner decoder: $decoder)"
            decode "$decoder" "$learner" "$dset"
            announce_end
        done
    done
done

announce_start "Drawing graphs"
stac-util graph "$TMP_CORPUS_DIR" --output "$TMP_CORPUS_DIR"\
    2> "$T/logs/0800-graphs.txt"
announce_end

mkdir -p "$OUTPUT_DIR/graphs"
# copy just the interesting outputs over
cp -R "$T/parsed" "$OUTPUT_DIR/parsed"
for f in $(find "$TMP_CORPUS_DIR" -name '*.svg'); do
    df=$(dirname "$f")
    bdf=$(basename "$df")
    cp "$f" "$OUTPUT_DIR/graphs/$bdf.svg"
done
