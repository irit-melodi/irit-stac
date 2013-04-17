#!/bin/bash

shopt -s nullglob

for sd in discourse units; do
    for d in data/socl-season1/s*; do
        anno_dir=$d/$sd/GOLD
        if [ ! -d $anno_dir ]; then
            echo $anno_dir
            mkdir $anno_dir
            pushd $anno_dir > /dev/null
            echo " ac"
            for ac in ../../unannotated/*.ac; do
                ln -s $ac .
            done
            echo " aam"
            ln -s ../../*.aam .
            echo "Delete this README file when these GOLD files are ready" > README
            echo " git"
            git add *.aa *.ac *.aam README
            popd > /dev/null
        fi
    done
done
