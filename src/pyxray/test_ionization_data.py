#!/usr/bin/env python
""" """

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
import ionization_data

# Globals and constants variables.

class TestIonizationData(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
#
    def testenergy_eV(self):
        # Test Al K.
        self.assertAlmostEquals(1.564e3, ionization_data.energy_eV(13, 1), 4)

    def testexists(self):
        self.assertTrue(ionization_data.exists(13, 1))
        self.assertFalse(ionization_data.exists(13, 29))


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
