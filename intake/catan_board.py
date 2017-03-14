"""Model of the Catan hex board.

== UNFINISHED AND UNUSED (2017-03-14) ==

This is intended to support the extraction of rich game states.
The first use case is to give the location of the robber at each dice
roll.

The hexagonal board consists of 37 hexes, oriented such that hexes on the
same horizontal line are separated by vertical edges.
Any hex can be located using two coordinates: the first is oriented from
North-West to South-East, the second South-West to North-East.

Coordinates increase by 2 units on either or both axes between any two
adjacent hexes.
For example, the neighbours of (3, 3) are:
W: (1, 1)
NW: (1, 3)
NE: (3, 5)
E: (5, 5)
SE: (5, 3)
SW: (3, 1)

Nodes correspond to the angles of hexes, they are potential sites for
settlements and cities.
The coordinates of the nodes around (3, 3) are:
NW: (2, 3)
N: (3, 4)
NE: (4, 5)
SE: (5, 4)
S: (4, 3)
SW: (3, 2)

Hexes are separated by edges, which are potential sites for roads.
The coordinates of the edges around (3, 3) are:
W: (2, 2)
NW: (2, 3)
NE: (3, 4)
E: (4, 4)
SE: (4, 3)
SW: (3, 2)

The western-most hex is at (1, 1), the eastern-most hex (on the same
horizontal line) is at (D, D).
"""

from __future__ import print_function

import re

# hex types:
# - the lowest numbered hex type is Desert ;
# - the highest numbered *land* hex type is Wood ;
# - the highest numbered hex type a robber can occupy is also Wood ;

# land hex types: desert, then clay, ore, sheep, wheat, wood
DESERT_HEX = 0
CLAY_HEX = 1
ORE_HEX = 2
SHEEP_HEX = 3
WHEAT_HEX = 4
WOOD_HEX = 5
MAX_LAND_HEX = 5
# water hex types: water and ports: misc then clay, ore, sheep, wheat,
# wood (in the same order as land resources)
WATER_HEX = 6
MISC_PORT_HEX = 7  # 3-for-1 port, must be first port hextype
CLAY_PORT_HEX = 8
ORE_PORT_HEX = 9
SHEEP_PORT_HEX = 10
WHEAT_PORT_HEX = 11
WOOD_PORT_HEX = 12
# and another round of hard-coded conventions
MISC_PORT = 0
CLAY_PORT = 1
ORE_PORT = 2
SHEEP_PORT = 3
WHEAT_PORT = 4
WOOD_PORT = 5
# highest numbered hex type which may hold a robber = highest land hex type
MAX_ROBBER_HEX = MAX_LAND_HEX


SOCBOARDLAYOUT_RE = r'SOCBoardLayout:game=(?P<game>[^\|]+)\|hexLayout={ (?P<hex_layout>[^\|]+) }\|numberLayout={ (?P<number_layout>[^\|]+) }\|robberHex=(?P<robber_hex>0x[0-9a-fA-F][0-9a-fA-F])'
SOCBOARDLAYOUT_MATCH = re.compile(SOCBOARDLAYOUT_RE)


class CatanBoard(object):
    """Board itself.

    Parameters
    ----------
    hex_layout : sequence of int
        General layout of the board, as a sequence of 37 terrain tiles for
        land, port, water.

    number_layout : sequence of int
        Production on the land hexes of the board, as a sequence of 19 number
        tokens.

    robber_hex : str
        Initial position of the robber, hexadecimal coordinates in 0xNN
        notation.
    """

    def __init__(self, hex_layout, number_layout, robber_hex):
        """Init"""
        self.hex_layout = hex_layout
        self.number_layout = number_layout
        self.robber_hex = robber_hex

    @classmethod
    def from_soclog_line(cls, soclog_line):
        """Parse a SOCBoardLayout message from a line in the soclog."""
        soclog_line = soclog_line.strip()
        msg_match = SOCBOARDLAYOUT_MATCH.search(soclog_line)
        if msg_match is not None:
            hex_layout = [int(x) for x
                          in msg_match.group('hex_layout').split(' ')]
            number_layout = [int(x) for x
                             in msg_match.group('number_layout').split(' ')]
            robber_hex = msg_match.group('robber_hex')
            return cls(hex_layout, number_layout, robber_hex)
        # backup
        return None


if __name__ == '__main__':
    with open('../svn-stac/data/socl-season1/s1-league1-game3/soclog/league1 31may-2012-05-31-19-59-37-+0100.soclog') as f:
        for line in f:
            if 'SOCBoardLayout' in line:
                CatanBoard.from_soclog_line(line)
