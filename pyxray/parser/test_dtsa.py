#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pyxray.parser.dtsa import DtsaSubshellParser, DtsaLineParser

# Globals and constants variables.

def test_dtsa1992_subshell():
    parser = DtsaSubshellParser()
    props = list(parser)

    assert len(props) == 1045

    assert props[0].element.z == 3
    assert props[0].value_eV == pytest.approx(54.75, abs=1e-2)

    assert props[-1].element.z == 95
    assert props[-1].value_eV == pytest.approx(366.49, abs=1e-2)

def test_dtsa1992_line():
    parser = DtsaLineParser()
    props = list(parser)

    assert len(props) == 6434

    assert props[0].element.z == 3
    assert props[0].value_eV == pytest.approx(54.3000, abs=1e-4)

    assert props[1].element.z == 3
    assert props[1].value == pytest.approx(1.00000, abs=1e-5)

    assert props[-2].element.z == 95
    assert props[-2].value_eV == pytest.approx(378.5100, abs=1e-4)

    assert props[-1].element.z == 95
    assert props[-1].value == pytest.approx(0.01000, abs=1e-2)
