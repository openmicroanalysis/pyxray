"""
Current implementation of the database
"""

__all__ = [
    'set_default_reference',
    'get_default_reference',
    'element_atomic_number',
    'element_symbol',
    'element_name',
    'element_atomic_weight',
    'element_mass_density_kg_per_m3',
    'element_mass_density_g_per_cm3',
    'atomic_shell_notation',
    'atomic_subshell_notation',
    'atomic_subshell_binding_energy_eV',
    'atomic_subshell_radiative_width_eV',
    'atomic_subshell_nonradiative_width_eV',
    'atomic_subshell_occupancy',
    'transition_notation',
    'transition_energy_eV',
    'transition_probability',
    'transition_relative_weight',
    'transitionset_notation',
    'transitionset_energy_eV',
    'transitionset_relative_weight']

# Standard library modules.
import os

# Third party modules.

# Local modules.

# Globals and constants variables.

def _init_sql_database():
    from sqlalchemy import create_engine
    from pyxray.sql.data import SqlEngineDatabase

    basedir = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(basedir, 'data', 'pyxray.sql')
    if not os.path.exists(filepath):
        raise RuntimeError('Cannot find SQL database at location {0}'
                           .format(filepath))

    engine = create_engine('sqlite:///' + filepath)
    return SqlEngineDatabase(engine)

database = _init_sql_database()

set_default_reference = database.set_default_reference
get_default_reference = database.get_default_reference
element_atomic_number = database.element_atomic_number
element_symbol = database.element_symbol
element_name = database.element_name
element_atomic_weight = database.element_atomic_weight
element_mass_density_kg_per_m3 = database.element_mass_density_kg_per_m3
element_mass_density_g_per_cm3 = database.element_mass_density_g_per_cm3
atomic_shell_notation = database.atomic_shell_notation
atomic_subshell_notation = database.atomic_subshell_notation
atomic_subshell_binding_energy_eV = database.atomic_subshell_binding_energy_eV
atomic_subshell_radiative_width_eV = database.atomic_subshell_radiative_width_eV
atomic_subshell_nonradiative_width_eV = database.atomic_subshell_nonradiative_width_eV
atomic_subshell_occupancy = database.atomic_subshell_occupancy
transition_notation = database.transition_notation
transition_energy_eV = database.transition_energy_eV
transition_probability = database.transition_probability
transition_relative_weight = database.transition_relative_weight
transitionset_notation = database.transitionset_notation
transitionset_energy_eV = database.transitionset_energy_eV
transitionset_relative_weight = database.transitionset_relative_weight
