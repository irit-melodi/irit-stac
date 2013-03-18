# About

**IMPORTANT**

These scripts are meant to be run in a Git repository (Stac is a
subversion repo).

Here's what I do to instantiate it and to switch to the
corpus-reorg branch:

    cd Stac
    git svn init https://wwwsecu.irit.fr/svn/Stac\
        --trunk .\
        --tags tags\
        --branches branches\
        --prefix svn\
        --username XXXX
    git svn fetch

    # create a local corpus-reorg branch tracking the SVN one
    git branch svn/corpus-reorg corpus-reorg

    # switch to that branch
    git checkout corpus-regorg

# Inventory

## Script generators

These scripts themselves generate scripts, the idea being that you'd
have a glance through the generated code as a sanity check before
running it.

They are meant to be run in order (the cleanup progresses through
phases), ie. you run the first script generator and the resulting
script.  Then the second generator and resulting script, etc.

1. mk-cleanup-script : run once
2. mk-tidy-up-script : meant to be run until no changes (sorry)
3. populate-gold     : run when all is said and done

## Helper scripts

* delete-if-empty : svn delete an empty directory
* query-safe-to-delete-ac : was only used for my reserach purposes

## Example outputs

Any scripts whose names start with dates should be treated as sample
output. Because more stuff has been added to the corpus since the
first few times we've run them, you'll need to generate fresh versions
in a new SVN/Git branch
