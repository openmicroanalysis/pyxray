#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.jeol import JEOLTransitionParser

# Globals and constants variables.

def test_jeol():
    parser = JEOLTransitionParser()
    assert len(list(parser)) == 2372
