The scripts in this directory aim to automate as much of the process of
preparing Settlers of Catan log files (soclog) for annotation in Glozz.

This is essentially the contents of [Vladimir's pipeline notes][vlad]
in the form of Bash scripts, with some corrections noted in
[Eric's errata][eric].

This is *not* self-contained.  It currently calls scripts in

* /code/txt2csv
* /code/segmentation
* /code/csv2glozz

## Usage

See the scripts intake-1-batch.sh and intake-2.sh for details

0. Put soclog files in a directory, with a comma-separated mappings.txt
   file that assigns a clean name to each file, as in eg.

          s1-l1-g02,League 1-2012-06-17-19-53-24-+0100.soclog
          s1-l1-g03,League 1 game-2012-06-19-18-49-00-+0100.soclog

1. [AUTO]
   In that directory, pre-segment all soclog files, create aam templates
   (run intake-1-batch.sh)

2. [MANUAL]
   For each soclog file (we assume here you are working incrementally):

   Manually correct segmentation results (OpenOffice, Excel, etc),
   using '&' to separate EDUS, and
   inserting blank lines to create document sections
   (foo/segmented/foo.soclog.seg.csv)

3. [AUTO]
   As you create the segmented files, convert the results to glozz
   (run intake-2.sh foo/segmented/foo.soclog.seg.csv)


[vlad]: /docs/reation_aa_ac_Vladimir.README
[eric]: /docs/notes-kow/intake-errata.markdown
