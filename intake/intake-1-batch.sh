#!/bin/bash
set -e

# First half of the intake process:
#
# Given mapping file, prepare for segmentation
pushd `dirname $0` > /dev/null
SCRIPT_DIR=$PWD
popd > /dev/null

if [ $# -ne 1 ]; then
    echo >&2 "Usage: $0 mapping [gen2_ling_only]"
    exit 1
fi

MAPPING_FILE=$1
GEN=$2

while IFS=, read clean original; do
    bash $SCRIPT_DIR/intake-1.sh "$original" "$clean" "$GEN" batch
done < $MAPPING_FILE

echo >&2 "Now for each entry in $MAPPING_FILE, edit the segmented csv file"
echo >&2 "using '&' characters for EDUs and blank lines for sections"
echo >&2 "Then run intake-2.sh on segmented/XXX.soclog.seg.csv"
