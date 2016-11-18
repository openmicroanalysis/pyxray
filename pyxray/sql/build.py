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

# Third party modules.
from sqlalchemy import create_engine
import sqlalchemy.sql as sql
from sqlalchemy.pool import QueuePool

import progressbar

# Local modules.
from pyxray.parser.parser import find_parsers
import pyxray.sql.table as table
from pyxray.sql.base import SqlEngineDatabaseMixin
import pyxray.property as props
from pyxray.base import NotFound

# Globals and constants variables.

class _DatabaseBuilder(metaclass=abc.ABCMeta):

    def __init__(self):
        self._propfuncs = {}

        self._propfuncs[props.ElementSymbol] = self._add_element_symbol_property
        self._propfuncs[props.ElementName] = self._add_element_name_property
        self._propfuncs[props.ElementAtomicWeight] = self._add_element_atomic_weight_property
        self._propfuncs[props.ElementMassDensity] = self._add_element_mass_density_property

        self._propfuncs[props.AtomicShellNotation] = self._add_atomic_shell_notation_property

        self._propfuncs[props.AtomicSubshellNotation] = self._add_atomic_subshell_notation_property
        self._propfuncs[props.AtomicSubshellBindingEnergy] = self._add_atomic_subshell_binding_energy_property
        self._propfuncs[props.AtomicSubshellRadiativeWidth] = self._add_atomic_subshell_radiative_width_property
        self._propfuncs[props.AtomicSubshellNonRadiativeWidth] = self._add_atomic_subshell_nonradiative_width_property
        self._propfuncs[props.AtomicSubshellOccupancy] = self._add_atomic_subshell_occupancy_property

        self._propfuncs[props.TransitionNotation] = self._add_transition_notation_property
        self._propfuncs[props.TransitionEnergy] = self._add_transition_energy_property
        self._propfuncs[props.TransitionProbability] = self._add_transition_propability_property
        self._propfuncs[props.TransitionRelativeWeight] = self._add_transition_relative_weight_property

        self._propfuncs[props.TransitionSetNotation] = self._add_transitionset_notation_property
        self._propfuncs[props.TransitionSetEnergy] = self._add_transitionset_energy_property
        self._propfuncs[props.TransitionSetRelativeWeight] = self._add_transitionset_relative_weight_property

    @abc.abstractmethod
    def _backup_existing_database(self): #pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def _create_database_engine(self): #pragma: no cover
        raise NotImplementedError

    @abc.abstractmethod
    def _revert_to_backup_database(self): #pragma: no cover
        raise NotImplementedError

    def _cleanup(self):
        pass

    def _find_parsers(self):
        return find_parsers()

    def _create_progressbar(self, desc):
        widgets = [desc, ' ' * 4, progressbar.Bar(), progressbar.Percentage()]
        return progressbar.ProgressBar(max_value=100, widgets=widgets)

    def _process_parser(self, conn, name, parser):
        bar = self._create_progressbar(name)
        parser.add_reporthook(bar.update)

        try:
            bar.start()

            for prop in parser:
                func = self._propfuncs[type(prop)]
                func(conn, prop)

        finally:
            parser.clear_reporthooks()
            bar.finish()

    def purge_database(self, engine):
        table.metadata.drop_all(engine) #@UndefinedVariable

    def build(self):
        parsers = self._find_parsers()
        logger.info('Found {:d} parsers'.format(len(parsers)))

        backuped = self._backup_existing_database()
        if backuped:
            logger.info('Backup existing database')

        try:
            engine = self._create_database_engine()
            logger.info('Created database engine')

            self.purge_database(engine)
            logger.info('Purged database')

            for name, parser in parsers:
                with engine.begin() as conn:
                    self._process_parser(conn, name, parser)
                logger.info('Populated {0}'.format(name))

        except:
            reverted = self._revert_to_backup_database()
            if reverted:
                logger.info('Reverted to previous database')
            raise

        self._cleanup()

    def _insert_element(self, conn, element):
        atomic_number = element.atomic_number

        tbl = table.element
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(atomic_number=atomic_number)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _insert_atomic_shell(self, conn, atomic_shell):
        principal_quantum_number = atomic_shell.principal_quantum_number

        tbl = table.atomic_shell
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(principal_quantum_number=principal_quantum_number)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _insert_atomic_subshell(self, conn, atomic_subshell):
        atomic_shell_id = self._require_atomic_shell(conn, atomic_subshell.atomic_shell)
        azimuthal_quantum_number = atomic_subshell.azimuthal_quantum_number
        total_angular_momentum_nominator = atomic_subshell.total_angular_momentum_nominator

        tbl = table.atomic_subshell
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(atomic_shell_id=atomic_shell_id,
                                 azimuthal_quantum_number=azimuthal_quantum_number,
                                 total_angular_momentum_nominator=total_angular_momentum_nominator)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _insert_transition(self, conn, transition):
        source_subshell_id = \
            self._require_atomic_subshell(conn, transition.source_subshell)
        destination_subshell_id = \
            self._require_atomic_subshell(conn, transition.destination_subshell)
        if transition.secondary_destination_subshell:
            secondary_destination_subshell_id = \
                self._require_atomic_subshell(conn, transition.secondary_destination_subshell)
        else:
            secondary_destination_subshell_id = None

        tbl = table.transition
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(source_subshell_id=source_subshell_id,
                                 destination_subshell_id=destination_subshell_id,
                                 secondary_destination_subshell_id=secondary_destination_subshell_id)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _insert_transitionset(self, conn, transitionset):
        transition_ids = set()
        for transition in transitionset.transitions:
            transition_id = self._require_transition(conn, transition)
            transition_ids.add(transition_id)

        table.transitionset.create(conn, checkfirst=True)
        table.transitionset_association.create(conn, checkfirst=True)

        # Create empty transitionset row
        command = sql.insert(table.transitionset)
        result = conn.execute(command)
        transitionset_id = result.inserted_primary_key[0]

        # Populate association table
        for transition_id in transition_ids:
            command = sql.insert(table.transitionset_association)
            command = command.values(transitionset_id=transitionset_id,
                                     transition_id=transition_id)
            conn.execute(command)

        return transitionset_id

    def _insert_language(self, conn, language):
        code = language.code

        tbl = table.language
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(code=code)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _insert_notation(self, conn, notation):
        name = notation.name

        tbl = table.notation
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(name=name)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _insert_reference(self, conn, reference):
        tbl = table.reference
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(bibtexkey=reference.bibtexkey,
                                 author=reference.author,
                                 year=reference.year,
                                 title=reference.title,
                                 type=reference.type,
                                 booktitle=reference.booktitle,
                                 editor=reference.editor,
                                 pages=reference.pages,
                                 edition=reference.edition,
                                 journal=reference.journal,
                                 school=reference.school,
                                 address=reference.address,
                                 url=reference.url,
                                 note=reference.note,
                                 number=reference.number,
                                 series=reference.series,
                                 volume=reference.volume,
                                 publisher=reference.publisher,
                                 organization=reference.organization,
                                 chapter=reference.chapter,
                                 howpublished=reference.howpublished,
                                 doi=reference.doi)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _require_element(self, conn, element):
        try:
            return self._get_element_id(conn, element)
        except NotFound:
            return self._insert_element(conn, element)

    def _require_atomic_shell(self, conn, atomic_shell):
        try:
            return self._get_atomic_shell_id(conn, atomic_shell)
        except NotFound:
            return self._insert_atomic_shell(conn, atomic_shell)

    def _require_atomic_subshell(self, conn, atomic_subshell):
        # Ensure atomic shell exists
        self._require_atomic_shell(conn, atomic_subshell.atomic_shell)

        try:
            return self._get_atomic_subshell_id(conn, atomic_subshell)
        except NotFound:
            return self._insert_atomic_subshell(conn, atomic_subshell)

    def _require_transition(self, conn, transition):
        # Ensure atomic subshells exist
        self._require_atomic_subshell(conn, transition.source_subshell)
        self._require_atomic_subshell(conn, transition.destination_subshell)
        if transition.secondary_destination_subshell:
            self._require_atomic_subshell(conn, transition.secondary_destination_subshell)

        try:
            return self._get_transition_id(conn, transition)
        except NotFound:
            return self._insert_transition(conn, transition)

    def _require_transitionset(self, conn, transitionset):
        # Ensure transitions exist
        for transition in transitionset.transitions:
            self._require_transition(conn, transition)

        try:
            return self._get_transitionset_id(conn, transitionset)
        except NotFound:
            return self._insert_transitionset(conn, transitionset)

    def _require_language(self, conn, language):
        try:
            return self._get_language_id(conn, language)
        except NotFound:
            return self._insert_language(conn, language)

    def _require_notation(self, conn, notation):
        try:
            return self._get_notation_id(conn, notation)
        except NotFound:
            return self._insert_notation(conn, notation)

    def _require_reference(self, conn, reference):
        try:
            return self._get_reference_id(conn, reference)
        except NotFound:
            return self._insert_reference(conn, reference)

    def _add_element_symbol_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        symbol = prop.symbol

        tbl = table.element_symbol
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 symbol=symbol)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_element_name_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        language_id = self._require_language(conn, prop.language)
        name = prop.name

        tbl = table.element_name
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 language_id=language_id,
                                 name=name)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_element_atomic_weight_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        value = prop.value

        tbl = table.element_atomic_weight
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 value=value)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_element_mass_density_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        value_kg_per_m3 = prop.value_kg_per_m3

        tbl = table.element_mass_density
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 value_kg_per_m3=value_kg_per_m3)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_atomic_shell_notation_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        atomic_shell_id = self._require_atomic_shell(conn, prop.atomic_shell)
        notation_id = self._require_notation(conn, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.atomic_shell_notation
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 atomic_shell_id=atomic_shell_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_atomic_subshell_notation_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        atomic_subshell_id = self._require_atomic_subshell(conn, prop.atomic_subshell)
        notation_id = self._require_notation(conn, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.atomic_subshell_notation
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_atomic_subshell_binding_energy_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(conn, prop.atomic_subshell)
        value_eV = prop.value_eV

        tbl = table.atomic_subshell_binding_energy
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value_eV=value_eV)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_atomic_subshell_radiative_width_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(conn, prop.atomic_subshell)
        value_eV = prop.value_eV

        tbl = table.atomic_subshell_radiative_width
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value_eV=value_eV)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_atomic_subshell_nonradiative_width_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(conn, prop.atomic_subshell)
        value_eV = prop.value_eV

        tbl = table.atomic_subshell_nonradiative_width
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value_eV=value_eV)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_atomic_subshell_occupancy_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(conn, prop.atomic_subshell)
        value = prop.value

        tbl = table.atomic_subshell_occupancy
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value=value)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transition_notation_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        transition_id = self._require_transition(conn, prop.transition)
        notation_id = self._require_notation(conn, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.transition_notation
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 transition_id=transition_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transition_energy_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        transition_id = self._require_transition(conn, prop.transition)
        value_eV = prop.value_eV

        tbl = table.transition_energy
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transition_id=transition_id,
                                 value_eV=value_eV)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transition_propability_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        transition_id = self._require_transition(conn, prop.transition)
        value = prop.value

        tbl = table.transition_probability
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transition_id=transition_id,
                                 value=value)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transition_relative_weight_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        transition_id = self._require_transition(conn, prop.transition)
        value = prop.value

        tbl = table.transition_relative_weight
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transition_id=transition_id,
                                 value=value)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transitionset_notation_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        transitionset_id = self._require_transitionset(conn, prop.transitionset)
        notation_id = self._require_notation(conn, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.transitionset_notation
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 transitionset_id=transitionset_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transitionset_energy_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        transitionset_id = self._require_transitionset(conn, prop.transitionset)
        value_eV = prop.value_eV

        tbl = table.transitionset_energy
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transitionset_id=transitionset_id,
                                 value_eV=value_eV)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

    def _add_transitionset_relative_weight_property(self, conn, prop):
        reference_id = self._require_reference(conn, prop.reference)
        element_id = self._require_element(conn, prop.element)
        transitionset_id = self._require_transitionset(conn, prop.transitionset)
        value = prop.value

        tbl = table.transitionset_relative_weight
        tbl.create(conn, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transitionset_id=transitionset_id,
                                 value=value)
        result = conn.execute(command)
        return result.inserted_primary_key[0]

class SqliteDatabaseBuilder(SqlEngineDatabaseMixin, _DatabaseBuilder):

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
            shutil.copy(self.filepath, oldfilepath)
            self._oldfilepath = oldfilepath
            return True
        return False

    def _revert_to_backup_database(self):
        if self._oldfilepath:
            os.rename(self._oldfilepath, self.filepath)
            return True
        return False

    def _create_database_engine(self):
        return create_engine('sqlite:///' + self.filepath,
                             poolclass=QueuePool,
                             pool_size=20, max_overflow=0)

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
