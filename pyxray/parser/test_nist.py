#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.nist import NISTElementAtomicWeightParser

# Globals and constants variables.

class TestNISTElementAtomicWeightParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = NISTElementAtomicWeightParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(84, len(props))

        self.assertEqual(73, props[70].element.z)
        self.assertAlmostEqual(180.94788, props[70].value, 5)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
