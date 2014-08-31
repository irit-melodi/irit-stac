"""
irit-rst-dt subcommands
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3)

from . import\
    clean,\
    count,\
    evaluate,\
    features,\
    gather,\
    model,\
    parse

SUBCOMMANDS = [gather, evaluate, model, parse, features, count, clean]
