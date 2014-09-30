#!/usr/bin/env python
"""
================================================================================
:mod:`util` -- Utilities functions
================================================================================

.. module:: util
   :synopsis: Utilities functions

.. inheritance-diagram:: pyxray.util

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2014 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

c = 299792458
h_eVs = 4.13566733e-15

def energy_to_wavelength_m(energy_eV):
    return h_eVs * c / energy_eV

def wavelength_to_energy_eV(wavelength_m):
    return h_eVs * c / wavelength_m