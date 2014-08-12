"""
irit-rst-dt subcommands
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3)

from . import evaluate, features, gather, clean, model

SUBCOMMANDS = [gather, evaluate, model, features, clean]
