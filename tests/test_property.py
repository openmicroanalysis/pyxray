#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pyxray.descriptor import Reference, Element
from pyxray.property import ElementSymbol

# Globals and constants variables.

@pytest.fixture
def reference():
    return Reference('test2016')

@pytest.fixture
def element_symbol(reference):
    return ElementSymbol(reference, Element(6), 'C')

def test_element_symbol(element_symbol, reference):
    assert element_symbol.reference == reference
    assert element_symbol.element == Element(6)
    assert element_symbol.value == 'C'

def test_element_symbol_validate(reference):
    with pytest.raises(ValueError):
        ElementSymbol(reference, Element(6), '')
        ElementSymbol(reference, Element(6), 'CCC')
        ElementSymbol(reference, Element(6), 'c')

