#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.subshell import Subshell

# Globals and constants variables.
from pyxray.subshell import _IUPACS, _ORBITALS, _SIEGBAHNS

class TestSubshell(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        for i in range(1, 31):
            x = Subshell(13, i)
            setattr(self, 'x%i' % i, x)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testindex(self):
        for i in range(1, 31):
            x = getattr(self, "x%i" % i)
            self.assertEqual(i, x.index)

    def testorbital(self):
        for i in range(1, 31):
            x = getattr(self, "x%i" % i)
            self.assertEqual(_ORBITALS[i - 1], x.orbital)

    def testiupac(self):
        for i in range(1, 31):
            x = getattr(self, "x%i" % i)
            self.assertEqual(_IUPACS[i - 1], x.iupac)

    def testsiegbahn(self):
        for i in range(1, 31):
            x = getattr(self, "x%i" % i)
            self.assertEqual(_SIEGBAHNS[i - 1], x.siegbahn)

    def testfamily(self):
        # K
        self.assertEqual('K', self.x1.family)

        # L
        for i in range(2, 5):
            x = getattr(self, "x%i" % i)
            self.assertEqual("L", x.family)

        # M
        for i in range(5, 10):
            x = getattr(self, "x%i" % i)
            self.assertEqual("M", x.family)

        # N
        for i in range(10, 17):
            x = getattr(self, "x%i" % i)
            self.assertEqual("N", x.family)

        # O
        for i in range(17, 24):
            x = getattr(self, "x%i" % i)
            self.assertEqual("O", x.family)

        # P
        for i in range(24, 29):
            x = getattr(self, "x%i" % i)
            self.assertEqual("P", x.family)

        # Q
        self.assertEqual('Q', self.x29.family)

        # outer
        self.assertEqual(None, self.x30.family)

    def testionization_energy_eV(self):
        self.assertAlmostEqual(1.564e3, self.x1.ionization_energy_eV, 4)

    def testexists(self):
        self.assertTrue(self.x1.exists())
        self.assertFalse(self.x29.exists())

    def testwidth_eV(self):
        self.assertAlmostEqual(0.42, self.x1.width_eV, 4)
        self.assertAlmostEqual(0.0, self.x6.width_eV, 4)

    def testsort(self):
        subshells = [Subshell(29, 5), Subshell(29, 1), Subshell(29, 3)]
        subshells.sort()
        self.assertEqual(Subshell(29, 1), subshells[0])
        self.assertEqual(Subshell(29, 3), subshells[1])
        self.assertEqual(Subshell(29, 5), subshells[2])

        subshells = [Subshell(13, 5), Subshell(29, 1), Subshell(29, 3)]
        subshells.sort()
        self.assertEqual(Subshell(13, 5), subshells[0])
        self.assertEqual(Subshell(29, 1), subshells[1])
        self.assertEqual(Subshell(29, 3), subshells[2])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
