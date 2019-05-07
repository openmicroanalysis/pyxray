#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.wikipedia import WikipediaElementNameParser

# Globals and constants variables.

def test_wikipedia():
    parser = WikipediaElementNameParser()
    assert len(list(parser)) > 0
