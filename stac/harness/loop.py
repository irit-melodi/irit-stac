'''
Harness loop management
'''

from collections import namedtuple
from enum import Enum

# pylint: disable=too-few-public-methods

# pylint: disable=pointless-string-statement
LoopConfig = namedtuple("LoopConfig",
                        ["eval_dir",
                         "scratch_dir",
                         "naughty_filters",
                         "stage",
                         "folds",
                         "fold_file",
                         "n_jobs",
                         "dataset",
                         "testset"])
"that which is common to outerish loops"


DataConfig = namedtuple("DataConfig",
                        ["pack",
                         "folds"])
"data tables we have read"
# pylint: enable=pointless-string-statement


class ClusterStage(Enum):
    '''
    What stage of cluster usage we are at
    '''
    start = 1
    main = 2
    combined_models = 3
    end = 4
