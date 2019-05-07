#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.perkins1991 import Perkins1991Parser
# Globals and constants variables.

def test_perkins1991():
    parser = Perkins1991Parser()
    assert len(list(parser)) == 19189
