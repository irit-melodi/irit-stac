#!/bin/bash
pushd $(dirname $0) > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

set -e

#test cross-validation avec attachement et relations
#
DATA_DIR=/tmp/charette-2014-01-13
DATA_EXT=.csv # .2.csv
DECODE_FLAGS="-C $SCRIPT_DIR/stac-features.config"
DECODER=attelo

for dataset in all; do
    $DECODER evaluate $DECODE_FLAGS\
        $DATA_DIR/$dataset.edu-pairs$DATA_EXT $DATA_DIR/$dataset.relations$DATA_EXT -l bayes -d mst

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

# results
#socl
#FINAL EVAL: relations full: 	 locallyGreedy+bayes, h=average, unlabelled=False,post=False,rfc=full 	 Prec=0.229, Recall=0.217, F1=0.223 +/- 0.015 (0.239 +- 0.029)
#FINAL EVAL: relations full: 	 local+maxent, h=average, unlabelled=False,post=False,rfc=full 	         Prec=0.678, Recall=0.151, F1=0.247 +/- 0.017 (0.243 +- 0.034)
#FINAL EVAL: relations full: 	 local+bayes, h=average, unlabelled=False,post=False,rfc=full 	                 Prec=0.261, Recall=0.249, F1=0.255 +/- 0.015 (0.264 +- 0.031)
#FINAL EVAL: relations full: 	 locallyGreedy+maxent, h=average, unlabelled=False,post=False,rfc=full 	 Prec=0.281, Recall=0.257, F1=0.269 +/- 0.015 (0.277 +- 0.030)

#pilot
#FINAL EVAL: relations full  : 	 locallyGreedy+maxent, h=average, unlabelled=False,post=False,rfc=full 	 Prec=0.341, Recall=0.244, F1=0.284 +/- 0.015 (0.279 +- 0.029)
