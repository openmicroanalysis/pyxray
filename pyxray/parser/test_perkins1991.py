#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.perkins1991 import Perkins1991Parser
# Globals and constants variables.

class TestJenkins1991TransitionNotationParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = Perkins1991Parser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(19189, len(props))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
