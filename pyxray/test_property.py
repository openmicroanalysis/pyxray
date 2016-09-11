#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.descriptor import Reference, Element
from pyxray.property import ElementSymbol

# Globals and constants variables.

REFERENCE_TEST = Reference('test2016')

class TestElementSymbol(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.prop = ElementSymbol(REFERENCE_TEST, Element(6), 'C')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual(REFERENCE_TEST, self.prop.reference)
        self.assertIs(REFERENCE_TEST, self.prop.reference)
        self.assertEqual(Element(6), self.prop.element)
        self.assertIs(Element(6), self.prop.element)
        self.assertEqual('C', self.prop.symbol)

    def testvalidable(self):
        self.assertRaises(ValueError, ElementSymbol,
                          REFERENCE_TEST, Element(6), '')
        self.assertRaises(ValueError, ElementSymbol,
                          REFERENCE_TEST, Element(6), 'CCCC')
        self.assertRaises(ValueError, ElementSymbol,
                          REFERENCE_TEST, Element(6), 'c')

    def testimmutable(self):
        self.assertRaises(AttributeError, setattr,
                          self.prop, 'reference', None)
        self.assertRaises(AttributeError, delattr,
                          self.prop, 'reference')
        self.assertRaises(AttributeError, setattr,
                          self.prop, 'element', None)
        self.assertRaises(AttributeError, delattr,
                          self.prop, 'element')
        self.assertRaises(AttributeError, setattr,
                          self.prop, 'symbol', None)
        self.assertRaises(AttributeError, delattr,
                          self.prop, 'symbol')
        self.assertRaises(AttributeError, setattr,
                          self.prop, 'abc', 7)

    def testreprable(self):
        self.assertEqual('ElementSymbol(test2016, z=6, symbol=C)', repr(self.prop))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
