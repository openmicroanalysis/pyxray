#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.jenkins1991 import Jenkins1991TransitionNotationParser

# Globals and constants variables.

def test_jenkins1991():
    parser = Jenkins1991TransitionNotationParser()
    assert len(list(parser)) == 44
