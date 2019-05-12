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

class StatementBuilder:

    def __init__(self):
        self._columns = []
        self._joins = {}
        self._clauses = []

    def add_column(self, column):
        self._columns.append(column)

    def add_join(self, left, right, onclause):
        if left == right:
            return
        self._joins[(left, right)] = onclause

    def add_clause(self, clause):
        self._clauses.append(clause)

    def build(self):
        statement = sqlalchemy.sql.select(self._columns)

        if self._joins:
            # Joins have to be nested to work with sqlalchemy
            # E.g.
            # j = table_a.join(
            #        table_b.join(table_c,
            #            table_b.c.id == table_c.c.b_id),
            #        table_b.c.a_id == table_a.c.id)
            joins = self._joins.copy()

            (left, right), onclause = joins.popitem()
            finaljoin = left.join(right, onclause)

            for (_left, right), onclause in joins.items():
                finaljoin = finaljoin.join(right, onclause)

            statement = statement.select_from(finaljoin)

        return statement.where(sqlalchemy.sql.and_(*self._clauses))

class SqlDatabase(_DatabaseMixin, SqlBase):

    def __init__(self, engine):
        super().__init__(engine)
        self._preferred_references = []

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
            raise NotFound('Cannot parse atomic subshell: {}'.format(atomic_subshell))

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

    def _update_element(self, builder, table, element, column='element_id'):
        if hasattr(element, 'atomic_number'):
            element = element.atomic_number

        if isinstance(element, str):
            table_name = self.require_table(property.ElementName)
            builder.add_join(table, table_name, table.c[column] == table_name.c['element_id'])
            clause_name = table_name.c['value'] == element

            table_symbol = self.require_table(property.ElementSymbol)
            builder.add_join(table, table_symbol, table.c[column] == table_symbol.c['element_id'])
            clause_symbol = table_symbol.c['value'] == element

            builder.add_clause(sqlalchemy.sql.or_(clause_name, clause_symbol))

        elif isinstance(element, int):
            table_element = self.require_table(descriptor.Element)
            builder.add_join(table, table_element, table.c[column] == table_element.c['id'])
            builder.add_clause(table_element.c['atomic_number'] == element)

        else:
            raise NotFound('Cannot parse element: {}'.format(element))

    def _update_atomic_shell(self, builder, table, atomic_shell, column='atomic_shell_id'):
        if hasattr(atomic_shell, 'principal_quantum_number'):
            atomic_shell = atomic_shell.principal_quantum_number

        if isinstance(atomic_shell, str):
            table_notation = self.require_table(property.AtomicShellNotation)
            builder.add_join(table, table_notation, table.c[column] == table_notation.c['atomic_shell_id'])
            builder.add_clause(sqlalchemy.sql.or_(table_notation.c['ascii'] == atomic_shell,
                                                  table_notation.c['utf16'] == atomic_shell))

        elif isinstance(atomic_shell, int):
            table_atomic_shell = self.require_table(descriptor.AtomicShell)
            builder.add_join(table, table_atomic_shell, table.c[column] == table_atomic_shell.c['id'])
            builder.add_clause(table_atomic_shell.c['principal_quantum_number'] == atomic_shell)

        else:
            raise NotFound('Cannot parse atomic shell: {}'.format(atomic_shell))

    def _update_atomic_subshell(self, builder, table, atomic_subshell, column='atomic_subshell_id'):
        if isinstance(atomic_subshell, str):
            table_notation = self.require_table(property.AtomicSubshellNotation)
            builder.add_join(table, table_notation, table.c[column] == table_notation.c['atomic_subshell_id'])
            builder.add_clause(sqlalchemy.sql.or_(table_notation.c['ascii'] == atomic_subshell,
                                                  table_notation.c['utf16'] == atomic_subshell))

        else:
            n, l, j_n = self._expand_atomic_subshell(atomic_subshell)
            table_atomic_subshell = self.require_table(descriptor.AtomicSubshell)
            builder.add_join(table, table_atomic_subshell, table.c[column] == table_atomic_subshell.c['id'])
            builder.add_clause(table_atomic_subshell.c['principal_quantum_number'] == n)
            builder.add_clause(table_atomic_subshell.c['azimuthal_quantum_number'] == l)
            builder.add_clause(table_atomic_subshell.c['total_angular_momentum_nominator'] == j_n)

    def _update_xray_transition(self, builder, table, xray_transition, column='xray_transition_id', search=False):
        if isinstance(xray_transition, str):
            table_notation = self.require_table(property.XrayTransitionNotation)
            builder.add_join(table, table_notation, table.c[column] == table_notation.c['xray_transition_id'])
            builder.add_clause(sqlalchemy.sql.or_(table_notation.c['ascii'] == xray_transition,
                                              table_notation.c['utf16'] == xray_transition))

        else:
            src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = self._expand_xray_transition(xray_transition)
            table_xray_transition = self.require_table(descriptor.XrayTransition)
            builder.add_join(table, table_xray_transition, table.c[column] == table_xray_transition.c['id'])

            if search:
                def create_clause(column, value):
                    if value is not None:
                        return table_xray_transition.c[column] == value
                    else:
                        return table_xray_transition.c[column] != None

                builder.add_clause(create_clause('source_principal_quantum_number', src_n))
                builder.add_clause(create_clause('source_azimuthal_quantum_number', src_l))
                builder.add_clause(create_clause('source_total_angular_momentum_nominator', src_j_n))
                builder.add_clause(create_clause('destination_principal_quantum_number', dst_n))
                builder.add_clause(create_clause('destination_azimuthal_quantum_number', dst_l))
                builder.add_clause(create_clause('destination_total_angular_momentum_nominator', dst_j_n))

            else:
                builder.add_clause(table_xray_transition.c['source_principal_quantum_number'] == src_n)
                builder.add_clause(table_xray_transition.c['source_azimuthal_quantum_number'] == src_l)
                builder.add_clause(table_xray_transition.c['source_total_angular_momentum_nominator'] == src_j_n)
                builder.add_clause(table_xray_transition.c['destination_principal_quantum_number'] == dst_n)
                builder.add_clause(table_xray_transition.c['destination_azimuthal_quantum_number'] == dst_l)
                builder.add_clause(table_xray_transition.c['destination_total_angular_momentum_nominator'] == dst_j_n)

    def _update_reference(self, builder, table, reference, column='reference_id'):
        if isinstance(reference, descriptor.Reference):
            reference = reference.bibtexkey

        table_reference = self.require_table(descriptor.Reference)
        builder.add_column(table_reference.c['bibtexkey'])
        builder.add_join(table, table_reference, table.c[column] == table_reference.c['id'])

        if reference:
            builder.add_clause(table_reference.c['bibtexkey'] == reference)

    def _update_language(self, builder, table, language):
        if isinstance(language, descriptor.Language):
            language = language.key

        table_language = self.require_table(descriptor.Language)
        builder.add_join(table, table_language, table.c['language_id'] == table_language.c['id'])
        builder.add_clause(table_language.c['key'] == language)

    def _update_notation(self, builder, table, notation):
        if isinstance(notation, descriptor.Notation):
            notation = notation.key

        table_notation = self.require_table(descriptor.Notation)
        builder.add_join(table, table_notation, table.c['notation_id'] == table_notation.c['id'])
        builder.add_clause(table_notation.c['key'] == notation)

    def _execute(self, builder, remove_bibtexkey_column=True):
        statement = builder.build()
        logger.debug(statement.compile())

        # Execute
        with self.engine.connect() as conn:
            rows = conn.execute(statement).fetchall()
            if not rows:
                raise NotFound

            # Only one row, no need to check for the preferred references
            elif len(rows) == 1:
                row = rows[0]

            else:
                dictrows = dict((dict(row).get('bibtexkey', None), row) for row in rows)
                row = rows[0] # fall back
                for bibtexkey in self._preferred_references:
                    if bibtexkey in dictrows:
                        row = dictrows[bibtexkey]
                        break

            row = dict(row)
            if remove_bibtexkey_column:
                row.pop('bibtexkey', None)

            if len(row) == 1:
                return row.popitem()[1]
            else:
                return row.values()

    def _execute_many(self, builder, remove_bibtexkey_column=True):
        statement = builder.build()
        logger.debug(statement.compile())

        # Execute
        with self.engine.connect() as conn:
            rows = conn.execute(statement).fetchall()
            if not rows:
                raise NotFound

            outrows = []
            for row in rows:
                row = dict(row)
                if remove_bibtexkey_column:
                    row.pop('bibtexkey', None)
                outrows.append(list(row.values()))

            return outrows

    def get_preferred_references(self):
        return tuple(self._preferred_references)

    def add_preferred_reference(self, reference):
        if isinstance(reference, descriptor.Reference):
            reference = reference.bibtexkey
        if reference in self._preferred_references:
            return

        table = self.require_table(descriptor.Reference)

        builder = StatementBuilder()
        self._update_reference(builder, table, reference, 'id')

        bibtexkey = self._execute(builder, remove_bibtexkey_column=False)

        self._preferred_references.append(bibtexkey)

    def clear_preferred_references(self):
        self._preferred_references.clear()

    def element(self, element):
        table = self.require_table(descriptor.Element)

        builder = StatementBuilder()
        builder.add_column(table.c['atomic_number'])
        self._update_element(builder, table, element, 'id')

        atomic_number = self._execute(builder)
        return descriptor.Element(atomic_number)

    def element_atomic_number(self, element):
        table = self.require_table(descriptor.Element)

        builder = StatementBuilder()
        builder.add_column(table.c['atomic_number'])
        self._update_element(builder, table, element, 'id')

        return self._execute(builder)

    def element_symbol(self, element, reference=None):
        table = self.require_table(property.ElementSymbol)

        builder = StatementBuilder()
        builder.add_column(table.c['value'])
        self._update_element(builder, table, element)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def element_name(self, element, language='en', reference=None):
        table = self.require_table(property.ElementName)

        builder = StatementBuilder()
        builder.add_column(table.c['value'])
        self._update_element(builder, table, element)
        self._update_language(builder, table, language)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def element_atomic_weight(self, element, reference=None):
        table = self.require_table(property.ElementAtomicWeight)

        builder = StatementBuilder()
        builder.add_column(table.c['value'])
        self._update_element(builder, table, element)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def element_mass_density_kg_per_m3(self, element, reference=None):
        table = self.require_table(property.ElementMassDensity)

        builder = StatementBuilder()
        builder.add_column(table.c['value_kg_per_m3'])
        self._update_element(builder, table, element)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def element_xray_transitions(self, element, xray_transition=None, reference=None):
        table_xray = self.require_table(descriptor.XrayTransition)
        table_probability = self.require_table(property.XrayTransitionProbability)

        builder = StatementBuilder()
        builder.add_column(table_xray.c['source_principal_quantum_number'])
        builder.add_column(table_xray.c['source_azimuthal_quantum_number'])
        builder.add_column(table_xray.c['source_total_angular_momentum_nominator'])
        builder.add_column(table_xray.c['destination_principal_quantum_number'])
        builder.add_column(table_xray.c['destination_azimuthal_quantum_number'])
        builder.add_column(table_xray.c['destination_total_angular_momentum_nominator'])
        builder.add_join(table_probability, table_xray, table_probability.c['xray_transition_id'] == table_xray.c['id'])
        builder.add_clause(table_probability.c['value'] > 0.0)
        self._update_element(builder, table_probability, element)
        self._update_reference(builder, table_probability, reference)
        if xray_transition is not None:
            self._update_xray_transition(builder, table_probability, xray_transition, search=True)

        transitions = []
        for src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n in self._execute_many(builder):
            transition = descriptor.XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n)
            transitions.append(transition)

        return tuple(transitions)

    def element_xray_transition(self, element, xray_transition, reference=None):
        table_xray = self.require_table(descriptor.XrayTransition)
        table_probability = self.require_table(property.XrayTransitionProbability)

        builder = StatementBuilder()
        builder.add_column(table_xray.c['source_principal_quantum_number'])
        builder.add_column(table_xray.c['source_azimuthal_quantum_number'])
        builder.add_column(table_xray.c['source_total_angular_momentum_nominator'])
        builder.add_column(table_xray.c['destination_principal_quantum_number'])
        builder.add_column(table_xray.c['destination_azimuthal_quantum_number'])
        builder.add_column(table_xray.c['destination_total_angular_momentum_nominator'])
        builder.add_join(table_probability, table_xray, table_probability.c['xray_transition_id'] == table_xray.c['id'])
        builder.add_clause(table_probability.c['value'] > 0.0)
        self._update_xray_transition(builder, table_xray, xray_transition, 'id')
        self._update_element(builder, table_probability, element)
        self._update_reference(builder, table_probability, reference)

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = self._execute(builder)
        return descriptor.XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n)

    def atomic_shell(self, atomic_shell):
        table = self.require_table(descriptor.AtomicShell)

        builder = StatementBuilder()
        builder.add_column(table.c['principal_quantum_number'])
        self._update_atomic_shell(builder, table, atomic_shell, 'id')

        principal_quantum_number = self._execute(builder)
        return descriptor.AtomicShell(principal_quantum_number)

    def atomic_shell_notation(self, atomic_shell, notation, encoding='utf16', reference=None):
        table = self.require_table(property.AtomicShellNotation)

        builder = StatementBuilder()
        builder.add_column(table.c[encoding])
        self._update_atomic_shell(builder, table, atomic_shell, 'id')
        self._update_notation(builder, table, notation)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def atomic_subshell(self, atomic_subshell):
        table = self.require_table(descriptor.AtomicSubshell)

        builder = StatementBuilder()
        builder.add_column(table.c['principal_quantum_number'])
        builder.add_column(table.c['azimuthal_quantum_number'])
        builder.add_column(table.c['total_angular_momentum_nominator'])
        self._update_atomic_subshell(builder, table, atomic_subshell, 'id')

        n, l, j_n = self._execute(builder)
        return descriptor.AtomicSubshell(n, l, j_n)

    def atomic_subshell_notation(self, atomic_subshell, notation, encoding='utf16', reference=None):
        table = self.require_table(property.AtomicSubshellNotation)

        builder = StatementBuilder()
        builder.add_column(table.c[encoding])
        self._update_atomic_subshell(builder, table, atomic_subshell)
        self._update_notation(builder, table, notation)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellBindingEnergy)

        builder = StatementBuilder()
        builder.add_column(table.c['value_eV'])
        self._update_element(builder, table, element)
        self._update_atomic_subshell(builder, table, atomic_subshell)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellRadiativeWidth)

        builder = StatementBuilder()
        builder.add_column(table.c['value_eV'])
        self._update_element(builder, table, element)
        self._update_atomic_subshell(builder, table, atomic_subshell)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellNonRadiativeWidth)

        builder = StatementBuilder()
        builder.add_column(table.c['value_eV'])
        self._update_element(builder, table, element)
        self._update_atomic_subshell(builder, table, atomic_subshell)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
        table = self.require_table(property.AtomicSubshellOccupancy)

        builder = StatementBuilder()
        builder.add_column(table.c['value'])
        self._update_element(builder, table, element)
        self._update_atomic_subshell(builder, table, atomic_subshell)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def xray_transition(self, xray_transition):
        table = self.require_table(descriptor.XrayTransition)

        builder = StatementBuilder()
        builder.add_column(table.c['source_principal_quantum_number'])
        builder.add_column(table.c['source_azimuthal_quantum_number'])
        builder.add_column(table.c['source_total_angular_momentum_nominator'])
        builder.add_column(table.c['destination_principal_quantum_number'])
        builder.add_column(table.c['destination_azimuthal_quantum_number'])
        builder.add_column(table.c['destination_total_angular_momentum_nominator'])
        self._update_xray_transition(builder, table, xray_transition, 'id')

        src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = self._execute(builder)
        return descriptor.XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n)

    def xray_transition_notation(self, xray_transition, notation, encoding='utf16', reference=None):
        table = self.require_table(property.XrayTransitionNotation)

        builder = StatementBuilder()
        builder.add_column(table.c[encoding])
        self._update_xray_transition(builder, table, xray_transition)
        self._update_notation(builder, table, notation)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def xray_transition_energy_eV(self, element, xray_transition, reference=None):
        table = self.require_table(property.XrayTransitionEnergy)

        builder = StatementBuilder()
        builder.add_column(table.c['value_eV'])
        self._update_element(builder, table, element)
        self._update_xray_transition(builder, table, xray_transition)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def xray_transition_probability(self, element, xray_transition, reference=None):
        table = self.require_table(property.XrayTransitionProbability)

        builder = StatementBuilder()
        builder.add_column(table.c['value'])
        self._update_element(builder, table, element)
        self._update_xray_transition(builder, table, xray_transition)
        self._update_reference(builder, table, reference)

        return self._execute(builder)

    def xray_transition_relative_weight(self, element, xray_transition, reference=None):
        table = self.require_table(property.XrayTransitionRelativeWeight)

        builder = StatementBuilder()
        builder.add_column(table.c['value'])
        self._update_element(builder, table, element)
        self._update_xray_transition(builder, table, xray_transition)
        self._update_reference(builder, table, reference)

        return self._execute(builder)
