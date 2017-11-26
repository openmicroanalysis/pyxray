"""
Current implementation of the database
"""

__all__ = [
    'set_default_reference',
    'get_default_reference',
    'element',
    'element_atomic_number',
    'element_symbol',
    'element_name',
    'element_atomic_weight',
    'element_mass_density_kg_per_m3',
    'element_mass_density_g_per_cm3',
    'element_xray_transitions',
    'element_xray_transition',
    'print_element_xray_transitions',
    'atomic_shell',
    'atomic_shell_notation',
    'atomic_subshell',
    'atomic_subshell_notation',
    'atomic_subshell_binding_energy_eV',
    'atomic_subshell_radiative_width_eV',
    'atomic_subshell_nonradiative_width_eV',
    'atomic_subshell_occupancy',
    'xray_transition',
    'xray_transition_notation',
    'xray_transition_energy_eV',
    'xray_transition_probability',
    'xray_transition_relative_weight',
    'xray_transitionset',
    'xray_transitionset_notation',
    'xray_transitionset_energy_eV',
    'xray_transitionset_relative_weight',
    'xray_line',
    ]

# Standard library modules.
import os
import logging
logger = logging.getLogger(__name__)
import sqlite3
import atexit

# Third party modules.

# Local modules.
from pyxray.base import _Database, NotFound
from pyxray.sql.data import SqlDatabase

# Globals and constants variables.

class _EmptyDatabase(_Database):

    def element(self, element): #pragma: no cover
        raise NotFound

    def element_atomic_number(self, element): #pragma: no cover
        raise NotFound

    def element_symbol(self, element, reference=None): #pragma: no cover
        raise NotFound

    def element_name(self, element, language='en', reference=None): #pragma: no cover
        raise NotFound

    def element_atomic_weight(self, element, reference=None): #pragma: no cover
        raise NotFound

    def element_mass_density_kg_per_m3(self, element, reference=None): #pragma: no cover
        raise NotFound

    def element_mass_density_g_per_cm3(self, element, reference=None): #pragma: no cover
        raise NotFound

    def element_xray_transitions(self, element, reference=None): #pragma: no cover
        raise NotFound

    def element_xray_transition(self, element, xraytransition, reference=None):
        raise NotFound

    def atomic_shell(self, atomic_shell): #pragma: no cover
        raise NotFound

    def atomic_shell_notation(self, atomic_shell, notation, encoding='utf16', reference=None): #pragma: no cover
        raise NotFound

    def atomic_subshell(self, atomic_subshell): #pragma: no cover
        raise NotFound

    def atomic_subshell_notation(self, atomic_subshell, notation, encoding='utf16', reference=None): #pragma: no cover
        raise NotFound

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None): #pragma: no cover
        raise NotFound

    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None): #pragma: no cover
        raise NotFound

    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None): #pragma: no cover
        raise NotFound

    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None): #pragma: no cover
        raise NotFound

    def xray_transition(self, xraytransition): #pragma: no cover
        raise NotFound

    def xray_transition_notation(self, xraytransition, notation, encoding='utf16', reference=None): #pragma: no cover
        raise NotFound

    def xray_transition_energy_eV(self, element, xraytransition, reference=None): #pragma: no cover
        raise NotFound

    def xray_transition_probability(self, element, xraytransition, reference=None): #pragma: no cover
        raise NotFound

    def xray_transition_relative_weight(self, element, xraytransition, reference=None): #pragma: no cover
        raise NotFound

    def xray_transitionset(self, xraytransitionset): #pragma: no cover
        raise NotFound

    def xray_transitionset_notation(self, xraytransitionset, notation, encoding='utf16', reference=None): #pragma: no cover
        raise NotFound

    def xray_transitionset_energy_eV(self, element, xraytransitionset, reference=None): #pragma: no cover
        raise NotFound

    def xray_transitionset_relative_weight(self, element, xraytransitionset, reference=None): #pragma: no cover
        raise NotFound

    def xray_line(self, element, line, reference=None): #pragma: no cover
        raise NotFound

connection = None

def _init_sql_database():
    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, 'data', 'pyxray.sql')
    if not os.path.exists(filepath):
        raise RuntimeError('Cannot find SQL database at location {0}'
                           .format(filepath))

    global connection
    connection = sqlite3.connect(filepath, check_same_thread=False)
    return SqlDatabase(connection)

@atexit.register
def _close_sql_database():
    global connection
    if hasattr(connection, 'close'):
        connection.close()

try:
    database = _init_sql_database()
except:
    logger.error("No SQL database found")
    database = _EmptyDatabase()

set_default_reference = database.set_default_reference
get_default_reference = database.get_default_reference
element = database.element
element_atomic_number = database.element_atomic_number
element_symbol = database.element_symbol
element_name = database.element_name
element_atomic_weight = database.element_atomic_weight
element_mass_density_kg_per_m3 = database.element_mass_density_kg_per_m3
element_mass_density_g_per_cm3 = database.element_mass_density_g_per_cm3
element_xray_transitions = database.element_xray_transitions
element_xray_transition = database.element_xray_transition
print_element_xray_transitions = database.print_element_xray_transitions
atomic_shell = database.atomic_shell
atomic_shell_notation = database.atomic_shell_notation
atomic_subshell = database.atomic_subshell
atomic_subshell_notation = database.atomic_subshell_notation
atomic_subshell_binding_energy_eV = database.atomic_subshell_binding_energy_eV
atomic_subshell_radiative_width_eV = database.atomic_subshell_radiative_width_eV
atomic_subshell_nonradiative_width_eV = database.atomic_subshell_nonradiative_width_eV
atomic_subshell_occupancy = database.atomic_subshell_occupancy
xray_transition = database.xray_transition
xray_transition_notation = database.xray_transition_notation
xray_transition_energy_eV = database.xray_transition_energy_eV
xray_transition_probability = database.xray_transition_probability
xray_transition_relative_weight = database.xray_transition_relative_weight
xray_transitionset = database.xray_transitionset
xray_transitionset_notation = database.xray_transitionset_notation
xray_transitionset_energy_eV = database.xray_transitionset_energy_eV
xray_transitionset_relative_weight = database.xray_transitionset_relative_weight
xray_line = database.xray_line
