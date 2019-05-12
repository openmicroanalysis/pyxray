#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.
import pytest

# Local modules.
from pyxray.base import _DatabaseMixin

# Globals and constants variables.

class MockDatabase(_DatabaseMixin):

    def element(self, element):
        pass

    def element_atomic_number(self, element):
        pass

    def element_symbol(self, element, reference=None):
        pass

    def element_name(self, element, language='en', reference=None):
        pass

    def element_atomic_weight(self, element, reference=None):
        pass

    def element_mass_density_kg_per_m3(self, element, reference=None):
        pass

    def element_mass_density_g_per_cm3(self, element, reference=None):
        pass

    def element_xray_transitions(self, element, reference=None):
        pass

    def element_xray_transition(self, element, xraytransitionset=None, reference=None):
        pass

    def atomic_shell(self, atomic_shell):
        pass

    def atomic_shell_notation(self, atomic_shell, notation, encoding='utf16', reference=None):
        pass

    def atomic_subshell(self, atomic_subshell):
        pass

    def atomic_subshell_notation(self, atomic_subshell, notation, encoding='utf16', reference=None):
        pass

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        pass

    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
        pass

    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
        pass

    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
        pass

    def xray_transition(self, xraytransition):
        pass

    def xray_transition_notation(self, xraytransition, notation, encoding='utf16', reference=None):
        pass

    def xray_transition_energy_eV(self, element, xraytransition, reference=None):
        pass

    def xray_transition_probability(self, element, xraytransition, reference=None):
        pass

    def xray_transition_relative_weight(self, element, xraytransition, reference=None):
        pass

    def xray_transitionset(self, xraytransitionset):
        pass

    def xray_transitionset_notation(self, xraytransitionset, notation, encoding='utf16', reference=None):
        pass

    def xray_transitionset_energy_eV(self, element, xraytransitionset, reference=None):
        pass

    def xray_transitionset_relative_weight(self, element, xraytransitionset, reference=None):
        pass

    def xray_line(self, element, line, reference=None):
        pass

@pytest.fixture
def database():
    return MockDatabase()

# def test_base_get_default_reference(database):
#     assert database.get_default_reference('element_symbol') is None

#     with pytest.raises(ValueError):
#         database.get_default_reference('foo')

# def test_base_set_default_reference(database):
#     database.set_default_reference('element_symbol', 'doe2016')

#     assert database.get_default_reference('element_symbol') == 'doe2016'

#     with pytest.raises(ValueError):
#         database.set_default_reference('foo', 'doe2016')

