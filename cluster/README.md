## Using the harness on a SLURM cluster

The configuration we assume is that you have a team of users working
on different aspects of the system in a shared space. One of the users
(eg. Eric) should be designated “local admin”.

## Initialisation 1 (local admin)

1. Upload the corpora to a shared space

2. Install miniconda (Python 2.7 version for now; we think Python 3 is
   doable too but it'll probably involve some tweaks to educe…)

## Initialisation 2 (you)

1. Put the following in your .bashrc

   ```
   MINICONDA_DIR=/projets/melodi/miniconda
   PROJECT_DIR=/projets/melodi
   export PATH=$MINICONDA_DIR/bin:$PATH
   ```

   (PROJECT_DIR is not strictly speaking needed; it's just a handy
   way to refer to the shared space below)

2. Start bash (it's tcsh by default for us; I couldn't figure out
   how to change my login shell)

3. Create and activate your personal conda environment
   (HINT: is conda in your path? It should be after steps 1 and 2)

      ```
      conda create -n irit-stac-$USER scipy pip
      source activate irit-stac-$USER
      ```

4. Copy the STAC SVN to the project space: on your local machine

      ```
      cd /wherever/your/local/Stac-SVN/lives
      rsync -avH Stac/ cluster:/projets/melodi/Stac-YOUR-USER-NAME
      ```

5. Link the STAC SVN in

    ```
    cd $PROJECT_DIR # or just type path in yourself
    ln -s $PROJECT_DIR/Stac-$USER $HOME/Stac
    ```

6. (optional) modify the requirements.txt to point to your personal educe
   and attelo branch (HINT: you can refer to branches on GitHub
   repositories)

7. Run the usual install

   ```
   pip install -r requirements.txt
   ```

8. Set up your cluster scripts (replace vim with your favourite text
   editor below). You'll need to plug in your email address and
   absolute paths appropriate to your cluster

   ```
   for i in env gather.script; do
       cp cluster/$i.example cluster/$i
   done
   vim cluster/env
   vim cluster/gather.script
   ```

## Using the cluster scripts

1. Launch feature extraction

```
bash
cd Stac
sbatch code/cluster/gather.script
```

2. Look out for a slurm-?????.out file. Check its contents ocassionally.
   Does feature extraction seem to be properly running? How about a nice
   coffee then?

3. Launch the experiment (I assume here you'd been automatically logged
   out)

```
bash
cd Stac
chmod u+x code/cluster/go
code/cluster/go
```

HINT: the `cluster/go` script can accept arguments for `irit-stac
evaluate` on the command line
