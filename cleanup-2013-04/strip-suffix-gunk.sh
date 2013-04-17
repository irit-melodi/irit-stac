#!/bin/bash

# Given an extension prefix, strips off parts between that extension
# and the final extension
#
# Given .seg.csv_petersen_d_
# These files get renamed
#
#    pilot1.2.1.seg.csv_petersen_d_19022013.aa -> pilot1.2.1.seg.csv_petersen_d.aa
#    pilot1.2.2.seg.csv_petersen_d_20102013.aa -> pilot1.2.1.seg.csv_petersen_d.aa
#    pilot1.2.3.seg.csv_petersen_d_16122013.aa -> pilot1.2.1.seg.csv_petersen_d.aa
#
# hINT: second argument is the command to do the operation, eg. "git mv"

set -e

pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

if [ $# -lt 1 ]; then
    echo >&2 "Usage: $0 extension-prefix [mv-cmd]"
    echo >&2 "Eg. $0 .seg.csv_petersen_d"
    exit 1
fi

EXT_PREFIX=$1
if [ -z "$2" ]; then
    RENAMER=echo
else
    RENAMER=$2
fi

for f in *.${EXT_PREFIX}*; do
    extension="${f##*.}"
    f2=$(echo $f | sed -e 's/\('${EXT_PREFIX}'\)\(.*\)/\1.'$extension'/')
    $RENAMER $f $f2
done
