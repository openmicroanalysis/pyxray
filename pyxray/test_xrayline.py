#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pyxray
from pyxray.xrayline import XrayLine

# Globals and constants variables.

class TestXrayLine(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.x = XrayLine(13, 'Ka1')

    def testskeleton(self):
        self.assertEqual(13, self.x.element.atomic_number)

        self.assertEqual(2, self.x.line.source_subshell.n)
        self.assertEqual(1, self.x.line.destination_subshell.n)

        self.assertFalse(self.x.is_xray_transitionset())

    def testimmutable(self):
        self.assertRaises(AttributeError, setattr,
                          self.x, 'element', 13)
        self.assertRaises(AttributeError, delattr,
                          self.x, 'Ka1')

    def testcachable(self):
        self.assertEqual(XrayLine(13, 'Ka1'), self.x)
        self.assertIs(XrayLine(13, 'Ka1'), self.x)

        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertEqual(x, self.x)
        self.assertIs(x, self.x)

    def testreprable(self):
        self.assertEqual('<XrayLine(Al K–L3)>', repr(self.x))

    def test__hash__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertEqual(hash(x), hash(self.x))

    def testiupac(self):
        self.assertEqual('Al K\u2013L3', self.x.iupac)

    def testsiegbahn(self):
        self.assertEqual('Al K\u03b11', self.x.siegbahn)

    def test__eq__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertEqual(x, self.x)

    def test__ne__(self):
        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(2, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(14), line)
        self.assertNotEqual(x, self.x)

        K = pyxray.AtomicSubshell(1, 0, 1)
        L3 = pyxray.AtomicSubshell(3, 1, 3)
        line = pyxray.XrayTransition(L3, K)
        x = XrayLine(pyxray.Element(13), line)
        self.assertNotEqual(x, self.x)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
