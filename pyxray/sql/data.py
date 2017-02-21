"""
Implementation of the database using a SQL database
"""

# Standard library modules.
import collections

# Third party modules.

# Local modules.
from pyxray.base import _Database
import pyxray.descriptor as descriptor
from pyxray.sql.base import SqlEngineDatabaseMixin, NotFound, SelectBuilder

# Globals and constants variables.

class SqlEngineDatabase(_Database, SqlEngineDatabaseMixin):

    def __init__(self, connection):
        super().__init__()
        self.connection = connection

    def _append_element(self, builder, table, column, element):
        if hasattr(element, 'atomic_number'):
            element = element.atomic_number

        if isinstance(element, str):
            builder.add_join('element_name', 'element_id', table, column)
            builder.add_join('element_symbol', 'element_id', table, column)
            builder.add_where('element_name', 'name', 'element',
                              'element_symbol', 'symbol', 'element')

        elif isinstance(element, int):
            builder.add_join('element', 'id', table, column)
            builder.add_where('element', 'atomic_number', 'element')

        else:
            raise NotFound('Cannot parse element: {}'.format(element))

        return {'element': element}

    def _append_atomic_shell(self, builder, table, column, atomic_shell):
        if hasattr(atomic_shell, 'principal_quantum_number'):
            atomic_shell = atomic_shell.principal_quantum_number

        if isinstance(atomic_shell, str):
            builder.add_join('atomic_shell_notation', 'atomic_shell_id', table, column)
            builder.add_where('atomic_shell_notation', 'ascii', 'atomic_shell',
                              'atomic_shell_notation', 'utf16', 'atomic_shell')

        elif isinstance(atomic_shell, int):
            builder.add_join('atomic_shell', 'id', table, column)
            builder.add_where('atomic_shell', 'principal_quantum_number', 'atomic_shell')

        else:
            raise NotFound('Cannot parse atomic shell: {}'.format(atomic_shell))

        return {'atomic_shell': atomic_shell}

    def _expand_atomic_subshell(self, atomic_subshell):
        n = 0
        l = -1
        j_n = 0
        if hasattr(atomic_subshell, 'principal_quantum_number') and \
                hasattr(atomic_subshell, 'azimuthal_quantum_number') and \
                hasattr(atomic_subshell, 'total_angular_momentum_nominator'):
            n = atomic_subshell.atomic_shell.principal_quantum_number
            l = atomic_subshell.azimuthal_quantum_number
            j_n = atomic_subshell.total_angular_momentum_nominator

        elif isinstance(atomic_subshell, collections.Sequence) and \
                len(atomic_subshell) == 3:
            n = atomic_subshell[0]
            l = atomic_subshell[1]
            j_n = atomic_subshell[2]

        return n, l, j_n

    def _append_atomic_subshell(self, builder, table, column, atomic_subshell):
        n, l, j_n = self._expand_atomic_subshell(atomic_subshell)

        builder.add_join('atomic_subshell', 'id', table, column)
        builder.add_join('atomic_shell', 'id', 'atomic_subshell', 'atomic_shell_id')

        if isinstance(atomic_subshell, str):
            builder.add_join('atomic_subshell_notation', 'atomic_subshell_id', table, column)
            builder.add_where('atomic_subshell_notation', 'ascii', 'atomic_subshell',
                              'atomic_subshell_notation', 'utf16', 'atomic_subshell')
            return {'atomic_subshell': atomic_subshell}

        elif n > 0 and l >= 0 and j_n > 0:
            builder.add_where('atomic_shell', 'principal_quantum_number', 'n')
            builder.add_where('atomic_subshell', 'azimuthal_quantum_number', 'l')
            builder.add_where('atomic_subshell', 'total_angular_momentum_nominator', 'j_n')
            return {'n': n, 'l': l, 'j_n': j_n}

        else:
            raise NotFound('Cannot parse atomic subshell: {}'.format(atomic_subshell))

    def _append_transition(self, builder, table, column, transition):
        src_n = 0; src_l = -1; src_j_n = 0
        dst_n = 0; dst_l = -1; dst_j_n = 0

        if hasattr(transition, 'source_subshell') and \
                hasattr(transition, 'destination_subshell'):
            src_n, src_l, src_j_n = \
                self._expand_atomic_subshell(transition.source_subshell)
            dst_n, dst_l, dst_j_n = \
                self._expand_atomic_subshell(transition.destination_subshell)

        elif isinstance(transition, collections.Sequence) and \
                len(transition) >= 2:
            src_n, src_l, src_j_n = self._expand_atomic_subshell(transition[0])
            dst_n, dst_l, dst_j_n = self._expand_atomic_subshell(transition[1])

        builder.add_join('transition', 'id', table, column)
        builder.add_join('atomic_subshell', 'id', 'transition', 'source_subshell_id', 'srcsubshell')
        builder.add_join('atomic_subshell', 'id', 'transition', 'destination_subshell_id', 'dstsubshell')
        builder.add_join('atomic_shell', 'id', 'srcsubshell', 'atomic_shell_id', 'srcshell')
        builder.add_join('atomic_shell', 'id', 'dstsubshell', 'atomic_shell_id', 'dstshell')

        if isinstance(transition, str):
            builder.add_join('transition_notation', 'transition_id', table, column)
            builder.add_where('transition_notation', 'ascii', 'transition',
                              'transition_notation', 'utf16', 'transition')
            return {'transition': transition}

        elif src_n > 0 and src_l >= 0 and src_j_n > 0 and \
                dst_n > 0 and dst_l >= 0 and dst_j_n > 0:
            builder.add_where('srcshell', 'principal_quantum_number', 'src_n')
            builder.add_where('srcsubshell', 'azimuthal_quantum_number', 'src_l')
            builder.add_where('srcsubshell', 'total_angular_momentum_nominator', 'src_j_n')
            builder.add_where('dstshell', 'principal_quantum_number', 'dst_n')
            builder.add_where('dstsubshell', 'azimuthal_quantum_number', 'dst_l')
            builder.add_where('dstsubshell', 'total_angular_momentum_nominator', 'dst_j_n')

            return {'src_n': src_n, 'src_l': src_l, 'src_j_n': src_j_n,
                    'dst_n': dst_n, 'dst_l': dst_l, 'dst_j_n': dst_j_n}

        else:
            raise NotFound('Cannot parse transition: {}'.format(transition))

    def _append_language(self, builder, table, language):
        if isinstance(language, descriptor.Language):
            language = language.code

        builder.add_join('language', 'id', table, 'language_id')
        builder.add_where('language', 'code', 'language')

        return {'language': language}

    def _append_notation(self, builder, table, notation):
        if isinstance(notation, descriptor.Notation):
            notation = notation.name

        builder.add_join('notation', 'id', table, 'notation_id')
        builder.add_where('notation', 'name', 'notation')

        return {'notation': notation}

    def _append_reference(self, builder, table, reference):
        if isinstance(reference, descriptor.Reference):
            reference = reference.bibtexkey

        if reference:
            builder.add_join('ref', 'id', table, 'reference_id')
            builder.add_where('ref', 'bibtexkey', 'reference')

        else:
            builder.add_orderby(table, 'reference_id')

        return {'reference': reference}

    def element(self, element):
        table = 'element'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'atomic_number')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'id', element))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No element found')

        atomic_number, = row
        return descriptor.Element(atomic_number)

    def element_atomic_number(self, element):
        table = 'element'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'atomic_number')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'id', element))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic number found')

        atomic_number, = row
        return atomic_number

    def element_symbol(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('element_symbol')

        table = 'element_symbol'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'symbol')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No symbol found')

        symbol, = row
        return symbol

    def element_name(self, element, language='en', reference=None):
        if not reference:
            reference = self.get_default_reference('element_name')

        table = 'element_name'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'name')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_language(builder, table, language))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No name found')

        name, = row
        return name

    def element_atomic_weight(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('element_atomic_weight')

        table = 'element_atomic_weight'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic weight found')

        value, = row
        return value

    def element_mass_density_kg_per_m3(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('element_mass_density_kg_per_m3')

        table = 'element_mass_density'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_kg_per_m3')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No mass density found')

        value_kg_per_m3, = row
        return value_kg_per_m3

#    def element_transitions(self, element, reference=None):
#        if not reference:
#            reference = self.get_default_reference('transition_probability')
#
#        element_id = self._get_element_id(self.engine, element)
#
#        tbl = table.transition_probability
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.transition_id])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.value > 0.0)
#        command = self._append_command_reference(command, tbl, reference)
#        result = self.engine.execute(command)
#        rows = result.fetchall()
#        if not rows:
#            raise NotFound('No transition found')
#
#        return tuple(self._get_transition(self.engine, row[0]) for row in rows)
#
    def atomic_shell(self, atomic_shell):
        table = 'atomic_shell'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'principal_quantum_number')
        builder.add_from(table)
        params.update(self._append_atomic_shell(builder, table, 'id', atomic_shell))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No mass density found')

        principal_quantum_number, = row
        return descriptor.AtomicShell(principal_quantum_number)

    def atomic_shell_notation(self, atomic_shell, notation,
                              encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_shell_notation')

        table = 'atomic_shell_notation'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        params.update(self._append_atomic_shell(builder, table, 'atomic_shell_id', atomic_shell))
        params.update(self._append_notation(builder, table, notation))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic shell notation found')

        value, = row
        return value

    def atomic_subshell(self, atomic_subshell):
        table = 'atomic_subshell'
        params = {}
        builder = SelectBuilder()
        builder.add_select('atomic_shell', 'principal_quantum_number')
        builder.add_select(table, 'azimuthal_quantum_number')
        builder.add_select(table, 'total_angular_momentum_nominator')
        builder.add_from(table)
        params.update(self._append_atomic_subshell(builder, table, 'id', atomic_subshell))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell found')

        n, l, j_n = row
        return descriptor.AtomicSubshell(n, l, j_n)

    def atomic_subshell_notation(self, atomic_subshell, notation,
                                 encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_notation')

        table = 'atomic_subshell_notation'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        params.update(self._append_atomic_shell(builder, table, 'atomic_subshell_id', atomic_subshell))
        params.update(self._append_notation(builder, table, notation))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell notation found')

        value, = row
        return value

#    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
#        if not reference:
#            reference = self.get_default_reference('atomic_subshell_binding_energy_eV')
#
#        element_id = self._get_element_id(self.engine, element)
#        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)
#
#        tbl = table.atomic_subshell_binding_energy
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value_eV])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No atomic subshell binding energy found'))
#
#    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
#        if not reference:
#            reference = self.get_default_reference('atomic_subshell_radiative_width_eV')
#
#        element_id = self._get_element_id(self.engine, element)
#        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)
#
#        tbl = table.atomic_subshell_radiative_width
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value_eV])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No atomic subshell radiative width found'))
#
#    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
#        if not reference:
#            reference = self.get_default_reference('atomic_subshell_nonradiative_width_eV')
#
#        element_id = self._get_element_id(self.engine, element)
#        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)
#
#        tbl = table.atomic_subshell_nonradiative_width
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value_eV])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No atomic subshell nonradiative width found'))
#
#    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
#        if not reference:
#            reference = self.get_default_reference('atomic_subshell_occupancy')
#
#        element_id = self._get_element_id(self.engine, element)
#        atomic_subshell_id = self._get_atomic_subshell_id(self.engine, atomic_subshell)
#
#        tbl = table.atomic_subshell_occupancy
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.atomic_subshell_id == atomic_subshell_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No atomic subshell occupancy found'))
#
    def transition(self, transition):
        table = 'transition'
        params = {}
        builder = SelectBuilder()
        builder.add_select('srcshell', 'principal_quantum_number')
        builder.add_select('srcsubshell', 'azimuthal_quantum_number')
        builder.add_select('srcsubshell', 'total_angular_momentum_nominator')
        builder.add_select('dstshell', 'principal_quantum_number')
        builder.add_select('dstsubshell', 'azimuthal_quantum_number')
        builder.add_select('dstsubshell', 'total_angular_momentum_nominator')
        builder.add_from(table)
        params.update(self._append_transition(builder, table, 'id', transition))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No transition found')

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = row
        src = descriptor.AtomicSubshell(src_n, src_l, src_j_n)
        dst = descriptor.AtomicSubshell(dst_n, dst_l, dst_j_n)
        return descriptor.Transition(src, dst)

    def transition_notation(self, transition, notation,
                            encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('transition_notation')

        table = 'transition_notation'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        params.update(self._append_transition(builder, table, 'transition_id', transition))
        params.update(self._append_notation(builder, table, notation))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No transition notation found')

        value, = row
        return value

    def transition_energy_eV(self, element, transition, reference=None):
        if not reference:
            reference = self.get_default_reference('transition_energy_eV')

        table = 'transition_energy'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_transition(builder, table, 'transition_id', transition))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No transition energy found')

        value_eV, = row
        return value_eV

#    def transition_probability(self, element, transition, reference=None):
#        if not reference:
#            reference = self.get_default_reference('transition_probability')
#
#        element_id = self._get_element_id(self.engine, element)
#        transition_id = self._get_transition_id(self.engine, transition)
#
#        tbl = table.transition_probability
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.transition_id == transition_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No transition probability found'))
#
#    def transition_relative_weight(self, element, transition, reference=None):
#        if not reference:
#            reference = self.get_default_reference('transition_relative_weight')
#
#        element_id = self._get_element_id(self.engine, element)
#        transition_id = self._get_transition_id(self.engine, transition)
#
#        tbl = table.transition_relative_weight
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.transition_id == transition_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No transition relative weight found'))
#
#    def transitionset(self, transitionset):
#        if isinstance(transitionset, descriptor.TransitionSet):
#            return transitionset
#        transitionset_id = self._get_transitionset_id(self.engine, transitionset)
#        return self._get_transitionset(self.engine, transitionset_id)
#
#    def transitionset_notation(self, transitionset, notation,
#                            encoding='utf16', reference=None):
#        if not reference:
#            reference = self.get_default_reference('transitionset_notation')
#
#        transitionset_id = self._get_transitionset_id(self.engine, transitionset)
#        notation_id = self._get_notation_id(self.engine, notation)
#
#        tbl = table.transitionset_notation
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([getattr(tbl.c, encoding)])
#        command = command.where(tbl.c.transitionset_id == transitionset_id)
#        command = command.where(tbl.c.notation_id == notation_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No transition set notation found'))
#
#    def transitionset_energy_eV(self, element, transitionset, reference=None):
#        if not reference:
#            reference = self.get_default_reference('transitionset_energy_eV')
#
#        element_id = self._get_element_id(self.engine, element)
#        transitionset_id = self._get_transitionset_id(self.engine, transitionset)
#
#        tbl = table.transitionset_energy
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value_eV])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.transitionset_id == transitionset_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No transition set energy found'))
#
#    def transitionset_relative_weight(self, element, transitionset, reference=None):
#        if not reference:
#            reference = self.get_default_reference('transitionset_relative_weight')
#
#        element_id = self._get_element_id(self.engine, element)
#        transitionset_id = self._get_transitionset_id(self.engine, transitionset)
#
#        tbl = table.transitionset_relative_weight
#        tbl.create(self.engine, checkfirst=True)
#        command = sql.select([tbl.c.value])
#        command = command.where(tbl.c.element_id == element_id)
#        command = command.where(tbl.c.transitionset_id == transitionset_id)
#        command = self._append_command_reference(command, tbl, reference)
#        return self._retrieve_first(self.engine, command,
#                                    NotFound('No transition set relative weight found'))
