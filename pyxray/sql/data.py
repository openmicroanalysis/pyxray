"""
Implementation of the database using a SQL database
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.base import _Database, NotFound
import pyxray.descriptor as descriptor
from pyxray.sql.command import SelectBuilder
from pyxray.sql.base import SelectMixin

# Globals and constants variables.

class SqlDatabase(SelectMixin, _Database):

    def __init__(self, connection):
        super().__init__()
        self.connection = connection

    def element(self, element):
        table = 'element'
        builder = SelectBuilder()
        builder.add_select(table, 'atomic_number')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'id', element)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, 'atomic_number')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'id', element)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, 'symbol')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, 'name')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_language(self.connection, builder, table, language)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, 'value_kg_per_m3')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No mass density found')

        value_kg_per_m3, = row
        return value_kg_per_m3

    def element_xray_transitions(self, element, xraytransitionset=None, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_probability')

        table = 'xray_transition_probability'
        builder = SelectBuilder()
        builder.distinct = True
        builder.add_select('srcshell', 'principal_quantum_number')
        builder.add_select('srcsubshell', 'azimuthal_quantum_number')
        builder.add_select('srcsubshell', 'total_angular_momentum_nominator')
        builder.add_select('dstshell', 'principal_quantum_number')
        builder.add_select('dstsubshell', 'azimuthal_quantum_number')
        builder.add_select('dstsubshell', 'total_angular_momentum_nominator')
        builder.add_from(table)
        builder.add_join('xray_transition', 'id', table, 'xray_transition_id')
        builder.add_join('xray_transitionset_association', 'xray_transition_id', table, 'xray_transition_id')
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'source_subshell_id', 'srcsubshell')
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'destination_subshell_id', 'dstsubshell')
        builder.add_join('atomic_shell', 'id', 'srcsubshell', 'atomic_shell_id', 'srcshell')
        builder.add_join('atomic_shell', 'id', 'dstsubshell', 'atomic_shell_id', 'dstshell')
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_reference(self.connection, builder, table, reference)
        if xraytransitionset is not None:
            self._append_select_xray_transitionset(self.connection, builder, 'xray_transitionset_association', 'xray_transitionset_id', xraytransitionset)
        builder.add_where(table, 'value', '>', 0.0)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        if not rows:
            raise NotFound('No X-ray transition set found for element={!r} and xraytransitionset={!r}'
                           .format(element, xraytransitionset))

        transitions = []
        for src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n in rows:
            src = descriptor.AtomicSubshell(src_n, src_l, src_j_n)
            dst = descriptor.AtomicSubshell(dst_n, dst_l, dst_j_n)
            transitions.append(descriptor.XrayTransition(src, dst))

        return tuple(transitions)

    def element_xray_transition(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_probability')

        table = 'xray_transition_probability'
        builder = SelectBuilder()
        builder.add_select('srcshell', 'principal_quantum_number')
        builder.add_select('srcsubshell', 'azimuthal_quantum_number')
        builder.add_select('srcsubshell', 'total_angular_momentum_nominator')
        builder.add_select('dstshell', 'principal_quantum_number')
        builder.add_select('dstsubshell', 'azimuthal_quantum_number')
        builder.add_select('dstsubshell', 'total_angular_momentum_nominator')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_reference(self.connection, builder, table, reference)
        self._append_select_xray_transition(self.connection, builder, table, 'xray_transition_id', xraytransition)
        builder.add_where(table, 'value', '>', 0.0)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition found for element={!r} and xraytransition={!r}'
                           .format(element, xraytransition))

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = row
        src = descriptor.AtomicSubshell(src_n, src_l, src_j_n)
        dst = descriptor.AtomicSubshell(dst_n, dst_l, dst_j_n)
        return descriptor.XrayTransition(src, dst)

    def atomic_shell(self, atomic_shell):
        table = 'atomic_shell'
        builder = SelectBuilder()
        builder.add_select(table, 'principal_quantum_number')
        builder.add_from(table)
        self._append_select_atomic_shell(self.connection, builder, table, 'id', atomic_shell)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        self._append_select_atomic_shell(self.connection, builder, table, 'atomic_shell_id', atomic_shell)
        self._append_select_notation(self.connection, builder, table, notation)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select('atomic_shell', 'principal_quantum_number')
        builder.add_select(table, 'azimuthal_quantum_number')
        builder.add_select(table, 'total_angular_momentum_nominator')
        builder.add_from(table)
        self._append_select_atomic_subshell(self.connection, builder, table, 'id', atomic_subshell)
        sql, params = builder.build()

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
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        self._append_select_atomic_subshell(self.connection, builder, table, 'atomic_subshell_id', atomic_subshell)
        self._append_select_notation(self.connection, builder, table, notation)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell notation found')

        value, = row
        return value

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_binding_energy_eV')

        table = 'atomic_subshell_binding_energy'
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_atomic_subshell(self.connection, builder, table, 'atomic_subshell_id', atomic_subshell)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell binding energy found')

        value_eV, = row
        return value_eV

    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_radiative_width_eV')

        table = 'atomic_subshell_radiative_width'
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_atomic_subshell(self.connection, builder, table, 'atomic_subshell_id', atomic_subshell)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell radiative width found')

        value_eV, = row
        return value_eV

    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_nonradiative_width_eV')

        table = 'atomic_subshell_nonradiative_width'
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_atomic_subshell(self.connection, builder, table, 'atomic_subshell_id', atomic_subshell)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell nonradiative width found')

        value_eV, = row
        return value_eV

    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_occupancy')

        table = 'atomic_subshell_occupancy'
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_atomic_subshell(self.connection, builder, table, 'atomic_subshell_id', atomic_subshell)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No atomic subshell occupancy found')

        value, = row
        return value

    def xray_transition(self, xraytransition):
        table = 'xray_transition'
        builder = SelectBuilder()
        builder.add_select('srcshell', 'principal_quantum_number')
        builder.add_select('srcsubshell', 'azimuthal_quantum_number')
        builder.add_select('srcsubshell', 'total_angular_momentum_nominator')
        builder.add_select('dstshell', 'principal_quantum_number')
        builder.add_select('dstsubshell', 'azimuthal_quantum_number')
        builder.add_select('dstsubshell', 'total_angular_momentum_nominator')
        builder.add_from(table)
        self._append_select_xray_transition(self.connection, builder, table, 'id', xraytransition)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition found')

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = row
        src = descriptor.AtomicSubshell(src_n, src_l, src_j_n)
        dst = descriptor.AtomicSubshell(dst_n, dst_l, dst_j_n)
        return descriptor.XrayTransition(src, dst)

    def xray_transition_notation(self, xraytransition, notation,
                                 encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_notation')

        table = 'xray_transition_notation'
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        self._append_select_xray_transition(self.connection, builder, table, 'xray_transition_id', xraytransition)
        self._append_select_notation(self.connection, builder, table, notation)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition notation found')

        value, = row
        return value

    def xray_transition_energy_eV(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_energy_eV')

        table = 'xray_transition_energy'
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_xray_transition(self.connection, builder, table, 'xray_transition_id', xraytransition)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition energy found')

        value_eV, = row
        return value_eV

    def xray_transition_probability(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_probability')

        table = 'xray_transition_probability'
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_xray_transition(self.connection, builder, table, 'xray_transition_id', xraytransition)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition probability found')

        value, = row
        return value

    def xray_transition_relative_weight(self, element, xraytransition, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_relative_weight')

        table = 'xray_transition_relative_weight'
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_xray_transition(self.connection, builder, table, 'xray_transition_id', xraytransition)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition relative weight found')

        value, = row
        return value

    def xray_transitionset(self, xraytransitionset):
        table = 'xray_transitionset_association'
        builder = SelectBuilder()
        builder.add_select('srcshell', 'principal_quantum_number')
        builder.add_select('srcsubshell', 'azimuthal_quantum_number')
        builder.add_select('srcsubshell', 'total_angular_momentum_nominator')
        builder.add_select('dstshell', 'principal_quantum_number')
        builder.add_select('dstsubshell', 'azimuthal_quantum_number')
        builder.add_select('dstsubshell', 'total_angular_momentum_nominator')
        builder.add_from(table)
        builder.add_join('xray_transition', 'id', table, 'xray_transition_id')
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'source_subshell_id', 'srcsubshell')
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'destination_subshell_id', 'dstsubshell')
        builder.add_join('atomic_shell', 'id', 'srcsubshell', 'atomic_shell_id', 'srcshell')
        builder.add_join('atomic_shell', 'id', 'dstsubshell', 'atomic_shell_id', 'dstshell')
        self._append_select_xray_transitionset(self.connection, builder, table, 'xray_transitionset_id', xraytransitionset)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        if not rows:
            raise NotFound('No X-ray transition set found')

        transitions = []
        for src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n in rows:
            src = descriptor.AtomicSubshell(src_n, src_l, src_j_n)
            dst = descriptor.AtomicSubshell(dst_n, dst_l, dst_j_n)
            transitions.append(descriptor.XrayTransition(src, dst))

        return descriptor.XrayTransitionSet(transitions)

    def xray_transitionset_notation(self, xraytransitionset, notation,
                                    encoding='utf16', reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transitionset_notation')

        table = 'xray_transitionset_notation'
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        self._append_select_xray_transitionset(self.connection, builder, table, 'xray_transitionset_id', xraytransitionset)
        self._append_select_notation(self.connection, builder, table, notation)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition set notation found')

        value, = row
        return value

    def xray_transitionset_energy_eV(self, element, xraytransitionset, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transitionset_energy_eV')

        table = 'xray_transitionset_energy'
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_xray_transitionset(self.connection, builder, table, 'xray_transitionset_id', xraytransitionset)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition set energy found')

        value_eV, = row
        return value_eV

    def xray_transitionset_relative_weight(self, element, xraytransitionset, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transitionset_relative_weight')

        table = 'xray_transitionset_relative_weight'
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        self._append_select_element(self.connection, builder, table, 'element_id', element)
        self._append_select_xray_transitionset(self.connection, builder, table, 'xray_transitionset_id', xraytransitionset)
        self._append_select_reference(self.connection, builder, table, reference)
        sql, params = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition set relative weight found')

        value, = row
        return value

    def xray_line(self, element, line, reference=None):
        element = self.element(element)
        symbol = self.element_symbol(element)

        try:
            transitions = [self.element_xray_transition(element, line)]
            method_notation = self.xray_transition_notation
            method_energy = self.xray_transition_energy_eV

        except NotFound:
            transitions = self.element_xray_transitions(element, line)
            method_notation = self.xray_transitionset_notation
            method_energy = self.xray_transitionset_energy_eV

        iupac = '{} {}'.format(symbol, method_notation(line, 'iupac', 'utf16'))

        try:
            siegbahn = '{} {}'.format(symbol, method_notation(line, 'siegbahn', 'utf16'))
        except:
            siegbahn = iupac

        try:
            energy_eV = method_energy(element, line, reference)
        except NotFound:
            energy_eV = 0.0

        return descriptor.XrayLine(element, transitions, iupac, siegbahn, energy_eV)
