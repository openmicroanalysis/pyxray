#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pyxray.parser.nist import NISTElementAtomicWeightParser

# Globals and constants variables.

def test_coursey2015():
    parser = NISTElementAtomicWeightParser()
    props = list(parser)

    assert len(props) == 84

    assert props[70].element.z == 73
    assert props[70].value == pytest.approx(180.94788, abs=1e-5)
