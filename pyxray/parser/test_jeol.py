#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.jeol import JEOLTransitionParser

# Globals and constants variables.

class TestJEOLTransitionParser(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.parser = JEOLTransitionParser()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(2308, len(props))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
