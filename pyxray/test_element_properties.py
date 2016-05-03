#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pyxray.element_properties as ep

# Globals and constants variables.

class MockElementPropertiesDatabase(ep._ElementPropertiesDatabase):

    def mass_density_kg_m3(self, z):
        return 0.0

    def atomic_mass_kg_mol(self, z):
        return 0.0

class Test_ElementPropertiesDatabase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ep = MockElementPropertiesDatabase()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testsymbol(self):
        self.assertEqual('H', ep.symbol(1))
        self.assertEqual('Uuo', ep.symbol(118))

    def testname(self):
        self.assertEqual('Hydrogen', ep.name(1))
        self.assertEqual('Ununoctium', ep.name(118))

    def testatomic_number(self):
        self.assertEqual(1, ep.atomic_number(symbol='H'))
        self.assertEqual(1, ep.atomic_number(name='Hydrogen'))
        self.assertEqual(118, ep.atomic_number(symbol='Uuo'))
        self.assertEqual(118, ep.atomic_number(name='Ununoctium'))

class TestSargentWelchElementPropertiesDatabase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.ep = ep.SargentWelchElementPropertiesDatabase()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testmass_density(self):
        self.assertAlmostEqual(7.1900, ep.mass_density_kg_m3(24) / 1000.0)

        self.assertRaises(ValueError, self.ep.mass_density_kg_m3, 85)
        self.assertRaises(ValueError, self.ep.mass_density_kg_m3, 87)
        self.assertRaises(ValueError, self.ep.mass_density_kg_m3, 118)

    def testatomic_mass(self):
        self.assertAlmostEqual(51.996000, ep.atomic_mass_kg_mol(24) * 1000.0)

        self.assertRaises(ValueError, self.ep.atomic_mass_kg_mol, 118)

    def testsymbol(self):
        self.assertEqual('Al', ep.symbol(13))

    def testname(self):
        self.assertEqual('Aluminium', ep.name(13))

    def testatomic_number(self):
        self.assertEqual(13, ep.atomic_number(symbol='Al'))
        self.assertEqual(13, ep.atomic_number(name='Aluminium'))

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testmass_density(self):
        self.assertAlmostEqual(7.1900, ep.mass_density_kg_m3(24) / 1000.0)

    def testatomic_mass(self):
        self.assertAlmostEqual(51.996000, ep.atomic_mass_kg_mol(24) * 1000.0)

    def testsymbol(self):
        self.assertEqual('Al', ep.symbol(13))

    def testname(self):
        self.assertEqual('Aluminium', ep.name(13))

    def testatomic_number(self):
        self.assertEqual(13, ep.atomic_number(symbol='Al'))
        self.assertEqual(13, ep.atomic_number(name='Aluminium'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
