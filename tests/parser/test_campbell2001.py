#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pyxray.parser.campbell2001 import CampbellAtomicSubshellRadiativeWidthParser

# Globals and constants variables.

def test_campbell2011():
    parser = CampbellAtomicSubshellRadiativeWidthParser()

    props = list(parser)
    assert len(props) == 963

    assert props[0].element.z == 10
    assert props[0].value_eV == pytest.approx(0.24, abs=1e-2)

    assert props[962].element.z == 92
    assert props[962].value_eV == pytest.approx(0.31, abs=1e-2)
