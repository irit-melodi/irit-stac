# Developers' Guide
The Melodi team has been developing discourse parsing systems that rely on
two libraries:
* [educe](https://github.com/irit-melodi/educe/) for corpus creation,
management and exploration, plus feature extraction,
* [attelo](https://github.com/irit-melodi/attelo/) for parsing and managing
experiments.

Parsing systems are built on top of these two libraries but they have their
own repositories, currently:
* [irit-rst-dt](https://github.com/irit-melodi/irit-rst-dt/) for the
RST-WSJ corpus,
* [irit-stac](https://github.com/irit-melodi/irit-stac/) for the STAC
corpus.

For what follows, let us suppose you are a new developer whose aim is to
define a new training procedure for parsing models and evaluate the
resulting models on the STAC corpus.
You will basically need to fork attelo (to implement your training procedure)
and irit-stac (to make your training procedure available for experiments).


## Initial setup of parsing systems for the STAC corpus (irit-stac)

### Prerequisites
1. git
2. Anaconda or miniconda >= 2.2.6
3. STAC corpus (released separately, ask your contact from the STAC project)
4. A GitHub account

### Basic setup for irit-stac
1. Fork the irit-stac repository on github:
   * Log into github,
   * Go to the home page for the
   [irit-stac](https://github.com/irit-melodi/irit-stac/)
   repository,
   * Click on the "Fork" button.
2. Clone your fork of irit-stac onto your machine:
```sh
git clone https://github.com/<yourgithubusername>/irit-stac.git
```
This will fetch the latest source code from your repository onto your local
machine. Your local copy keeps a pointer to your fork on github: the latter
is a "remote repository" named "origin".
3. Add to your local copy another remote repository: the original
irit-melodi/irit-stac repository.
```sh
cd irit-stac
git remote add upstream https://github.com/irit-melodi/irit-stac.git
```
[Source: GitHub help](https://help.github.com/articles/configuring-a-remote-for-a-fork/)
4. Create and activate a conda environment named `irit-stac`:
```sh
conda env create
source activate irit-stac
```
The first command creates a conda environment (a sort of sandbox) from the
specifications contained in the file `environment.yml`.
This environment is named `irit-stac` and includes
python 2.7, graphviz 2.38.0, scipy, pip, scikit-learn and a specific version
of pydot.
The second command activates the environment, which you have to do every time
you want to run experiments.
5. Install irit-stac from the local version on your machine. This should
automatically fetch the educe/attelo dependencies.
```sh
pip install -r requirements.txt
```
6. Install NLTK data files
```sh
python setup-nltk.py
```
7. Create a local link to the STAC corpus
```sh
ln -s /path/to/Stac/data data
```

### Run a basic experiment
1. Gather instances for training or testing.
```sh
irit-stac gather
```
2. Run an experiment on these instances: learn models and evaluate their
performances.
```sh
irit-stac evaluate
```

### Update your locally installed irit-stac
1. Activate your sandbox, if you haven't already done so.
```sh
source activate irit-stac
```
2. Fetch the latest version of the source code for irit-stac from your fork
on github.
```sh
git pull
```
3. Install the latest version of irit-stac.
```sh
pip install -r requirements.txt
```
This will also fetch and install the latest version of the dependencies,
including educe and attelo.

### Keep your fork in sync
Keeping your fork in sync with changes in the upstream repository involves
at least four steps, in its simplest form.
(Source: GitHub help)[https://help.github.com/articles/syncing-a-fork/]

1. Fetch upstream branches and their commits on your machine.
```sh
git fetch upstream
```
2. Check out your fork's local master branch.
```sh
git checkout master
```
3. Merge the changes from upstream/master into your local master branch.
```sh
git merge upstream/master
```
4. Push the commits from your local master branch to the master branch of
your remote fork.
```sh
git push
```

### Update your conda environment
1. Activate your conda environment if necessary
```sh
source activate irit-stac
```
2. Update the packages installed via conda in your conda environment.
```sh
conda update --all
```

You should probably take the
[conda 30-minute test drive](http://conda.pydata.org/docs/test-drive.html)
anyway.

## Setup your own modifiable version of attelo
1. Fork attelo (cf. supra).
2. Clone your fork of attelo onto your machine:
```sh
git clone https://github.com/<yourgithubusername>/irit-stac.git
```
If you were still in the irit-stac folder, you might want to get out first
(e.g. go one level up with "cd .."), so that attelo and irit-stac are cloned
into distinct folders.
3. Declare an upstream remote repository for your local attelo.
```sh
cd attelo
git remote add upstream https://github.com/irit-melodi/attelo.git
```
4. Have your local copy of irit-stac depend on your local copy of attelo.
You need to edit `irit-stac/requirements.txt`, comment the line about attelo
and point to your local version of attelo instead:
```
# -e git+https://github.com/irit-melodi/attelo.git#egg=attelo
-e /path/to/your/local/attelo
```

## Developing
### Feature requests and bug reports
To report a bug or request a feature, please open an issue on GitHub in the
relevant repository, for example https://github.com/irit-melodi/educe/issues
for educe.

### Develop a new feature
The most common git workflow consists in creating a new branch each time you
want to develop a new feature or fix a bug.
Ideally, a branch should have a goal that can be reached within a few hours
or days.
There are a few reasons to aim for that.
One is that branches are easier to review and merge when their diff is not
too long.
Another reason is that breaking your current, big task into smaller subtasks
enables you to better assess and track your progress towards the completion
of the bigger task.

Let us assume for this example that you want to implement a new loss function
in attelo.

1. Create a local branch, named "fancy-loss", from the master branch of
attelo.
Inside your attelo folder:
```sh
git checkout master
git checkout -b fancy-loss
```
2. Implement your fancy loss in several local commits. As long as you have
not made your commits public by pushing them on github, you are absolutely
free to rewrite the history of your local branch (for example by amending
or deleting commits).
```sh
git add attelo/metrics/fancy_loss.py
git commit -m "ENH new fancy loss"
```
```sh
git add attelo/metrics/fancy_loss.py
git commit -m "FIX bad default value for fancy loss"
```
etc
3. Create a "fancy-loss" branch on your fork on GitHub (aka "origin") and
push the commits from your local "fancy-loss" branch to this new
"fancy-loss" branch on origin.
```sh
git push -u origin fancy-loss
```
4. You can continue to work on your branch if necessary. New commits can
then be pushed in the most simple way from local/fancy-loss to
origin/fancy-loss.
```sh
git push
```
5. When you are done, go to the GitHub page of your attelo fork and create
a Pull Request from "fancy-loss" to "master".
You will be asked to provide a title and description for your Pull Request,
and you will be shown the summary diff of your changes.
If you notice that you forgot to change anything, you can make new commits
on local/fancy-loss, push them to origin/fancy-loss. Your new commits will
be automatically added to your Pull Request.
When you are really done, you can click on "merge the Pull Request", then
"Close Pull Request and delete branch".
6. If you are sure you pushed all your changes, it is time to clean up
your local fancy-loss branch.
```sh
git checkout -D fancy-loss
```
7. Delete your local copy of origin/fancy-loss (or: prune dead branches
from origin).
```sh
git remote prune origin
```

### Contributing code
If you want to contribute code to the irit-melodi repository, you need
to create a Pull Request from a branch (master or a feature branch) on
your fork (origin) to the "master" branch on irit-melodi (upstream).
Before you create the Pull Request, you need to sync your fork with
the upstream repository.
Both procedures are described above, so a more detailed description
is hopefully unnecessary.

### Coding style and guidelines
Our parsing pipeline depends a lot on [scikit-learn](http://scikit-learn.org).
This library provides, in particular, preprocessing utilities for
datasets, vectorizers and learners of various types: linear and non-linear
models, ensembles...
We try to follow their good practices:
* follow the same guidelines for coding (pep8, pylint),
* use the docstring specification from
[the numpy project](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt),
of which a concise example is available
[here](http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_numpy.html),
* adopt a similar [design and API](http://arxiv.org/abs/1309.0238)
(from 2013 but still relevant, for the most part).
