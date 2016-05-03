"""
Utilities functions
"""

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