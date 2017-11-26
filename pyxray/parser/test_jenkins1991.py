#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.jenkins1991 import Jenkins1991TransitionNotationParser

# Globals and constants variables.

class TestJenkins1991TransitionNotationParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = Jenkins1991TransitionNotationParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(41, len(props))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
