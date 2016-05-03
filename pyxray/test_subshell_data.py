#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import pyxray.subshell_data as subshell_data

# Globals and constants variables.

class TestIonizationData(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
#
    def testenergy_eV(self):
        # Test Al K.
        self.assertAlmostEqual(1.564e3, subshell_data.energy_eV(13, 1), 4)

    def testexists(self):
        self.assertTrue(subshell_data.exists(13, 1))
        self.assertFalse(subshell_data.exists(13, 29))

    def testwidth_eV(self):
        self.assertAlmostEqual(0.42, subshell_data.width_eV(13, 1), 4)
        self.assertRaises(ValueError, subshell_data.width_eV, 6, 1)


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
