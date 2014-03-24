This is the STAC codebase.

## Prerequisites

1. Python 2.7. Python 3 might also work.
2. pip (see educe README if you do not)
3. git (to keep up with educe/attelo changes)
4. graphviz (for visualising graphs)
5. [optional] Anacoda (`conda --version` should say 2.2.6 or higher)

## Sandboxing

If you are attempting to use the development version of this code
(ie. from SVN), I highly recommend using a sandbox environment.
We have two versions below, one for Anaconda users (on Mac),
and one for standard Python users via virtualenv.

### For Anaconda users

Anaconda users get slightly different instructions because virtualenv
doesn't yet seem to work well with it (at least with the versions we've
tried). Instead of using virtualenv, you could try something like this

    conda create -n stac --clone $HOME/anaconda

If that doesn't work, make sure your anaconda version is up to date,
and try `/anaconda` instead of `$HOME/anaconda`.

Note that whenever you want to use STAC things, you would need to run
this command

    source activate stac

### For standard Python users

The virtualenv equivalent works a bit more like the follow:

    mkdir $HOME/.virtualenvs
    virtualenv $HOME/.virtualenvs/stac --no-site-packages

Whenever you want to use STAC things, you would need to run this
command

    source $HOME/.virtualenvs/stac/bin/activate

## Installation (development mode)

Both educe and attelo supply requirements.txt files which can be
processed by pip

0. It can be useful to have a single directory where the STAC code
   and its friends can live. I'll call it StacProject for purposes
   of this documentation

       $HOME/StacProject/Stac
       $HOME/StacProject/educe
       $HOME/StacProject/attelo

1. Fetch educe and attelo:

       cd $HOME/StacProject
       git clone git@github.com:kowey/educe.git
       git clone git@github.com:kowey/attelo.git

2. Switch into your STAC virtualenv

       source $HOME/.virtualenvs/stac/bin/activate

3. Install educe and attelo prerequisites.

       cd educe
       pip install -r requirements.txt\
          --allow-unverified pydot\
          --allow-unverified python-graph-core\
          --allow-unverified python-graph-dot
       cd ..

       cd attelo
       pip install -r requirements.txt
       cd ..


4. Install educe and attelo in development mode. Development mode
   simply puts the link to the current version of educe/attelo into
   your environment

       cd educe
       python setup.py develop
       cd ..

       cd attelo
       python setup.py develop
       cd ..

   If somebody tells you to update educe/attelo, it should be
   possible to just go into the respective directories and
   issue a `git pull`. No further installation will be needed.

5. Install the STAC code in development mode

       cd Stac/code
       pip install -r requirements.txt
       python setup.py develop

   Likewise, if somebody tells you to update the STAC code, it
   should be possible to just `svn update`.  No further
   installation will be needed

## Parser infrastructure

Now that you have everything installed, there are a handful of parser
infrastructure scripts which run the feature extraction process, build
the attachment/labeling models, and run the decoder on sample data.

code/parser/gather-features
~ do feature extraction from annotated data, along with pre-saved
  pos-tagging and and parser output, and some lexical resources

code/parser/build-model
~ from the extracted features (see gather-features), build the
  attachment and labeling models needed to run the parser

code/parser/stac-parser.sh
~ given a model (see build-model), and a STAC soclog file, run the
  parser and display a graph of the output (needs third party
  tools, see script for details)

code/parser/harness.sh
~ given extracted features (see gather-features), run experiments on
  STAC data
