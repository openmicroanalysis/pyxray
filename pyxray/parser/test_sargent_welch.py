#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.sargent_welch import \
    SargentWelchElementAtomicWeightParser, SargentWelchElementMassDensityParser

# Globals and constants variables.

class TestSargentWelchElementAtomicWeightParser(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.parser = SargentWelchElementAtomicWeightParser()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(106, len(props))

class TestSargentWelchElementMassDensityParser(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.parser = SargentWelchElementMassDensityParser()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(94, len(props))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
