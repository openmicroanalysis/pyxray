"""
Build the SQL database from the registered parsers.
"""

# Standard library modules.
import os
import logging
logger = logging.getLogger(__name__)
import abc
import argparse
import shutil
import sqlite3

# Third party modules.
try:
    import progressbar
except ImportError:
    progressbar = None

# Local modules.
import pyxray.data
import pyxray.property as props
from pyxray.base import NotFound
from pyxray.parser.parser import find_parsers
from pyxray.sql.command import SelectBuilder, InsertBuilder, CreateTableBuilder
from pyxray.sql.base import SelectMixin, TableMixin, InsertMixin

# Globals and constants variables.

class SqlDatabaseBuilder(SelectMixin, TableMixin, InsertMixin,
                         metaclass=abc.ABCMeta):

    def __init__(self):
        self._propfuncs = {}

        self._propfuncs[props.ElementSymbol] = self._insert_element_symbol_property
        self._propfuncs[props.ElementName] = self._insert_element_name_property
        self._propfuncs[props.ElementAtomicWeight] = self._insert_element_atomic_weight_property
        self._propfuncs[props.ElementMassDensity] = self._insert_element_mass_density_property

        self._propfuncs[props.AtomicShellNotation] = self._insert_atomic_shell_notation_property

        self._propfuncs[props.AtomicSubshellNotation] = self._insert_atomic_subshell_notation_property
        self._propfuncs[props.AtomicSubshellBindingEnergy] = self._insert_atomic_subshell_binding_energy_property
        self._propfuncs[props.AtomicSubshellRadiativeWidth] = self._insert_atomic_subshell_radiative_width_property
        self._propfuncs[props.AtomicSubshellNonRadiativeWidth] = self._insert_atomic_subshell_nonradiative_width_property
        self._propfuncs[props.AtomicSubshellOccupancy] = self._insert_atomic_subshell_occupancy_property

        self._propfuncs[props.XrayTransitionNotation] = self._insert_xray_transition_notation_property
        self._propfuncs[props.XrayTransitionEnergy] = self._insert_xray_transition_energy_property
        self._propfuncs[props.XrayTransitionProbability] = self._insert_xray_transition_propability_property
        self._propfuncs[props.XrayTransitionRelativeWeight] = self._insert_xray_transition_relative_weight_property

        self._propfuncs[props.XrayTransitionSetNotation] = self._insert_xray_transitionset_notation_property
        self._propfuncs[props.XrayTransitionSetEnergy] = self._insert_xray_transitionset_energy_property
        self._propfuncs[props.XrayTransitionSetRelativeWeight] = self._insert_xray_transitionset_relative_weight_property

    @abc.abstractmethod
    def _backup_existing_database(self): #pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def _create_database_connection(self): #pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def _revert_to_backup_database(self): #pragma: no cover
        raise NotImplementedError

    def _cleanup(self):
        pass

    def _find_parsers(self):
        return find_parsers()

    def _create_progressbar(self, desc):
        if not progressbar:
            return
        widgets = [desc, ' ' * 4, progressbar.Bar(), progressbar.Percentage()]
        return progressbar.ProgressBar(max_value=100, widgets=widgets)

    def _process_parser(self, connection, name, parser):
        bar = self._create_progressbar(name)
        if bar: parser.add_reporthook(bar.update)

        try:
            if bar: bar.start()

            for prop in parser:
                func = self._propfuncs[type(prop)]
                func(connection, prop)

        finally:
            parser.clear_reporthooks()
            if bar: bar.finish()

    def build(self):
        parsers = self._find_parsers()
        logger.info('Found {:d} parsers'.format(len(parsers)))

        pyxray.data._close_sql_database()
        logger.info('Closed connection')

        backuped = self._backup_existing_database()
        if backuped:
            logger.info('Backup existing database')

        connection = None
        try:
            connection = self._create_database_connection()
            logger.info('Created database connection')

            self._create_tables(connection)
            logger.info('Created tables')

            for name, parser in parsers:
                self._process_parser(connection, name, parser)
                logger.info('Populated {0}'.format(name))

            connection.commit()
            connection.close()
        except:
            if connection:
                connection.close()

            reverted = self._revert_to_backup_database()
            if reverted:
                logger.info('Reverted to previous database')
            raise

        self._cleanup()

    def _create_tables(self, connection):
        self._create_element_table(connection)
        self._create_element_symbol_table(connection)
        self._create_element_name_table(connection)
        self._create_element_atomic_weight_table(connection)
        self._create_element_mass_density_table(connection)

        self._create_atomic_shell_table(connection)
        self._create_atomic_shell_notation_table(connection)

        self._create_atomic_subshell_table(connection)
        self._create_atomic_subshell_notation_table(connection)
        self._create_atomic_subshell_binding_energy_table(connection)
        self._create_atomic_subshell_radiative_width_table(connection)
        self._create_atomic_subshell_nonradiative_width_table(connection)
        self._create_atomic_subshell_occupancy_table(connection)

        self._create_xray_transition_table(connection)
        self._create_xray_transition_notation_table(connection)
        self._create_xray_transition_energy_table(connection)
        self._create_xray_transition_probability_table(connection)
        self._create_xray_transition_relative_weight_table(connection)

        self._create_xray_transitionset_table(connection)
        self._create_xray_transitionset_association_table(connection)
        self._create_xray_transitionset_notation_table(connection)
        self._create_xray_transitionset_energy_table(connection)
        self._create_xray_transitionset_relative_weight_table(connection)

        self._create_language_table(connection)
        self._create_notation_table(connection)
        self._create_reference_table(connection)

    def _create_table(self, connection, builder):
        sql = builder.build()

        cur = connection.cursor()
        cur.execute(sql)
        cur.close()

    def _create_element_table(self, connection):
        builder = CreateTableBuilder('element')
        self._append_table_primary_key_columns(builder)
        builder.add_integer_column('atomic_number', nullable=False)
        self._create_table(connection, builder)

    def _create_element_symbol_table(self, connection):
        builder = CreateTableBuilder('element_symbol')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_reference_columns(builder)
        builder.add_string_column('symbol', 3, nullable=False, casesensitive=False)
        self._create_table(connection, builder)

    def _create_element_name_table(self, connection):
        builder = CreateTableBuilder('element_name')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_language_columns(builder)
        self._append_table_reference_columns(builder)
        builder.add_string_column('name', 256, nullable=False, casesensitive=False)
        self._create_table(connection, builder)

    def _create_element_atomic_weight_table(self, connection):
        builder = CreateTableBuilder('element_atomic_weight')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_reference_columns(builder)
        self._append_table_value_property_columns(builder)
        self._create_table(connection, builder)

    def _create_element_mass_density_table(self, connection):
        builder = CreateTableBuilder('element_mass_density')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_reference_columns(builder)
        builder.add_float_column('value_kg_per_m3', nullable=False)
        self._create_table(connection, builder)

    def _create_atomic_shell_table(self, connection):
        builder = CreateTableBuilder('atomic_shell')
        self._append_table_primary_key_columns(builder)
        builder.add_integer_column('principal_quantum_number', nullable=False)
        self._create_table(connection, builder)

    def _create_atomic_shell_notation_table(self, connection):
        builder = CreateTableBuilder('atomic_shell_notation')
        self._append_table_primary_key_columns(builder)
        self._append_table_atomic_shell_columns(builder)
        self._append_table_notation_columns(builder)
        self._append_table_notation_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_atomic_subshell_table(self, connection):
        builder = CreateTableBuilder('atomic_subshell')
        self._append_table_primary_key_columns(builder)
        self._append_table_atomic_shell_columns(builder)
        builder.add_integer_column('azimuthal_quantum_number', nullable=False)
        builder.add_integer_column('total_angular_momentum_nominator', nullable=False)
        self._create_table(connection, builder)

    def _create_atomic_subshell_notation_table(self, connection):
        builder = CreateTableBuilder('atomic_subshell_notation')
        self._append_table_primary_key_columns(builder)
        self._append_table_atomic_subshell_columns(builder)
        self._append_table_notation_columns(builder)
        self._append_table_notation_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_atomic_subshell_binding_energy_table(self, connection):
        builder = CreateTableBuilder('atomic_subshell_binding_energy')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_atomic_subshell_columns(builder)
        self._append_table_energy_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_atomic_subshell_radiative_width_table(self, connection):
        builder = CreateTableBuilder('atomic_subshell_radiative_width')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_atomic_subshell_columns(builder)
        self._append_table_energy_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_atomic_subshell_nonradiative_width_table(self, connection):
        builder = CreateTableBuilder('atomic_subshell_nonradiative_width')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_atomic_subshell_columns(builder)
        self._append_table_energy_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_atomic_subshell_occupancy_table(self, connection):
        builder = CreateTableBuilder('atomic_subshell_occupancy')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_atomic_subshell_columns(builder)
        self._append_table_value_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transition_table(self, connection):
        builder = CreateTableBuilder('xray_transition')
        self._append_table_primary_key_columns(builder)
        builder.add_foreignkey_column('source_subshell_id', 'atomic_subshell', 'id')
        builder.add_foreignkey_column('destination_subshell_id', 'atomic_subshell', 'id')
        self._create_table(connection, builder)

    def _create_xray_transition_notation_table(self, connection):
        builder = CreateTableBuilder('xray_transition_notation')
        self._append_table_primary_key_columns(builder)
        self._append_table_xray_transition_columns(builder)
        self._append_table_notation_columns(builder)
        self._append_table_notation_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transition_energy_table(self, connection):
        builder = CreateTableBuilder('xray_transition_energy')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_xray_transition_columns(builder)
        self._append_table_energy_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transition_probability_table(self, connection):
        builder = CreateTableBuilder('xray_transition_probability')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_xray_transition_columns(builder)
        self._append_table_value_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transition_relative_weight_table(self, connection):
        builder = CreateTableBuilder('xray_transition_relative_weight')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_xray_transition_columns(builder)
        self._append_table_value_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transitionset_table(self, connection):
        builder = CreateTableBuilder('xray_transitionset')
        self._append_table_primary_key_columns(builder)
        builder.add_integer_column('count', nullable=False)
        self._create_table(connection, builder)

    def _create_xray_transitionset_association_table(self, connection):
        builder = CreateTableBuilder('xray_transitionset_association')
        self._append_table_primary_key_columns(builder)
        builder.add_foreignkey_column('xray_transitionset_id', 'xray_transitionset', 'id')
        builder.add_foreignkey_column('xray_transition_id', 'xray_transition', 'id')
        self._create_table(connection, builder)

    def _create_xray_transitionset_notation_table(self, connection):
        builder = CreateTableBuilder('xray_transitionset_notation')
        self._append_table_primary_key_columns(builder)
        self._append_table_xray_transitionset_columns(builder)
        self._append_table_notation_columns(builder)
        self._append_table_notation_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transitionset_energy_table(self, connection):
        builder = CreateTableBuilder('xray_transitionset_energy')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_xray_transitionset_columns(builder)
        self._append_table_energy_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_xray_transitionset_relative_weight_table(self, connection):
        builder = CreateTableBuilder('xray_transitionset_relative_weight')
        self._append_table_primary_key_columns(builder)
        self._append_table_element_columns(builder)
        self._append_table_xray_transitionset_columns(builder)
        self._append_table_value_property_columns(builder)
        self._append_table_reference_columns(builder)
        self._create_table(connection, builder)

    def _create_language_table(self, connection):
        builder = CreateTableBuilder('language')
        self._append_table_primary_key_columns(builder)
        builder.add_string_column('code', 3, nullable=False, casesensitive=False)
        self._create_table(connection, builder)

    def _create_notation_table(self, connection):
        builder = CreateTableBuilder('notation')
        self._append_table_primary_key_columns(builder)
        builder.add_string_column('name', 25, nullable=False, casesensitive=False)
        self._create_table(connection, builder)

    def _create_reference_table(self, connection):
        builder = CreateTableBuilder('ref')
        self._append_table_primary_key_columns(builder)
        builder.add_string_column('bibtexkey', 256, nullable=False, casesensitive=False)
        for column in ['author', 'year', 'title', 'type', 'booktitle', 'editor',
                       'pages', 'edition', 'journal', 'school', 'address',
                       'url', 'note', 'number', 'series', 'volume', 'publisher',
                       'organization', 'chapter', 'howpublished', 'doi']:
            builder.add_string_column(column)
        self._create_table(connection, builder)

    def _select_id(self, connection, table, builder):
        builder.add_select(table, 'id')
        builder.add_from(table)
        sql, params = builder.build()

        cur = connection.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        if row is None:
            raise NotFound('No element found')

        return row[0]

    def _select_element_id(self, connection, element):
        builder = SelectBuilder()
        self._append_select_element(connection, builder, 'element', 'id', element)
        return self._select_id(connection, 'element', builder)

    def _select_atomic_shell_id(self, connection, atomic_shell):
        builder = SelectBuilder()
        self._append_select_atomic_shell(connection, builder, 'atomic_shell', 'id', atomic_shell)
        return self._select_id(connection, 'atomic_shell', builder)

    def _select_atomic_subshell_id(self, connection, atomic_subshell):
        builder = SelectBuilder()
        self._append_select_atomic_subshell(connection, builder, 'atomic_subshell', 'id', atomic_subshell)
        return self._select_id(connection, 'atomic_subshell', builder)

    def _select_xray_transition_id(self, connection, xraytransition):
        builder = SelectBuilder()
        self._append_select_xray_transition(connection, builder, 'xray_transition', 'id', xraytransition)
        return self._select_id(connection, 'xray_transition', builder)

    def _select_xray_transitionset_id(self, connection, xraytransitionset):
        builder = SelectBuilder()
        self._append_select_xray_transitionset(connection, builder, 'xray_transitionset', 'id', xraytransitionset)
        return self._select_id(connection, 'xray_transitionset', builder)

    def _select_notation_id(self, connection, notation):
        builder = SelectBuilder()
        self._append_select_notation(connection, builder, 'notation', notation)
        return self._select_id(connection, 'notation', builder)

    def _select_language_id(self, connection, language):
        builder = SelectBuilder()
        self._append_select_language(connection, builder, 'language', language)
        return self._select_id(connection, 'language', builder)

    def _select_reference_id(self, connection, reference):
        builder = SelectBuilder()
        self._append_select_reference(connection, builder, 'ref', reference)
        return self._select_id(connection, 'ref', builder)

    def _require_element(self, connection, element):
        try:
            return self._select_element_id(connection, element)
        except NotFound:
            return self._insert_element(connection, element)

    def _require_atomic_shell(self, connection, atomic_shell):
        try:
            return self._select_atomic_shell_id(connection, atomic_shell)
        except NotFound:
            return self._insert_atomic_shell(connection, atomic_shell)

    def _require_atomic_subshell(self, connection, atomic_subshell):
        # Ensure atomic shell exists
        self._require_atomic_shell(connection, atomic_subshell.atomic_shell)

        try:
            return self._select_atomic_subshell_id(connection, atomic_subshell)
        except NotFound:
            return self._insert_atomic_subshell(connection, atomic_subshell)

    def _require_xray_transition(self, connection, xraytransition):
        # Ensure atomic subshells exist
        self._require_atomic_subshell(connection, xraytransition.source_subshell)
        self._require_atomic_subshell(connection, xraytransition.destination_subshell)

        try:
            return self._select_xray_transition_id(connection, xraytransition)
        except NotFound:
            return self._insert_xray_transition(connection, xraytransition)

    def _require_xray_transitionset(self, connection, xraytransitionset):
        # Ensure transitions exist
        for xraytransition in xraytransitionset.possible_transitions:
            self._require_xray_transition(connection, xraytransition)

        try:
            return self._select_xray_transitionset_id(connection, xraytransitionset)
        except NotFound:
            return self._insert_xray_transitionset(connection, xraytransitionset)
#
    def _require_language(self, connection, language):
        try:
            return self._select_language_id(connection, language)
        except NotFound:
            return self._insert_language(connection, language)

    def _require_notation(self, connection, notation):
        try:
            return self._select_notation_id(connection, notation)
        except NotFound:
            return self._insert_notation(connection, notation)

    def _require_reference(self, connection, reference):
        try:
            return self._select_reference_id(connection, reference)
        except NotFound:
            return self._insert_reference(connection, reference)

    def _insert(self, connection, builder):
        sql, params = builder.build()

        cur = connection.cursor()
        cur.execute(sql, params)
        cur.close()

        return cur.lastrowid

    def _insert_element(self, connection, element):
        builder = InsertBuilder('element')
        builder.add_column('atomic_number', element.atomic_number)
        return self._insert(connection, builder)

    def _insert_atomic_shell(self, connection, atomic_shell):
        builder = InsertBuilder('atomic_shell')
        builder.add_column('principal_quantum_number', atomic_shell.principal_quantum_number)
        return self._insert(connection, builder)

    def _insert_atomic_subshell(self, connection, atomic_subshell):
        atomic_shell_id = self._require_atomic_shell(connection, atomic_subshell.atomic_shell)

        builder = InsertBuilder('atomic_subshell')
        builder.add_column('atomic_shell_id', atomic_shell_id)
        builder.add_column('azimuthal_quantum_number', atomic_subshell.azimuthal_quantum_number)
        builder.add_column('total_angular_momentum_nominator', atomic_subshell.total_angular_momentum_nominator)
        return self._insert(connection, builder)
#
    def _insert_xray_transition(self, connection, xraytransition):
        source_subshell_id = \
            self._require_atomic_subshell(connection, xraytransition.source_subshell)
        destination_subshell_id = \
            self._require_atomic_subshell(connection, xraytransition.destination_subshell)

        builder = InsertBuilder('xray_transition')
        builder.add_column('source_subshell_id', source_subshell_id)
        builder.add_column('destination_subshell_id', destination_subshell_id)
        return self._insert(connection, builder)

    def _insert_xray_transitionset(self, connection, xraytransitionset):
        xray_transition_ids = set()
        for xraytransition in xraytransitionset.possible_transitions:
            xray_transition_id = self._require_xray_transition(connection, xraytransition)
            xray_transition_ids.add(xray_transition_id)

        builder = InsertBuilder('xray_transitionset')
        builder.add_column('count', len(xray_transition_ids))
        xray_transitionset_id = self._insert(connection, builder)

        for xray_transition_id in xray_transition_ids:
            builder = InsertBuilder('xray_transitionset_association')
            builder.add_column('xray_transitionset_id', xray_transitionset_id)
            builder.add_column('xray_transition_id', xray_transition_id)
            self._insert(connection, builder)

        return xray_transitionset_id
#
    def _insert_language(self, connection, language):
        builder = InsertBuilder('language')
        builder.add_column('code', language.code)
        return self._insert(connection, builder)

    def _insert_notation(self, connection, notation):
        builder = InsertBuilder('notation')
        builder.add_column('name', notation.name)
        return self._insert(connection, builder)

    def _insert_reference(self, connection, reference):
        builder = InsertBuilder('ref')
        builder.add_column('bibtexkey', reference.bibtexkey)
        builder.add_column('author', reference.author)
        builder.add_column('year', reference.year)
        builder.add_column('title', reference.title)
        builder.add_column('type', reference.type)
        builder.add_column('booktitle', reference.booktitle)
        builder.add_column('editor', reference.editor)
        builder.add_column('pages', reference.pages)
        builder.add_column('edition', reference.edition)
        builder.add_column('journal', reference.journal)
        builder.add_column('school', reference.school)
        builder.add_column('address', reference.address)
        builder.add_column('url', reference.url)
        builder.add_column('note', reference.note)
        builder.add_column('number', reference.number)
        builder.add_column('series', reference.series)
        builder.add_column('volume', reference.volume)
        builder.add_column('publisher', reference.publisher)
        builder.add_column('organization', reference.organization)
        builder.add_column('chapter', reference.chapter)
        builder.add_column('howpublished', reference.howpublished)
        builder.add_column('doi', reference.doi)
        return self._insert(connection, builder)

    def _insert_element_symbol_property(self, connection, prop):
        builder = InsertBuilder('element_symbol')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('symbol', prop.symbol)
        return self._insert(connection, builder)

    def _insert_element_name_property(self, connection, prop):
        builder = InsertBuilder('element_name')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_language_columns(connection, builder, prop)
        builder.add_column('name', prop.name)
        return self._insert(connection, builder)

    def _insert_element_atomic_weight_property(self, connection, prop):
        builder = InsertBuilder('element_atomic_weight')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('value', prop.value)
        return self._insert(connection, builder)

    def _insert_element_mass_density_property(self, connection, prop):
        builder = InsertBuilder('element_mass_density')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('value_kg_per_m3', prop.value_kg_per_m3)
        return self._insert(connection, builder)

    def _insert_atomic_shell_notation_property(self, connection, prop):
        builder = InsertBuilder('atomic_shell_notation')
        self._append_insert_property_atomic_shell_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_notation_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_atomic_subshell_notation_property(self, connection, prop):
        builder = InsertBuilder('atomic_subshell_notation')
        self._append_insert_property_atomic_subshell_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_notation_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_atomic_subshell_binding_energy_property(self, connection, prop):
        builder = InsertBuilder('atomic_subshell_binding_energy')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_atomic_subshell_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_energy_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_atomic_subshell_radiative_width_property(self, connection, prop):
        builder = InsertBuilder('atomic_subshell_radiative_width')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_atomic_subshell_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_energy_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_atomic_subshell_nonradiative_width_property(self, connection, prop):
        builder = InsertBuilder('atomic_subshell_nonradiative_width')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_atomic_subshell_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_energy_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_atomic_subshell_occupancy_property(self, connection, prop):
        builder = InsertBuilder('atomic_subshell_occupancy')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_atomic_subshell_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('value', prop.value)
        return self._insert(connection, builder)

    def _insert_xray_transition_notation_property(self, connection, prop):
        builder = InsertBuilder('xray_transition_notation')
        self._append_insert_property_xray_transition_columns(connection, builder, prop)
        self._append_insert_property_notation_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_xray_transition_energy_property(self, connection, prop):
        builder = InsertBuilder('xray_transition_energy')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_xray_transition_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_energy_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_xray_transition_propability_property(self, connection, prop):
        builder = InsertBuilder('xray_transition_probability')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_xray_transition_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('value', prop.value)
        return self._insert(connection, builder)

    def _insert_xray_transition_relative_weight_property(self, connection, prop):
        builder = InsertBuilder('xray_transition_relative_weight')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_xray_transition_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('value', prop.value)
        return self._insert(connection, builder)

    def _insert_xray_transitionset_notation_property(self, connection, prop):
        builder = InsertBuilder('xray_transitionset_notation')
        self._append_insert_property_xray_transitionset_columns(connection, builder, prop)
        self._append_insert_property_notation_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_xray_transitionset_energy_property(self, connection, prop):
        builder = InsertBuilder('xray_transitionset_energy')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_xray_transitionset_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        self._append_insert_property_energy_columns(connection, builder, prop)
        return self._insert(connection, builder)

    def _insert_xray_transitionset_relative_weight_property(self, connection, prop):
        builder = InsertBuilder('xray_transitionset_relative_weight')
        self._append_insert_property_element_columns(connection, builder, prop)
        self._append_insert_property_xray_transitionset_columns(connection, builder, prop)
        self._append_insert_property_reference_columns(connection, builder, prop)
        builder.add_column('value', prop.value)
        return self._insert(connection, builder)

class SqliteDatabaseBuilder(SqlDatabaseBuilder):

    def __init__(self, filepath=None):
        super().__init__()
        if filepath is None:
            filepath = self._get_default_database_filepath()
        self._filepath = filepath
        self._oldfilepath = None

    def _get_default_database_filepath(self):
        packagedir = os.path.join(os.path.dirname(__file__), '..')
        filepath = os.path.join(packagedir, 'data', 'pyxray.sql')
        return os.path.abspath(filepath)

    def _backup_existing_database(self):
        if os.path.exists(self.filepath):
            oldfilepath = self.filepath + '.old'
            shutil.move(self.filepath, oldfilepath)
            self._oldfilepath = oldfilepath
            return True
        return False

    def _revert_to_backup_database(self):
        if self._oldfilepath:
            os.rename(self._oldfilepath, self.filepath)
            return True
        return False

    def _create_database_connection(self):
        return sqlite3.connect(self.filepath)

    @property
    def filepath(self):
        return self._filepath

def main(): #pragma: no cover
    parser = argparse.ArgumentParser(description='Build the SQL database')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show debug information')

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(level)
    logging.basicConfig()

    builder = SqliteDatabaseBuilder()
    builder.build()

if __name__ == '__main__': #pragma: no cover
    main()
