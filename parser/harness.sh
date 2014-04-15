#!/usr/bin/env bash

# Note: you should have run build-model to gather the data for this
# (it also builds a model, which we don't really use here)

pushd "$(dirname $0)" > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

set -e

#test cross-validation avec attachement et relations
#
DATA_DIR=$SCRIPT_DIR/../../data/SNAPSHOTS/latest
DATA_EXT=.csv # .2.csv
DECODE_FLAGS="-C $SCRIPT_DIR/stac-features.config"
DECODER=attelo

if [ ! -d "$DATA_DIR" ]; then
    echo >&2 "No data to run experiments on"
    echo >&2 "Please run $SCRIPT_DIR/gather-features"
    exit 1
fi

TODAY=$(date +%Y-%m-%d)
EVAL_DIR=$DATA_DIR/eval-$TODAY
mkdir -p $EVAL_DIR

T=$(mktemp -d -t stac.XXXX)
cd $T

# NB: use a colon if you want a separate learner for relations
LEARNERS="bayes maxent"
DECODERS="last local locallyGreedy mst"
DATASETS="all pilot socl-season1"

for dataset in $DATASETS; do
    echo > $EVAL_DIR/scores-$dataset
    # try x-fold validation with various algos
    for learner in $LEARNERS; do
        for decoder in $DECODERS; do
            echo >&2 "=============================================================="
            echo >&2 "$dataset $decoder $learner"
            echo >&2 "=============================================================="
            echo >&2 ""
            LEARNER_FLAGS="-l"$(echo $learner | sed -e 's/:/ --relation-learner /')
            $DECODER evaluate $DECODE_FLAGS\
                $DATA_DIR/$dataset.edu-pairs$DATA_EXT\
                $DATA_DIR/$dataset.relations$DATA_EXT\
                $LEARNER_FLAGS\
                -d $decoder >> $EVAL_DIR/scores-$dataset
        done
    done
done

cd $EVAL_DIR
# This isn't part of the evalution proper.
# It seems to just be here to try training a model on the data
# and seeing what happens when we decode on the very same data
for dataset in $DATASETS; do
    # test stand-alone parser for stac
    # 1) train and save attachment model
    # -i
    $DECODER learn $DECODE_FLAGS $DATA_DIR/$dataset.edu-pairs$DATA_EXT -l bayes
    mv attach.model $dataset.attach.model

    # 2) predict attachment (same instances here, but should be sth else) 
    # NB: updated astar decoder seems to fail / TODO: check with the real subdoc id
    # -i
    $DECODER decode $DECODE_FLAGS -A $dataset.attach.model -o tmp\
        $DATA_DIR/$dataset.edu-pairs$DATA_EXT -d mst

    # attach + relations: TODO: relation file is not generated properly yet
    # 1b) train + save attachemtn+relations models
    $DECODER learn $DECODE_FLAGS\
        $DATA_DIR/$dataset.edu-pairs$DATA_EXT\
        $DATA_DIR/$dataset.relations$DATA_EXT\
        -l bayes
    mv attach.model    $dataset.attach.model
    mv relations.model $dataset.relations.model

    # 2b) predict attachment + relations
    # -i
    $DECODER decode $DECODE_FLAGS -A $dataset.attach.model -R $dataset.relations.model -o tmp/\
        $DATA_DIR/$dataset.edu-pairs$DATA_EXT\
        $DATA_DIR/$dataset.relations$DATA_EXT\
        -d mst
done
echo $T >&2
