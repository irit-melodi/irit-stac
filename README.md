This is the STAC codebase.

## Prerequisites

1. Python 2.7. Python 3 might also work.
2. pip (see educe README if you do not)
3. git (to keep up with educe/attelo changes)

If you are attempting to use the development version of this code
(ie. from SVN), I highly recommend using virtualenv to create a
Python sandbox where all things STAC will be installed

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

3. Install educe and attelo in development mode. Development mode
   simply puts the link to the current version of educe/attelo into
   your environment

       cd educe
       pip install -r requirements.txt
       python setup.py develop
       cd ..

       cd attelo
       pip install -r requirements.txt
       python setup.py develop
       cd ..

   If somebody tells you to update educe/attelo, it should be
   possible to just go into the respective directories and
   issue a `git pull`. No further installation will be needed.

4. Install the STAC code in development mode

       cd Stac/code
       python setup.py development

   Likewise, if somebody tells you to update the STAC code, it
   should be possible to just `svn update`.  No further
   installation will be needed
