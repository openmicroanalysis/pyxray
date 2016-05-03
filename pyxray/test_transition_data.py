#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pyxray.transition_data as transition_data

# Globals and constants variables.

class TestRelaxationData(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testenergy_eV(self):
        # Al Ka1.
        self.assertAlmostEqual(1.48671e3, transition_data.energy_eV(13, [4, 1]), 4)

        # Li Ka1
        self.assertAlmostEqual(52.0, transition_data.energy_eV(3, [4, 1]), 4)

        # Al SKa3
        self.assertAlmostEqual(1496.1829, transition_data.energy_eV(13, [4, 1, 3]), 4)

    def testprobability(self):
        # Al Ka1.
        self.assertAlmostEqual(2.45528e-2, transition_data.probability(13, [4, 1]), 6)

        # Li Ka1
        self.assertAlmostEqual(1.06e-4, transition_data.probability(3, [4, 1]), 6)

        # Al SKa3
        expected = 8.0 * 2.45528e-2 / 100.0
        self.assertAlmostEqual(expected, transition_data.probability(13, [4, 1, 3]), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
