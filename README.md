This is the STAC codebase.

## Prerequisites

1. Python 2.7. Python 3 might also work.
2. pip 1.5 or higher (see educe README if you do not)
3. Anacoda or miniconda (`conda --version` should say 2.2.6 or higher)
4. git (to keep up with educe/attelo changes)
5. graphviz (for visualising graphs)
6. STAC corpus (released separately)

## Sandboxing

A sandbox environment is required.  We assume you will be using Anaconda
(miniconda on Linux).  Once you have installed it, you should be able to
create the environment with

    conda create -n stac scipy pip

If that doesn't work, make sure your anaconda version is up to date,
and the conda bin directory is in your path (it might be installed in
`/anaconda` instead of `$HOME/anaconda`).

Note that whenever you want to use STAC things, you would need to run
this command

    source activate stac

## Installation (basics, development mode)

Both educe and attelo supply requirements.txt files which can be
processed by pip

1. Switch into your STAC sandbox

       source activate stac

2. Linux users: (Debian/Ubuntu)

       sudo apt-get install python-dev libyaml-dev
       # NB: this step may be obsoleted by requiring conda


3. Fetch the irit-stac code if you have not done so already

       git clone https://github.com/kowey/irit-stac.git
       cd irit-stac

4. Install the irit-stac code in development mode.
   This should automatically fetch the educe/attelo dependencies
   automatically

       pip install -r requirements.txt

   At this point, if somebody tells you to update the STAC code, it
   should be possible to just `git pull` and maybe
   `pip install -r requirements.txt` again if attelo/educe need to be
   updated. No further installation will be needed

5. Install NLTK data files

       python setup-nltk.py

6. Link the STAC corpus in (STAC has not yet been released, so here
   the directory "Stac" refers to the STAC SVN directory)

       ln -s /path/to/Stac/data data


## Full installation (Toulouse/Edinburgh)

You only need to do this if you intend to use the `irit-stac parse`
or `irit-stac serve` command, i.e. if you're participating in
discourse parser experiments or integration work between the
parsing pipeline and the dialogue manager.

1. Do the basic install above

2. Download [tweet-nlp][tweet-nlp] part of speech tagger
   and put the jar file (ark-tweet- in the
   lib/ directory (ie. on the STAC SVN root at the same level as
   code/ and data/)

3. Download and install corenlp-server (needs Apache Maven!)

        cd irit-stac
        mkdir lib
        cd lib
        git clone https://github.com/kowey/corenlp-server
        cd corenlp-server
        mvn package

## Usage (Toulouse)

Running the pieces of infrastructure here should consist of running
`irit-stac <subcommand>` from the STAC SVN root.

Folks (likely in Edinburgh) who just want to run the parsing pipeline
server should skip this section and go to "Usage (Edinburgh)" instead.

### Basics

Using the harness consists of two steps, gathering the features, and
running the n-fold cross validation loop

    irit-stac gather
    irit-stac evaluate

If you stop an evaluation (control-C) in progress, you can resume it
by running

    irit-stac evaluate --resume

The harness will try to detect what work it has already done and pick
up where it left off.

### Configuration

There is a small configuration module that you can edit
in code/stac/harness/local.py

It lets you control things such as which corpora to run on,
which decoders and learners to try, and how to do feature
extraction.

It tries to be self-documenting.

### Standalone parser

You can also use this infrastructure to parse new soclog files,
using models built from features you have collected.

    irit-stac gather
    irit-stac model
    irit-stac parse code/parser/sample.soclog /tmp/parser-output

### Scores

You can get a sense of how things are going by inspecting the various
intermediary results

1. count files: At each learner/decoder combination we will count
   the number of correct attachments and relation labels (and save
   these into intermediary count) (for a given fold N, see
   `TMP/latest/scratch-current/fold-N/count-*.csv`)

2. fold summaries: At the end of each fold, we will summarise all of
   the counts into a simple Precision/Recall/F1 report for attachment
   and labelling. (for a given fold N, see
   `TMP/latest/scratch-current/fold-N/scores*.txt`)

3. full summary: If we make it through the entire experiment, we will
   produce a cross-validation summary combining the counts from all
   folds (`TMP/latest/eval-current/scores*.txt`)

### Cleanup

The harness produces a lot of output, and can take up potentially a lot
of disk space in the process.  If you have saved results you want to
keep, you can run the command

    irit-stac clean

This will delete *all* scratch directories, along with any evaluation
directories that look incomplete (no scores).

### Output files

There are two main directories for output.

* The data/SNAPSHOTS directory is meant for intermediary results that
you want to save. You have to copy files into here manually (more on
that later).
Because this directory can take up space, it does not feel quite right
to dump it on the public GitHub repo. We'll need to think about where to
store our snapshots later (possibly some IRIT-local SVN?)

* The TMP directory is where the test harness does all its work.  Each
`TMP/<timestamp>` directory corresponds to a set of feature files
generated by `irit-stac gather`.  For convenience, the harness will
maintain a `TMP/latest` symlink pointing to one of these directories.

Within the each feature directory, we can have a number of evaluation
and scratch directories. This layout is motivated by us wanting to
suppport ongoing changes to our learning/decoding algorithms
independently of feature collection. So the thinking is that we may
have multiple evaluations for any given set of features. Like the
feature directories, these are named by timestamp (with
`eval-current` and `scratch-current` symlinks for convenience).

* scratch directories: these are considered relatively ephemeral
  (hence them being deleted by `irit-stac clean`). They contain
  all the models and counts saved by harness during evaluation.

* eval directories: these contain things we would consider more
  essential for reproducing an evaluation. They contain the
  feature files (hardlinked from the parent dir) along with the
  fold listing and the cross-fold validation scores. If you hit
  any interesting milestones in development, it may be good to
  manually copy the eval directory to SNAPSHOTS, maybe with a
  small README explaining what it is, or at least a vaguely
  memorable name. This directory should be fairly self-contained.

## Usage (Edinburgh)

First make sure that the standalone parser works for you

    irit-stac parse code/parser/sample.soclog /tmp/parser-output

The parsing pipeline server has the same function as the standalone
parser but accepts inputs and sends outputs back over a network
connection

    irit-stac server --port 7777

Note that if you launch

    irit-stac server --port 7777 --incremental

The server will assume that every connection is *appending* to an
input in progress, and will generate a new output based on the
extended input (you'll have to restart the server for new inputs)


[tweet-nlp]: http://www.ark.cs.cmu.edu/TweetNLP/
