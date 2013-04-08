The scripts in this directory aim to automate as much of the process of
preparing Settlers of Catan log files (soclog) for annotation in Glozz.

This is essentially the contents of [Vladimir's pipeline notes][vlad]
in the form of Bash scripts.

This is not self-contained.  It currently calls scripts in

* /code/txt2csv
* /code/segmentation
* /code/csv2glozz

## Usage

See the scripts intake-1-batch.sh and intake-2.sh for details

0. put soclog files in a directory, with a comma-separated mappings.txt
   file that assigns a clean name to each file, as in eg.

          League 1-2012-06-17-19-53-24-+0100.soclog,s1-l1-g02
          League 1 game-2012-06-19-18-49-00-+0100.soclog,s1-l1-g03

1. in that directory, pre-segment all soclog files
   (run intake-1-batch.sh)

For each soclog file (we assume here you are working incrementally)

2. manually correct segmentation results (OpenOffice, Excel, etc)
   (foo/segmented/foo.soclog.seg.csv)

3. split files (run intake-2.sh dir/segmented/file.soclog.seg.csv)

4. manually correct splits
   (open `dir/split/*.csv` files in text editor, move lines
   around as desired)

5. convert corrected segmentation results to glozz,
   create .aam templates for these (run intake-3.sh)


[vlad]: /docs/reation_aa_ac_Vladimir.README
