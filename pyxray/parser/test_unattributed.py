#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.unattributed import \
    (ElementSymbolPropertyParser, AtomicShellNotationParser,
     AtomicSubshellNotationParser, TransitionNotationParser,
     iter_subshells)

# Globals and constants variables.

class Testunattributed(unittest.TestCase):

    def testiter_subshells(self):
        self.assertEqual(1, len(list(iter_subshells(1))))
        self.assertEqual(4, len(list(iter_subshells(2))))
        self.assertEqual(49, len(list(iter_subshells(7))))

class TestElementSymbolPropertyParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = ElementSymbolPropertyParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(118, len(props))

class TestAtomicShellNotationParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = AtomicShellNotationParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(21, len(props))

class TestAtomicSubshellNotationParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = AtomicSubshellNotationParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(147, len(props))

class TestTransitionNotationParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = TransitionNotationParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(1176, len(props))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
