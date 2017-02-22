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
            builder.add_where('element_name', 'name', '=', 'element',
                              'element_symbol', 'symbol', '=', 'element')

        elif isinstance(element, int):
            builder.add_join('element', 'id', table, column)
            builder.add_where('element', 'atomic_number', '=', 'element')

        else:
            raise NotFound('Cannot parse element: {}'.format(element))

        return {'element': element}

    def _append_atomic_shell(self, builder, table, column, atomic_shell):
        if hasattr(atomic_shell, 'principal_quantum_number'):
            atomic_shell = atomic_shell.principal_quantum_number

        if isinstance(atomic_shell, str):
            builder.add_join('atomic_shell_notation', 'atomic_shell_id', table, column)
            builder.add_where('atomic_shell_notation', 'ascii', '=', 'atomic_shell',
                              'atomic_shell_notation', 'utf16', '=', 'atomic_shell')

        elif isinstance(atomic_shell, int):
            builder.add_join('atomic_shell', 'id', table, column)
            builder.add_where('atomic_shell', 'principal_quantum_number', '=', 'atomic_shell')

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
            builder.add_where('atomic_subshell_notation', 'ascii', '=', 'atomic_subshell',
                              'atomic_subshell_notation', 'utf16', '=', 'atomic_subshell')
            return {'atomic_subshell': atomic_subshell}

        elif n > 0 and l >= 0 and j_n > 0:
            builder.add_where('atomic_shell', 'principal_quantum_number', '=', 'n')
            builder.add_where('atomic_subshell', 'azimuthal_quantum_number', '=', 'l')
            builder.add_where('atomic_subshell', 'total_angular_momentum_nominator', '=', 'j_n')
            return {'n': n, 'l': l, 'j_n': j_n}

        else:
            raise NotFound('Cannot parse atomic subshell: {}'.format(atomic_subshell))

    def _append_xray_transition(self, builder, table, column, xraytransition):
        src_n = 0; src_l = -1; src_j_n = 0
        dst_n = 0; dst_l = -1; dst_j_n = 0

        if hasattr(xraytransition, 'source_subshell') and \
                hasattr(xraytransition, 'destination_subshell'):
            src_n, src_l, src_j_n = \
                self._expand_atomic_subshell(xraytransition.source_subshell)
            dst_n, dst_l, dst_j_n = \
                self._expand_atomic_subshell(xraytransition.destination_subshell)

        elif isinstance(xraytransition, collections.Sequence) and \
                len(xraytransition) >= 2:
            src_n, src_l, src_j_n = self._expand_atomic_subshell(xraytransition[0])
            dst_n, dst_l, dst_j_n = self._expand_atomic_subshell(xraytransition[1])

        builder.add_join('xray_transition', 'id', table, column)
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'source_subshell_id', 'srcsubshell')
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'destination_subshell_id', 'dstsubshell')
        builder.add_join('atomic_shell', 'id', 'srcsubshell', 'atomic_shell_id', 'srcshell')
        builder.add_join('atomic_shell', 'id', 'dstsubshell', 'atomic_shell_id', 'dstshell')

        if isinstance(xraytransition, str):
            builder.add_join('xray_transition_notation', 'xray_transition_id', table, column)
            builder.add_where('xray_transition_notation', 'ascii', '=', 'xraytransition',
                              'xray_transition_notation', 'utf16', '=', 'xraytransition')
            return {'xraytransition': xraytransition}

        elif src_n > 0 and src_l >= 0 and src_j_n > 0 and \
                dst_n > 0 and dst_l >= 0 and dst_j_n > 0:
            builder.add_where('srcshell', 'principal_quantum_number', '=', 'src_n')
            builder.add_where('srcsubshell', 'azimuthal_quantum_number', '=', 'src_l')
            builder.add_where('srcsubshell', 'total_angular_momentum_nominator', '=', 'src_j_n')
            builder.add_where('dstshell', 'principal_quantum_number', '=', 'dst_n')
            builder.add_where('dstsubshell', 'azimuthal_quantum_number', '=', 'dst_l')
            builder.add_where('dstsubshell', 'total_angular_momentum_nominator', '=', 'dst_j_n')

            return {'src_n': src_n, 'src_l': src_l, 'src_j_n': src_j_n,
                    'dst_n': dst_n, 'dst_l': dst_l, 'dst_j_n': dst_j_n}

        else:
            raise NotFound('Cannot parse X-ray transition: {}'.format(xraytransition))

    def _append_xray_transitionset(self, builder, table, column, xraytransitionset):
        xraytransitions = set()
        if isinstance(xraytransitionset, descriptor.XrayTransitionSet):
            xraytransitions.update(xraytransitionset.transitions)

        elif isinstance(xraytransitionset, collections.Sequence):
            xraytransitions.update(xraytransitionset)

        if isinstance(xraytransitionset, str):
            builder.add_join('xray_transitionset_notation', 'xray_transitionset_id', table, column)
            builder.add_where('xray_transitionset_notation', 'ascii', '=', 'xraytransitionset',
                              'xray_transitionset_notation', 'utf16', '=', 'xraytransitionset')
            return {'xraytransitionset': xraytransitionset}

        elif xraytransitions:
            possibilities = set()
            for i, xraytransition in enumerate(xraytransitions):
                subtable = 'xray_transitionset_association'
                subparams = {}
                subbuilder = SelectBuilder()
                subbuilder.add_select(subtable, 'xray_transitionset_id')
                subbuilder.add_select('xray_transitionset', 'count')
                subbuilder.add_from(subtable)
                subbuilder.add_join('xray_transitionset', 'id', subtable, 'xray_transitionset_id')
                subparams.update(self._append_xray_transition(subbuilder, subtable, 'id', xraytransition))
                sql = subbuilder.build()

                cur = self.connection.cursor()
                cur.execute(sql, subparams)
                rows = cur.fetchall()
                cur.close()

                if i == 0:
                    possibilities.update(rows)
                else:
                    possibilities.intersection_update(rows)

                if not possibilities:
                    break

            for xray_transitionset_id, count in possibilities:
                if count == len(xraytransitions):
                    builder.add_join('xray_transitionset', 'id', table, column)
                    builder.add_where('xray_transitionset', 'id', '=', 'xray_transitionset_id')
                    return {'xray_transitionset_id': xray_transitionset_id}

        raise NotFound('Cannot parse X-ray transition set: {}'.format(xraytransitionset))

    def _append_language(self, builder, table, language):
        if isinstance(language, descriptor.Language):
            language = language.code

        builder.add_join('language', 'id', table, 'language_id')
        builder.add_where('language', 'code', '=', 'language')

        return {'language': language}

    def _append_notation(self, builder, table, notation):
        if isinstance(notation, descriptor.Notation):
            notation = notation.name

        builder.add_join('notation', 'id', table, 'notation_id')
        builder.add_where('notation', 'name', '=', 'notation')

        return {'notation': notation}

    def _append_reference(self, builder, table, reference):
        if isinstance(reference, descriptor.Reference):
            reference = reference.bibtexkey

        if reference:
            builder.add_join('ref', 'id', table, 'reference_id')
            builder.add_where('ref', 'bibtexkey', '=', 'reference')

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

    def element_xray_transitions(self, element, reference=None):
        if not reference:
            reference = self.get_default_reference('xray_transition_probability')

        table = 'xray_transition_probability'
        params = {}
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
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_reference(builder, table, reference))
        builder.add_where(table, 'value', '>', 'probability')
        params['probability'] = 0.0
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        if not rows:
            raise NotFound('No X-ray transition found')

        transitions = []
        for src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n in rows:
            src = descriptor.AtomicSubshell(src_n, src_l, src_j_n)
            dst = descriptor.AtomicSubshell(dst_n, dst_l, dst_j_n)
            transitions.append(descriptor.XrayTransition(src, dst))

        return tuple(transitions)

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

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        if not reference:
            reference = self.get_default_reference('atomic_subshell_binding_energy_eV')

        table = 'atomic_subshell_binding_energy'
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_atomic_shell(builder, table, 'atomic_subshell_id', atomic_subshell))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_atomic_shell(builder, table, 'atomic_subshell_id', atomic_subshell))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_atomic_shell(builder, table, 'atomic_subshell_id', atomic_subshell))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_atomic_shell(builder, table, 'atomic_subshell_id', atomic_subshell))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select('srcshell', 'principal_quantum_number')
        builder.add_select('srcsubshell', 'azimuthal_quantum_number')
        builder.add_select('srcsubshell', 'total_angular_momentum_nominator')
        builder.add_select('dstshell', 'principal_quantum_number')
        builder.add_select('dstsubshell', 'azimuthal_quantum_number')
        builder.add_select('dstsubshell', 'total_angular_momentum_nominator')
        builder.add_from(table)
        params.update(self._append_xray_transition(builder, table, 'id', xraytransition))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        params.update(self._append_xray_transition(builder, table, 'xray_transition_id', xraytransition))
        params.update(self._append_notation(builder, table, notation))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_xray_transition(builder, table, 'xray_transition_id', xraytransition))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_xray_transition(builder, table, 'xray_transition_id', xraytransition))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_xray_transition(builder, table, 'xray_transition_id', xraytransition))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
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
        params.update(self._append_xray_transitionset(builder, table, 'xray_transitionset_id', xraytransitionset))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, encoding)
        builder.add_from(table)
        params.update(self._append_xray_transitionset(builder, table, 'xray_transitionset_id', xraytransitionset))
        params.update(self._append_notation(builder, table, notation))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value_eV')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_xray_transitionset(builder, table, 'xray_transitionset_id', xraytransitionset))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

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
        params = {}
        builder = SelectBuilder()
        builder.add_select(table, 'value')
        builder.add_from(table)
        params.update(self._append_element(builder, table, 'element_id', element))
        params.update(self._append_xray_transitionset(builder, table, 'xray_transitionset_id', xraytransitionset))
        params.update(self._append_reference(builder, table, reference))
        sql = builder.build()

        cur = self.connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No X-ray transition set relative weight found')

        value, = row
        return value
