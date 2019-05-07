#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.sargent_welch import \
    SargentWelchElementAtomicWeightParser, SargentWelchElementMassDensityParser

# Globals and constants variables.

def test_sargentwelch2010_atomicweight():
    parser = SargentWelchElementAtomicWeightParser()
    assert len(list(parser)) == 106

def test_sargentwelch2010_massdensity():
    parser = SargentWelchElementMassDensityParser()
    assert len(list(parser)) == 94