"""
irit-rst-dt subcommands
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3)

from . import\
    clean,\
    evaluate,\
    features,\
    gather,\
    model,\
    parse

SUBCOMMANDS = [gather, evaluate, model, parse, features, clean]
