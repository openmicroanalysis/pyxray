#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.meta.reference import Reference

# Globals and constants variables.

class TestReference(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ref = Reference('doe2016', author='John Doe', year=2016)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testbibtexkey(self):
        self.assertEqual('doe2016', self.ref.bibtexkey)

    def testauthor(self):
        self.assertEqual('John Doe', self.ref.author)

    def testyear(self):
        self.assertEqual('2016', self.ref.year)

    def test__eq__(self):
        other = Reference('doe2016', author='John Doe', year='2016')
        self.assertTrue(self.ref == other)

    def test__ne__(self):
        other = Reference('doe2016', author='John Doe')
        self.assertTrue(self.ref != other)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
