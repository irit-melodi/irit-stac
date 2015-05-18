"""
irit-rst-dt subcommands
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3)

from . import (clean,
               count,
               evaluate,
               gather,
               model,
               parse,
               serve,
               stop)

SUBCOMMANDS =\
    [
        gather,
        evaluate,
        count,
        clean,
        model,
        parse,
        serve,
        stop,
    ]
