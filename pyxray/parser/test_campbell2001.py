#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.campbell2001 import CampbellAtomicSubshellRadiativeWidthParser

# Globals and constants variables.

class TestCampbellAtomicSubshellRadiativeWidthParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = CampbellAtomicSubshellRadiativeWidthParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(963, len(props))

        self.assertEqual(10, props[0].element.z)
        self.assertAlmostEqual(0.24, props[0].value_eV, 2)

        self.assertEqual(92, props[962].element.z)
        self.assertAlmostEqual(0.31, props[962].value_eV, 2)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
