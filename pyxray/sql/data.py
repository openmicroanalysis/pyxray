""""""

# Standard library modules.
from collections.abc import Sequence
import logging

# Third party modules.
import sqlalchemy.sql

# Local modules.
from pyxray.base import _DatabaseMixin, NotFound
from pyxray.sql.base import SqlBase
import pyxray.descriptor as descriptor
import pyxray.property as property

# Globals and constants variables.
logger = logging.getLogger(__name__)

class SqlDatabase(_DatabaseMixin, SqlBase):

    def _expand_atomic_subshell(self, atomic_subshell):
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
        else:
            n = l = j_n = None

        return n, l, j_n

    def _expand_xray_transition(self, xray_transition):
        if isinstance(xray_transition, descriptor.XrayTransition):
            src_n = xray_transition.source_principal_quantum_number
            src_l = xray_transition.source_azimuthal_quantum_number
            src_j_n = xray_transition.source_total_angular_momentum_nominator
            dst_n = xray_transition.destination_principal_quantum_number
            dst_l = xray_transition.destination_azimuthal_quantum_number
            dst_j_n = xray_transition.destination_total_angular_momentum_nominator

        elif isinstance(xray_transition, Sequence) and \
                len(xray_transition) >= 2:
            src_n, src_l, src_j_n = self._expand_atomic_subshell(xray_transition[0])
            dst_n, dst_l, dst_j_n = self._expand_atomic_subshell(xray_transition[1])

        else:
            raise NotFound('Cannot parse X-ray transition: {}'.format(xray_transition))

        return src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n

    def _create_element_clauses(self, table, element, column='element_id'):
        if hasattr(element, 'atomic_number'):
            element = element.atomic_number

        if isinstance(element, str):
            table_name = self.require_table(property.ElementName)
            clause_name = (table.c[column] == table_name.c['element_id']) & \
                (table_name.c['value'] == element)

            table_symbol = self.require_table(property.ElementSymbol)
            clause_symbol = (table.c[column] == table_symbol.c['element_id']) & \
                (table_symbol.c['value'] == element)

            return [sqlalchemy.sql.or_(clause_name, clause_symbol)]

        if isinstance(element, int):
            table_element = self.require_table(descriptor.Element)
            return [table.c[column] == table_element.c['id'],
                    table_element.c['atomic_number'] == element]

        raise NotFound('Cannot parse element: {}'.format(element))

    def _create_atomic_shell_clauses(self, table, atomic_shell, column='atomic_shell_id'):
        if hasattr(atomic_shell, 'principal_quantum_number'):
            atomic_shell = atomic_shell.principal_quantum_number

        if isinstance(atomic_shell, str):
            table_notation = self.require_table(property.AtomicShellNotation)
            return [table.c[column] == table_notation.c['atomic_shell_id'],
                    sqlalchemy.sql.or_(table_notation.c['ascii'] == atomic_shell,
                                       table_notation.c['utf16'] == atomic_shell)]

        if isinstance(atomic_shell, int):
            table_atomic_shell = self.require_table(descriptor.AtomicShell)
            return [table.c[column] == table_atomic_shell.c['id'],
                    table_atomic_shell.c['principal_quantum_number'] == atomic_shell]

        raise NotFound('Cannot parse atomic shell: {}'.format(atomic_shell))

    def _create_atomic_subshell_clauses(self, table, atomic_subshell, column='atomic_subshell_id'):
        if isinstance(atomic_subshell, str):
            table_notation = self.require_table(property.AtomicSubshellNotation)
            return [table.c[column] == table_notation.c['atomic_subshell_id'],
                    sqlalchemy.sql.or_(table_notation.c['ascii'] == atomic_subshell,
                                       table_notation.c['utf16'] == atomic_subshell)]

        n, l, j_n = self._expand_atomic_subshell(atomic_subshell)
        if n is not None:
            table_atomic_subshell = self.require_table(descriptor.AtomicSubshell)
            return [table.c[column] == table_atomic_subshell.c['id'],
                    table_atomic_subshell.c['principal_quantum_number'] == n,
                    table_atomic_subshell.c['azimuthal_quantum_number'] == l,
                    table_atomic_subshell.c['total_angular_momentum_nominator'] == j_n]

        raise NotFound('Cannot parse atomic subshell: {}'.format(atomic_subshell))

    def _create_xray_transition_clauses(self, table, xray_transition, column='xray_transition_id', search=False):
        if isinstance(xray_transition, str):
            table_notation = self.require_table(property.XrayTransitionNotation)
            return [table.c[column] == table_notation.c['xray_transition_id'],
                    sqlalchemy.sql.or_(table_notation.c['ascii'] == xray_transition,
                                       table_notation.c['utf16'] == xray_transition)]

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = self._expand_xray_transition(xray_transition)

        table_xray_transition = self.require_table(descriptor.XrayTransition)

        if search:
            def create_clause(column, value):
                if value is not None:
                    return table_xray_transition.c[column] == value
                else:
                    return table_xray_transition.c[column] != None

            return [table.c[column] == table_xray_transition.c['id'],
                    create_clause('source_principal_quantum_number', src_n),
                    create_clause('source_azimuthal_quantum_number', src_l),
                    create_clause('source_total_angular_momentum_nominator', src_j_n),
                    create_clause('destination_principal_quantum_number', dst_n),
                    create_clause('destination_azimuthal_quantum_number', dst_l),
                    create_clause('destination_total_angular_momentum_nominator', dst_j_n)]

        else:
            return [table.c[column] == table_xray_transition.c['id'],
                    table_xray_transition.c['source_principal_quantum_number'] == src_n,
                    table_xray_transition.c['source_azimuthal_quantum_number'] == src_l,
                    table_xray_transition.c['source_total_angular_momentum_nominator'] == src_j_n,
                    table_xray_transition.c['destination_principal_quantum_number'] == dst_n,
                    table_xray_transition.c['destination_azimuthal_quantum_number'] == dst_l,
                    table_xray_transition.c['destination_total_angular_momentum_nominator'] == dst_j_n]

    def _create_reference_clauses(self, table, reference):
        if isinstance(reference, descriptor.Reference):
            reference = reference.bibtexkey

        if reference:
            table_reference = self.require_table(descriptor.Reference)
            return [table.c['reference_id'] == table_reference.c['id'],
                    table_reference.c['bibtexkey'] == reference]
        else:
            return []

    def _create_notation_clauses(self, table, notation):
        if isinstance(notation, descriptor.Notation):
            notation = notation.key

        table_notation = self.require_table(descriptor.Notation)
        return [table.c['notation_id'] == table_notation.c['id'],
                table_notation.c['key'] == notation]

    def _create_language_clauses(self, table, language):
        if isinstance(language, descriptor.Language):
            language = language.key

        table_language = self.require_table(descriptor.Language)
        return [table.c['language_id'] == table_language.c['id'],
                table_language.c['key'] == language]

    def _execute_select_one(self, statement):
        logger.debug(statement.compile())

        with self.engine.connect() as conn:
            row = conn.execute(statement).fetchone()
            if row is None:
                raise NotFound

            if len(row) == 1:
                return row[0]
            else:
                return row

    def _execute_select_many(self, statement):
        logger.debug(statement.compile())

        with self.engine.connect() as conn:
            rows = conn.execute(statement).fetchall()
            if not rows:
                raise NotFound
            return rows

    def element(self, element):
        table = self.require_table(descriptor.Element)

        clauses = []
        clauses += self._create_element_clauses(table, element, 'id')

        statement = sqlalchemy.sql.select([table.c['atomic_number']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        atomic_number = self._execute_select_one(statement)
        return descriptor.Element(atomic_number)

    def element_atomic_number(self, element):
        table = self.require_table(descriptor.Element)

        clauses = []
        clauses += self._create_element_clauses(table, element, 'id')

        statement = sqlalchemy.sql.select([table.c['atomic_number']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def element_symbol(self, element, reference=None):
        table = self.require_table(property.ElementSymbol)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def element_name(self, element, language='en', reference=None):
        table = self.require_table(property.ElementName)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_language_clauses(table, language)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def element_atomic_weight(self, element, reference=None):
        table = self.require_table(property.ElementAtomicWeight)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def element_mass_density_kg_per_m3(self, element, reference=None):
        table = self.require_table(property.ElementMassDensity)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value_kg_per_m3']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def element_xray_transitions(self, element, xray_transition=None, reference=None):
        table_xray = self.require_table(descriptor.XrayTransition)
        table_probability = self.require_table(property.XrayTransitionProbability)

        clauses = []
        clauses += self._create_element_clauses(table_probability, element)
        clauses += self._create_reference_clauses(table_probability, reference)
        if xray_transition is not None:
            clauses += self._create_xray_transition_clauses(table_probability, xray_transition, search=True)
        clauses += [table_probability.c['xray_transition_id'] == table_xray.c['id'],
                    table_probability.c['value'] > 0.0]

        statement = sqlalchemy.sql.select([table_xray.c['source_principal_quantum_number'],
                                           table_xray.c['source_azimuthal_quantum_number'],
                                           table_xray.c['source_total_angular_momentum_nominator'],
                                           table_xray.c['destination_principal_quantum_number'],
                                           table_xray.c['destination_azimuthal_quantum_number'],
                                           table_xray.c['destination_total_angular_momentum_nominator']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        transitions = []
        for src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n in self._execute_select_many(statement):
            transition = descriptor.XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n)
            transitions.append(transition)

        return tuple(transitions)

    def element_xray_transition(self, element, xray_transition, reference=None):
        table_xray = self.require_table(descriptor.XrayTransition)
        table_probability = self.require_table(property.XrayTransitionProbability)

        clauses = []
        clauses += self._create_xray_transition_clauses(table_xray, xray_transition, 'id')
        clauses += self._create_element_clauses(table_probability, element)
        clauses += self._create_reference_clauses(table_probability, reference)
        clauses += [table_probability.c['xray_transition_id'] == table_xray.c['id'],
                    table_probability.c['value'] > 0.0]

        statement = sqlalchemy.sql.select([table_xray.c['source_principal_quantum_number'],
                                           table_xray.c['source_azimuthal_quantum_number'],
                                           table_xray.c['source_total_angular_momentum_nominator'],
                                           table_xray.c['destination_principal_quantum_number'],
                                           table_xray.c['destination_azimuthal_quantum_number'],
                                           table_xray.c['destination_total_angular_momentum_nominator']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = self._execute_select_one(statement)
        return descriptor.XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n)

    def atomic_shell(self, atomic_shell):
        table = self.require_table(descriptor.AtomicShell)

        clauses = []
        clauses += self._create_atomic_shell_clauses(table, atomic_shell, 'id')

        statement = sqlalchemy.sql.select([table.c['principal_quantum_number']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        principal_quantum_number = self._execute_select_one(statement)
        return descriptor.AtomicShell(principal_quantum_number)

    def atomic_shell_notation(self, atomic_shell, notation, encoding='utf16', reference=None):
        table = self.require_table(property.AtomicShellNotation)

        clauses = []
        clauses += self._create_atomic_shell_clauses(table, atomic_shell)
        clauses += self._create_notation_clauses(table, notation)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c[encoding]])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def atomic_subshell(self, atomic_subshell):
        table = self.require_table(descriptor.AtomicSubshell)

        clauses = []
        clauses += self._create_atomic_subshell_clauses(table, atomic_subshell, 'id')

        statement = sqlalchemy.sql.select([table.c['principal_quantum_number'],
                                           table.c['azimuthal_quantum_number'],
                                           table.c['total_angular_momentum_nominator']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        n, l, j_n = self._execute_select_one(statement)
        return descriptor.AtomicSubshell(n, l, j_n)

    def atomic_subshell_notation(self, atomic_subshell, notation, encoding='utf16', reference=None):
        table = self.require_table(property.AtomicSubshellNotation)

        clauses = []
        clauses += self._create_atomic_subshell_clauses(table, atomic_subshell)
        clauses += self._create_notation_clauses(table, notation)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c[encoding]])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellBindingEnergy)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_atomic_subshell_clauses(table, atomic_subshell)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value_eV']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellRadiativeWidth)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_atomic_subshell_clauses(table, atomic_subshell)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value_eV']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellNonRadiativeWidth)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_atomic_subshell_clauses(table, atomic_subshell)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value_eV']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellOccupancy)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_atomic_subshell_clauses(table, atomic_subshell)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def xray_transition(self, xray_transition):
        table = self.require_table(descriptor.XrayTransition)

        clauses = []
        clauses += self._create_xray_transition_clauses(table, xray_transition, 'id')

        statement = sqlalchemy.sql.select([table.c['source_principal_quantum_number'],
                                           table.c['source_azimuthal_quantum_number'],
                                           table.c['source_total_angular_momentum_nominator'],
                                           table.c['destination_principal_quantum_number'],
                                           table.c['destination_azimuthal_quantum_number'],
                                           table.c['destination_total_angular_momentum_nominator']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = self._execute_select_one(statement)
        return descriptor.XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n)

    def xray_transition_notation(self, xray_transition, notation, encoding='utf16', reference=None):
        table = self.require_table(property.XrayTransitionNotation)

        clauses = []
        clauses += self._create_xray_transition_clauses(table, xray_transition)
        clauses += self._create_notation_clauses(table, notation)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c[encoding]])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def xray_transition_energy_eV(self, element, xray_transition, reference=None):
        table = self.require_table(property.XrayTransitionEnergy)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_xray_transition_clauses(table, xray_transition)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value_eV']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def xray_transition_probability(self, element, xray_transition, reference=None):
        table = self.require_table(property.XrayTransitionProbability)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_xray_transition_clauses(table, xray_transition)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)

    def xray_transition_relative_weight(self, element, xray_transition, reference=None):
        table = self.require_table(property.XrayTransitionRelativeWeight)

        clauses = []
        clauses += self._create_element_clauses(table, element)
        clauses += self._create_xray_transition_clauses(table, xray_transition)
        clauses += self._create_reference_clauses(table, reference)

        statement = sqlalchemy.sql.select([table.c['value']])
        statement = statement.where(sqlalchemy.sql.and_(*clauses))

        return self._execute_select_one(statement)
