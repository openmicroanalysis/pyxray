#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.composition import CompositionConverter

# Globals and constants variables.

class TestCompositionConverter(unittest.TestCase):

    def testfrom_formula(self):
        expected_al = 0.21358626371988801
        expected_na = 0.27298103136883051
        expected_b = 0.51343270491128157

        comp = CompositionConverter.from_formula('Al2Na3B12')
        mass_fractions = comp.to_mass_fractions()
        self.assertAlmostEqual(expected_al, mass_fractions[13], 4)
        self.assertAlmostEqual(expected_na, mass_fractions[11], 4)
        self.assertAlmostEqual(expected_b, mass_fractions[5], 4)

        comp = CompositionConverter.from_formula('Al 2 Na 3 B 12')
        mass_fractions = comp.to_mass_fractions()
        self.assertAlmostEqual(expected_al, mass_fractions[13], 4)
        self.assertAlmostEqual(expected_na, mass_fractions[11], 4)
        self.assertAlmostEqual(expected_b, mass_fractions[5], 4)

        comp = CompositionConverter.from_formula('Al2 Na3 B12')
        mass_fractions = comp.to_mass_fractions()
        self.assertAlmostEqual(expected_al, mass_fractions[13], 4)
        self.assertAlmostEqual(expected_na, mass_fractions[11], 4)
        self.assertAlmostEqual(expected_b, mass_fractions[5], 4)

        self.assertRaises(Exception, CompositionConverter.from_formula, 'Aq2 Na3 B12')

        comp = CompositionConverter.from_formula('Al2')
        mass_fractions = comp.to_mass_fractions()
        self.assertAlmostEqual(1.0, mass_fractions[13], 4)

    def testfrom_oxide_fractions(self):
        # From https://www.researchgate.net/post/How_can_I_calculate_elemental_weight_percent_from_oxide_weight_percent_given_by_XRF
        oxide_fractions = {'MnO': 0.07, 'MgO': 0.1, 'CaO': 55.84, 'P2O5': 42.05, 'H2O': 1.86}
        comp = CompositionConverter.from_oxide_fractions(oxide_fractions)
        mass_fractions = comp.to_mass_fractions()
        self.assertAlmostEqual(0.055, mass_fractions[25] * 100.0, 3)
        self.assertAlmostEqual(0.107, mass_fractions[12] * 100.0, 3)
        self.assertAlmostEqual(50.880, mass_fractions[20] * 100.0, 3)
        self.assertAlmostEqual(9.243, mass_fractions[15] * 100.0, 3)
        self.assertAlmostEqual(0.826, mass_fractions[1] * 100.0, 3)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
