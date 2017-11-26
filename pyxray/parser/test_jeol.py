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
        super().setUp()

        self.parser = JEOLTransitionParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(2384, len(props))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
