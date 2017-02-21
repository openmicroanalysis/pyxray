"""
Implementation of the database using a SQL database
"""

# Standard library modules.

# Third party modules.
import sqlalchemy.sql as sql

# Local modules.
from pyxray.base import _Database
import pyxray.descriptor as descriptor
import pyxray.sql.table as table
from pyxray.sql.base import SqlEngineDatabaseMixin, NotFound

# Globals and constants variables.

class SqlEngineDatabase(_Database, SqlEngineDatabaseMixin):

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def _append_command_reference(self, command, table, reference):
        if reference:
            reference_id = self._get_reference_id(self.engine, reference)
            command = command.where(table.c.reference_id == reference_id)
        else:
            command = command.order_by(table.c.reference_id)
        return command

    def element(self, element):
        if isinstance(element, descriptor.Element):
            return element
        element_id = self._get_element_id(self.engine, element)
        return self._get_element(self.engine, element_id)

    def element_atomic_number(self, element):
        element_id = self._get_element_id(self.engine, element)

        tbl = table.element
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.atomic_number])
        command = command.where(tbl.c.id == element_id)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic number found'))

    def element_symbol(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('element_symbol')

        element_id = self._get_element_id(self.engine, element)

        tbl = table.element_symbol
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.symbol])
        command = command.where(tbl.c.element_id == element_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No symbol found'))

    def element_name(self, element, language='en', reference=None):
        if not reference:
            reference = self.get_default_reference('element_name')

        element_id = self._get_element_id(self.engine, element)
        language_id = self._get_language_id(self.engine, language)

        tbl = table.element_name
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.name])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.language_id == language_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No name found'))

    def element_atomic_weight(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('element_atomic_weight')

        element_id = self._get_element_id(self.engine, element)

        tbl = table.element_atomic_weight
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic weight found'))

    def element_mass_density_kg_per_m3(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('element_mass_density_kg_per_m3')

        element_id = self._get_element_id(self.engine, element)

        tbl = table.element_mass_density
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_kg_per_m3])
        command = command.where(tbl.c.element_id == element_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No mass density found'))

    def element_xray_transitions(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_probability')

        element_id = self._get_element_id(self.engine, element)

        tbl = table.xray_transition_probability
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.xray_transition_id])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.value > 0.0)
        command = self._append_command_reference(command, tbl, reference)
        result = self.engine.execute(command)
        rows = result.fetchall()
        if not rows:
            raise NotFound('No X-ray transition found')

        return tuple(self._get_xray_transition(self.engine, row[0]) for row in rows)

    def atomic_shell(self, atomic_shell):
        if isinstance(atomic_shell, descriptor.AtomicShell):
            return atomic_shell
        atomic_shell_id = self._get_atomic_shell_id(self.engine, atomic_shell)
        return self._get_atomic_shell(self.engine, atomic_shell_id)

    def atomic_shell_notation(self, atomic_shell, notation,
                              encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_shell_notation')

        atomic_shell_id = self._get_atomic_shell_id(self.engine, atomic_shell)
        notation_id = self._get_notation_id(self.engine, notation)

        tbl = table.atomic_shell_notation
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([getattr(tbl.c, encoding)])
        command = command.where(tbl.c.atomic_shell_id == atomic_shell_id)
        command = command.where(tbl.c.notation_id == notation_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic shell notation found'))

    def atomic_subshell(self, atomic_subshell):
        if isinstance(atomic_subshell, descriptor.AtomicSubshell):
            return atomic_subshell
        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)
        return self._get_atomic_subshell(self.engine, atomic_subshell_id)

    def atomic_subshell_notation(self, atomic_subshell, notation,
                                 encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_notation')

        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)
        notation_id = self._get_notation_id(self.engine, notation)

        tbl = table.atomic_subshell_notation
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([getattr(tbl.c, encoding)])
        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
        command = command.where(tbl.c.notation_id == notation_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic subshell notation found'))

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_binding_energy_eV')

        element_id = self._get_element_id(self.engine, element)
        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)

        tbl = table.atomic_subshell_binding_energy
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic subshell binding energy found'))

    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_radiative_width_eV')

        element_id = self._get_element_id(self.engine, element)
        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)

        tbl = table.atomic_subshell_radiative_width
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic subshell radiative width found'))

    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_nonradiative_width_eV')

        element_id = self._get_element_id(self.engine, element)
        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)

        tbl = table.atomic_subshell_nonradiative_width
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic subshell nonradiative width found'))

    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_occupancy')

        element_id = self._get_element_id(self.engine, element)
        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)

        tbl = table.atomic_subshell_occupancy
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No atomic subshell occupancy found'))

    def xray_transition(self, xraytransition):
        if isinstance(xraytransition, descriptor.XrayTransition):
            return xraytransition
        xray_transition_id = self._get_xray_transition_id(self.engine, xraytransition)
        return self._get_xray_transition(self.engine, xray_transition_id)

    def xray_transition_notation(self, xraytransition, notation,
                                 encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_notation')

        xray_transition_id = self._get_xray_transition_id(self.engine, xraytransition)
        notation_id = self._get_notation_id(self.engine, notation)

        tbl = table.xray_transition_notation
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([getattr(tbl.c, encoding)])
        command = command.where(tbl.c.xray_transition_id == xray_transition_id)
        command = command.where(tbl.c.notation_id == notation_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition notation found'))

    def xray_transition_energy_eV(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_energy_eV')

        element_id = self._get_element_id(self.engine, element)
        xray_transition_id = self._get_xray_transition_id(self.engine, xraytransition)

        tbl = table.xray_transition_energy
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.xray_transition_id == xray_transition_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition energy found'))

    def xray_transition_probability(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_probability')

        element_id = self._get_element_id(self.engine, element)
        xray_transition_id = self._get_xray_transition_id(self.engine, xraytransition)

        tbl = table.xray_transition_probability
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.xray_transition_id == xray_transition_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition probability found'))

    def xray_transition_relative_weight(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_relative_weight')

        element_id = self._get_element_id(self.engine, element)
        xray_transition_id = self._get_xray_transition_id(self.engine, xraytransition)

        tbl = table.xray_transition_relative_weight
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.xray_transition_id == xray_transition_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition relative weight found'))

    def xray_transitionset(self, xraytransitionset):
        if isinstance(xraytransitionset, descriptor.XrayTransitionSet):
            return xraytransitionset
        xray_transitionset_id = self._get_xray_transitionset_id(self.engine, xraytransitionset)
        return self._get_xray_transitionset(self.engine, xray_transitionset_id)

    def xray_transitionset_notation(self, xraytransitionset, notation,
                                    encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transitionset_notation')

        xray_transitionset_id = self._get_xray_transitionset_id(self.engine, xraytransitionset)
        notation_id = self._get_notation_id(self.engine, notation)

        tbl = table.xray_transitionset_notation
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([getattr(tbl.c, encoding)])
        command = command.where(tbl.c.xray_transitionset_id == xray_transitionset_id)
        command = command.where(tbl.c.notation_id == notation_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition set notation found'))

    def xray_transitionset_energy_eV(self, element, xraytransitionset, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transitionset_energy_eV')

        element_id = self._get_element_id(self.engine, element)
        xray_transitionset_id = self._get_xray_transitionset_id(self.engine, xraytransitionset)

        tbl = table.xray_transitionset_energy
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.xray_transitionset_id == xray_transitionset_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition set energy found'))

    def xray_transitionset_relative_weight(self, element, xraytransitionset, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transitionset_relative_weight')

        element_id = self._get_element_id(self.engine, element)
        xray_transitionset_id = self._get_xray_transitionset_id(self.engine, xraytransitionset)

        tbl = table.xray_transitionset_relative_weight
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.xray_transitionset_id == xray_transitionset_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No X-ray transition set relative weight found'))
