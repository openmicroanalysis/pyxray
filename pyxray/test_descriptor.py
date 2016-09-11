#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.descriptor import \
    (Element, AtomicShell, AtomicSubshell, Reference)

# Globals and constants variables.

class TestElement(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.element = Element(6)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual(6, self.element.z)
        self.assertEqual(6, self.element.atomic_number)

    def testvalidable(self):
        self.assertRaises(ValueError, Element, 0)
        self.assertRaises(ValueError, Element, 119)
        self.assertRaises(ValueError, Element.validate, 0)
        self.assertRaises(ValueError, Element.validate, 119)

    def testimmutable(self):
        self.assertRaises(AttributeError, setattr,
                          self.element, 'atomic_number', 7)
        self.assertRaises(AttributeError, delattr,
                          self.element, 'atomic_number')
        self.assertRaises(AttributeError, setattr,
                          self.element, 'abc', 7)

    def testcachable(self):
        self.assertEqual(Element(6), self.element)
        self.assertIs(Element(6), self.element)

    def testreprable(self):
        self.assertEqual('Element(z=6)', repr(self.element))

class TestAtomicShell(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.atomicshell = AtomicShell(3)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual(3, self.atomicshell.n)
        self.assertEqual(3, self.atomicshell.principal_quantum_number)

    def testvalidable(self):
        self.assertRaises(ValueError, AtomicShell, 0)
        self.assertRaises(ValueError, AtomicShell.validate, 0)

    def testimmutable(self):
        self.assertRaises(AttributeError, setattr,
                          self.atomicshell, 'principal_quantum_number', 4)
        self.assertRaises(AttributeError, delattr,
                          self.atomicshell, 'principal_quantum_number')
        self.assertRaises(AttributeError, setattr,
                          self.atomicshell, 'abc', 7)

    def testcachable(self):
        self.assertEqual(AtomicShell(3), self.atomicshell)
        self.assertIs(AtomicShell(3), self.atomicshell)

    def testreprable(self):
        self.assertEqual('AtomicShell(n=3)', repr(self.atomicshell))

class TestAtomicSubshell(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.atomicsubshell = AtomicSubshell(3, 0, 1)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual(AtomicShell(3), self.atomicsubshell.atomic_shell)
        self.assertEqual(3, self.atomicsubshell.n)
        self.assertEqual(3, self.atomicsubshell.principal_quantum_number)
        self.assertEqual(0, self.atomicsubshell.l)
        self.assertEqual(0, self.atomicsubshell.azimuthal_quantum_number)
        self.assertEqual(1, self.atomicsubshell.j_n)
        self.assertEqual(1, self.atomicsubshell.total_angular_momentum_nominator)
        self.assertAlmostEqual(0.5, self.atomicsubshell.j)
        self.assertAlmostEqual(0.5, self.atomicsubshell.total_angular_momentum)

    def testvalidable(self):
        self.assertRaises(ValueError, AtomicSubshell, 3, 0, 5)
        self.assertRaises(ValueError, AtomicSubshell.validate, 3, 0, 5)
        self.assertRaises(ValueError, AtomicSubshell, 3, -1, 1)
        self.assertRaises(ValueError, AtomicSubshell.validate, 3, -1, 1)
        self.assertRaises(ValueError, AtomicSubshell, 3, 3, 1)
        self.assertRaises(ValueError, AtomicSubshell.validate, 3, 3, 1)

    def testimmutable(self):
        self.assertRaises(AttributeError, setattr,
                          self.atomicsubshell, 'principal_quantum_number', 4)
        self.assertRaises(AttributeError, delattr,
                          self.atomicsubshell, 'principal_quantum_number')
        self.assertRaises(AttributeError, setattr,
                          self.atomicsubshell, 'abc', 7)

    def testcachable(self):
        self.assertEqual(AtomicSubshell(3, 0, 1), self.atomicsubshell)
        self.assertIs(AtomicSubshell(3, 0, 1), self.atomicsubshell)

    def testreprable(self):
        self.assertEqual('AtomicSubshell(n=3, l=0, j=0.5)', repr(self.atomicsubshell))

class TestReference(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ref = Reference('doe2016')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual('doe2016', self.ref.bibtexkey)
        self.assertIsNone(self.ref.author)

    def testvalidable(self):
        self.assertRaises(ValueError, Reference, '')
        self.assertRaises(ValueError, Reference.validate, '')
        self.assertRaises(ValueError, Reference, None)
        self.assertRaises(ValueError, Reference.validate, None)

    def testimmutable(self):
        self.assertRaises(AttributeError, setattr,
                          self.ref, 'bibtexkey', 'john')
        self.assertRaises(AttributeError, delattr,
                          self.ref, 'bibtexkey')
        self.assertRaises(AttributeError, setattr,
                          self.ref, 'abc', 7)

    def testcachable(self):
        self.assertEqual(Reference('doe2016'), self.ref)
        self.assertIs(Reference('doe2016'), self.ref)

    def testreprable(self):
        self.assertEqual('Reference(doe2016)', repr(self.ref))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
