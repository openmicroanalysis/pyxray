""""""

# Standard library modules.
from collections.abc import Sequence

# Third party modules.

# Local modules.
from pyxray.base import NotFound
import pyxray.descriptor as descriptor
from pyxray.sql.command import SelectBuilder

# Globals and constants variables.

class SelectMixin:

    def _append_select_element(self, connection, builder, table, column, element):
        if hasattr(element, 'atomic_number'):
            element = element.atomic_number

        if isinstance(element, str):
            builder.add_join('element_name', 'element_id', table, column, 'en')
            builder.add_join('element_symbol', 'element_id', table, column, 'es')
            builder.add_where('en', 'name', '=', element,
                              'es', 'symbol', '=', element)

        elif isinstance(element, int):
            builder.add_join('element', 'id', table, column)
            builder.add_where('element', 'atomic_number', '=', element)

        else:
            raise NotFound('Cannot parse element: {}'.format(element))

    def _append_select_atomic_shell(self, connection, builder, table, column, atomic_shell):
        if hasattr(atomic_shell, 'principal_quantum_number'):
            atomic_shell = atomic_shell.principal_quantum_number

        if isinstance(atomic_shell, str):
            builder.add_join('atomic_shell_notation', 'atomic_shell_id', table, column, 'asn')
            builder.add_where('asn', 'ascii', '=', atomic_shell,
                              'asn', 'utf16', '=', atomic_shell)

        elif isinstance(atomic_shell, int):
            builder.add_join('atomic_shell', 'id', table, column)
            builder.add_where('atomic_shell', 'principal_quantum_number', '=', atomic_shell)

        else:
            raise NotFound('Cannot parse atomic shell: {}'.format(atomic_shell))

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

        elif isinstance(atomic_subshell, Sequence) and \
                len(atomic_subshell) == 3:
            n = atomic_subshell[0]
            l = atomic_subshell[1]
            j_n = atomic_subshell[2]

        return n, l, j_n

    def _append_select_atomic_subshell(self, connection, builder, table, column, atomic_subshell):
        n, l, j_n = self._expand_atomic_subshell(atomic_subshell)

        builder.add_join('atomic_subshell', 'id', table, column)
        builder.add_join('atomic_shell', 'id', 'atomic_subshell', 'atomic_shell_id')

        if isinstance(atomic_subshell, str):
            builder.add_join('atomic_subshell_notation', 'atomic_subshell_id', table, column, 'asn')
            builder.add_where('asn', 'ascii', '=', atomic_subshell,
                              'asn', 'utf16', '=', atomic_subshell)

        elif n > 0 and l >= 0 and j_n > 0:
            builder.add_where('atomic_shell', 'principal_quantum_number', '=', n)
            builder.add_where('atomic_subshell', 'azimuthal_quantum_number', '=', l)
            builder.add_where('atomic_subshell', 'total_angular_momentum_nominator', '=', j_n)

        else:
            raise NotFound('Cannot parse atomic subshell: {}'.format(atomic_subshell))

    def _append_select_xray_transition(self, connection, builder, table, column, xraytransition):
        src_n = 0; src_l = -1; src_j_n = 0
        dst_n = 0; dst_l = -1; dst_j_n = 0

        if hasattr(xraytransition, 'source_subshell') and \
                hasattr(xraytransition, 'destination_subshell'):
            src_n, src_l, src_j_n = \
                self._expand_atomic_subshell(xraytransition.source_subshell)
            dst_n, dst_l, dst_j_n = \
                self._expand_atomic_subshell(xraytransition.destination_subshell)

        elif isinstance(xraytransition, Sequence) and \
                len(xraytransition) >= 2:
            src_n, src_l, src_j_n = self._expand_atomic_subshell(xraytransition[0])
            dst_n, dst_l, dst_j_n = self._expand_atomic_subshell(xraytransition[1])

        builder.add_join('xray_transition', 'id', table, column)
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'source_subshell_id', 'srcsubshell')
        builder.add_join('atomic_subshell', 'id', 'xray_transition', 'destination_subshell_id', 'dstsubshell')
        builder.add_join('atomic_shell', 'id', 'srcsubshell', 'atomic_shell_id', 'srcshell')
        builder.add_join('atomic_shell', 'id', 'dstsubshell', 'atomic_shell_id', 'dstshell')

        if isinstance(xraytransition, str):
            builder.add_join('xray_transition_notation', 'xray_transition_id', table, column, 'xtn')
            builder.add_where('xtn', 'ascii', '=', xraytransition,
                              'xtn', 'utf16', '=', xraytransition)

        elif src_n > 0 and src_l >= 0 and src_j_n > 0 and \
                dst_n > 0 and dst_l >= 0 and dst_j_n > 0:
            builder.add_where('srcshell', 'principal_quantum_number', '=', src_n)
            builder.add_where('srcsubshell', 'azimuthal_quantum_number', '=', src_l)
            builder.add_where('srcsubshell', 'total_angular_momentum_nominator', '=', src_j_n)
            builder.add_where('dstshell', 'principal_quantum_number', '=', dst_n)
            builder.add_where('dstsubshell', 'azimuthal_quantum_number', '=', dst_l)
            builder.add_where('dstsubshell', 'total_angular_momentum_nominator', '=', dst_j_n)

        else:
            raise NotFound('Cannot parse X-ray transition: {}'.format(xraytransition))

    def _append_select_xray_transitionset(self, connection, builder, table, column, xraytransitionset):
        xraytransitions = set()
        if isinstance(xraytransitionset, descriptor.XrayTransitionSet):
            xraytransitions.update(xraytransitionset.possible_transitions)

        elif isinstance(xraytransitionset, Sequence):
            xraytransitions.update(xraytransitionset)

        if isinstance(xraytransitionset, str):
            builder.add_join('xray_transitionset_notation', 'xray_transitionset_id', table, column, 'xtn')
            builder.add_where('xtn', 'ascii', '=', xraytransitionset,
                              'xtn', 'utf16', '=', xraytransitionset)
            return

        elif xraytransitions:
            possibilities = set()
            for i, xraytransition in enumerate(xraytransitions):
                subtable = 'xray_transitionset_association'
                subbuilder = SelectBuilder()
                subbuilder.add_select(subtable, 'xray_transitionset_id')
                subbuilder.add_select('xray_transitionset', 'count')
                subbuilder.add_from(subtable)
                subbuilder.add_join('xray_transitionset', 'id', subtable, 'xray_transitionset_id')
                self._append_select_xray_transition(connection, subbuilder, subtable, 'xray_transition_id', xraytransition)
                sql, params = subbuilder.build()

                cur = connection.cursor()
                cur.execute(sql, params)
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
                    builder.add_where('xray_transitionset', 'id', '=', xray_transitionset_id)
                    return

        raise NotFound('Cannot parse X-ray transition set: {}'.format(xraytransitionset))

    def _append_select_language(self, connection, builder, table, language):
        if isinstance(language, descriptor.Language):
            language = language.code

        builder.add_join('language', 'id', table, 'language_id')
        builder.add_where('language', 'code', '=', language)

    def _append_select_notation(self, connection, builder, table, notation):
        if isinstance(notation, descriptor.Notation):
            notation = notation.name

        builder.add_join('notation', 'id', table, 'notation_id')
        builder.add_where('notation', 'name', '=', notation)

    def _append_select_reference(self, connection, builder, table, reference):
        if isinstance(reference, descriptor.Reference):
            reference = reference.bibtexkey

        if reference:
            builder.add_join('ref', 'id', table, 'reference_id')
            builder.add_where('ref', 'bibtexkey', '=', reference)

        else:
            builder.add_orderby(table, 'reference_id')

class TableMixin:

    def _append_table_primary_key_columns(self, builder):
        builder.add_primarykey_column('id')

    def _append_table_element_columns(self, builder):
        builder.add_foreignkey_column('element_id', 'element', 'id')

    def _append_table_atomic_shell_columns(self, builder):
        builder.add_foreignkey_column('atomic_shell_id', 'atomic_shell', 'id'),

    def _append_table_atomic_subshell_columns(self, builder):
        builder.add_foreignkey_column('atomic_subshell_id', 'atomic_subshell', 'id')

    def _append_table_xray_transition_columns(self, builder):
        builder.add_foreignkey_column('xray_transition_id', 'xray_transition', 'id')

    def _append_table_xray_transitionset_columns(self, builder):
        builder.add_foreignkey_column('xray_transitionset_id', 'xray_transitionset', 'id')

    def _append_table_language_columns(self, builder):
        builder.add_foreignkey_column('language_id', 'language', 'id')

    def _append_table_notation_columns(self, builder):
        builder.add_foreignkey_column('notation_id', 'notation', 'id')

    def _append_table_notation_property_columns(self, builder):
        builder.add_string_column('ascii', 100, nullable=False)
        builder.add_string_column('utf16', 100)
        builder.add_string_column('html', 100)
        builder.add_string_column('latex', 100)

    def _append_table_reference_columns(self, builder):
        builder.add_foreignkey_column('reference_id', 'ref', 'id')

    def _append_table_energy_property_columns(self, builder):
        builder.add_float_column('value_eV', nullable=False)

    def _append_table_value_property_columns(self, builder):
        builder.add_float_column('value', nullable=False)

class InsertMixin:

    def _append_insert_property_element_columns(self, connection, builder, prop):
        element_id = self._require_element(connection, prop.element)
        builder.add_column('element_id', element_id)

    def _append_insert_property_atomic_shell_columns(self, connection, builder, prop):
        atomic_shell_id = self._require_atomic_shell(connection, prop.atomic_shell)
        builder.add_column('atomic_shell_id', atomic_shell_id)

    def _append_insert_property_atomic_subshell_columns(self, connection, builder, prop):
        atomic_subshell_id = self._require_atomic_subshell(connection, prop.atomic_subshell)
        builder.add_column('atomic_subshell_id', atomic_subshell_id)

    def _append_insert_property_xray_transition_columns(self, connection, builder, prop):
        xray_transition_id = self._require_xray_transition(connection, prop.xraytransition)
        builder.add_column('xray_transition_id', xray_transition_id)

    def _append_insert_property_xray_transitionset_columns(self, connection, builder, prop):
        xray_transitionset_id = self._require_xray_transitionset(connection, prop.xraytransitionset)
        builder.add_column('xray_transitionset_id', xray_transitionset_id)

    def _append_insert_property_reference_columns(self, connection, builder, prop):
        reference_id = self._require_reference(connection, prop.reference)
        builder.add_column('reference_id', reference_id)

    def _append_insert_property_language_columns(self, connection, builder, prop):
        language_id = self._require_language(connection, prop.language)
        builder.add_column('language_id', language_id)

    def _append_insert_property_notation_columns(self, connection, builder, prop):
        notation_id = self._require_notation(connection, prop.notation)
        builder.add_column('notation_id', notation_id)

        builder.add_column('ascii', prop.ascii)
        builder.add_column('utf16', prop.utf16)
        builder.add_column('html', prop.html)
        builder.add_column('latex', prop.latex)

    def _append_insert_property_energy_columns(self, connection, builder, prop):
        builder.add_column('value_eV', prop.value_eV)
