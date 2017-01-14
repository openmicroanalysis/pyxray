"""
Implementation of the database using a SQL database
"""

# Standard library modules.

# Third party modules.
import sqlalchemy.sql as sql

# Local modules.
from pyxray.base import _Database
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

    def transition_notation(self, transition, notation,
                            encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('transition_notation')

        transition_id = self._get_transition_id(self.engine, transition)
        notation_id = self._get_notation_id(self.engine, notation)

        tbl = table.transition_notation
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([getattr(tbl.c, encoding)])
        command = command.where(tbl.c.transition_id == transition_id)
        command = command.where(tbl.c.notation_id == notation_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition notation found'))

    def transition_energy_eV(self, element, transition, reference=None):
        if not reference:
            reference = self.get_default_reference('transition_energy_eV')

        element_id = self._get_element_id(self.engine, element)
        transition_id = self._get_transition_id(self.engine, transition)

        tbl = table.transition_energy
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.transition_id == transition_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition energy found'))

    def transition_probability(self, element, transition, reference=None):
        if not reference:
            reference = self.get_default_reference('transition_probability')

        element_id = self._get_element_id(self.engine, element)
        transition_id = self._get_transition_id(self.engine, transition)

        tbl = table.transition_probability
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.transition_id == transition_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition probability found'))

    def transition_relative_weight(self, element, transition, reference=None):
        if not reference:
            reference = self.get_default_reference('transition_relative_weight')

        element_id = self._get_element_id(self.engine, element)
        transition_id = self._get_transition_id(self.engine, transition)

        tbl = table.transition_relative_weight
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.transition_id == transition_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition relative weight found'))

    def transitionset_notation(self, transitionset, notation,
                            encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('transitionset_notation')

        transitionset_id = self._get_transitionset_id(self.engine, transitionset)
        notation_id = self._get_notation_id(self.engine, notation)

        tbl = table.transitionset_notation
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([getattr(tbl.c, encoding)])
        command = command.where(tbl.c.transitionset_id == transitionset_id)
        command = command.where(tbl.c.notation_id == notation_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition set notation found'))

    def transitionset_energy_eV(self, element, transitionset, reference=None):
        if not reference:
            reference = self.get_default_reference('transitionset_energy_eV')

        element_id = self._get_element_id(self.engine, element)
        transitionset_id = self._get_transitionset_id(self.engine, transitionset)

        tbl = table.transitionset_energy
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value_eV])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.transitionset_id == transitionset_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition set energy found'))

    def transitionset_relative_weight(self, element, transitionset, reference=None):
        if not reference:
            reference = self.get_default_reference('transitionset_relative_weight')

        element_id = self._get_element_id(self.engine, element)
        transitionset_id = self._get_transitionset_id(self.engine, transitionset)

        tbl = table.transitionset_relative_weight
        tbl.create(self.engine, checkfirst=True)
        command = sql.select([tbl.c.value])
        command = command.where(tbl.c.element_id == element_id)
        command = command.where(tbl.c.transitionset_id == transitionset_id)
        command = self._append_command_reference(command, tbl, reference)
        return self._retrieve_first(self.engine, command,
                                    NotFound('No transition set relative weight found'))
