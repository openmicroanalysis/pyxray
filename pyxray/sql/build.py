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
from operator import itemgetter

# Third party modules.
from sqlalchemy import create_engine
import sqlalchemy.sql as sql

import progressbar

# Local modules.
from pyxray.parser.parser import find_parsers
import pyxray.sql.table as table
import pyxray.property as props
import pyxray.cbook as cbook

# Globals and constants variables.

class NotFound(Exception):
    pass

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

        self._propfuncs[props.TransitionSetNotation] = self._add_transitionset_notation_property
        self._propfuncs[props.TransitionSetEnergy] = self._add_transitionset_energy_property

    @abc.abstractmethod
    def _backup_existing_database(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _create_database_engine(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _revert_to_backup_database(self):
        raise NotImplementedError

    def _cleanup(self):
        pass

    def _find_parsers(self):
        return find_parsers()

    def _create_progressbar(self, desc):
        widgets = [desc, ' ' * 4, progressbar.Bar(), progressbar.Percentage()]
        return progressbar.ProgressBar(max_value=100, widgets=widgets)

    def _process_parser(self, engine, name, parser):
        bar = self._create_progressbar(name)
        parser.add_reporthook(bar.update)

        try:
            bar.start()

            for prop in parser:
                func = self._propfuncs[type(prop)]
                func(engine, prop)

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
                self._process_parser(engine, name, parser)
                logger.info('Populated {0}'.format(name))

        except:
            reverted = self._revert_to_backup_database()
            if reverted:
                logger.info('Reverted to previous database')
            raise

        self._cleanup()

    def _get_element(self, engine, element):
        atomic_number = element.atomic_number

        tbl = table.element
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.atomic_number == atomic_number)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _get_atomic_shell(self, engine, atomic_shell):
        principal_quantum_number = atomic_shell.principal_quantum_number

        tbl = table.atomic_shell
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.principal_quantum_number == principal_quantum_number)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _get_atomic_subshell(self, engine, atomic_subshell):
        atomic_shell_id = self._require_atomic_shell(engine, atomic_subshell.atomic_shell)
        azimuthal_quantum_number = atomic_subshell.azimuthal_quantum_number
        total_angular_momentum_nominator = atomic_subshell.total_angular_momentum_nominator

        tbl = table.atomic_subshell
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.atomic_shell_id == atomic_shell_id,
                                         tbl.c.azimuthal_quantum_number == azimuthal_quantum_number,
                                         tbl.c.total_angular_momentum_nominator == total_angular_momentum_nominator))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _get_transition(self, engine, transition):
        source_subshell_id = \
            self._require_atomic_subshell(engine, transition.source_subshell)
        destination_subshell_id = \
            self._require_atomic_subshell(engine, transition.destination_subshell)
        if transition.secondary_destination_subshell:
            secondary_destination_subshell_id = \
                self._require_atomic_subshell(engine, transition.secondary_destination_subshell)
        else:
            secondary_destination_subshell_id = None

        tbl = table.transition
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.source_subshell_id == source_subshell_id,
                                         tbl.c.destination_subshell_id == destination_subshell_id,
                                         tbl.c.secondary_destination_subshell_id == secondary_destination_subshell_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _get_transitionset(self, engine, transitionset):
        transition_ids = set()
        for transition in transitionset.transitions:
            transition_id = self._require_transition(engine, transition)
            transition_ids.add(transition_id)

        table.transitionset.create(engine, checkfirst=True)
        table.transitionset_association.create(engine, checkfirst=True)

        tbl = table.transitionset_association
        conditions = []
        for transition_id in transition_ids:
            conditions.append(tbl.c.transition_id == transition_id)

        command = sql.select([table.transitionset_association])
        command = command.where(sql.or_(*conditions))

        with engine.begin() as conn:
            result = conn.execute(command)
            rows = result.fetchall()
            if rows and cbook.allequal(map(itemgetter(0), rows)):
                return rows[0]['transitionset_id']

        raise NotFound

    def _get_language(self, engine, language):
        code = language.code

        tbl = table.language
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.code == code)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _get_notation(self, engine, notation):
        name = notation.name

        tbl = table.notation
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.name == name)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _get_reference(self, engine, reference):
        bibtexkey = reference.bibtexkey

        tbl = table.reference
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.bibtexkey == bibtexkey)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        raise NotFound

    def _insert_element(self, engine, element):
        atomic_number = element.atomic_number

        tbl = table.element
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(atomic_number=atomic_number)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _insert_atomic_shell(self, engine, atomic_shell):
        principal_quantum_number = atomic_shell.principal_quantum_number

        tbl = table.atomic_shell
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(principal_quantum_number=principal_quantum_number)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _insert_atomic_subshell(self, engine, atomic_subshell):
        atomic_shell_id = self._require_atomic_shell(engine, atomic_subshell.atomic_shell)
        azimuthal_quantum_number = atomic_subshell.azimuthal_quantum_number
        total_angular_momentum_nominator = atomic_subshell.total_angular_momentum_nominator

        tbl = table.atomic_subshell
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(atomic_shell_id=atomic_shell_id,
                                 azimuthal_quantum_number=azimuthal_quantum_number,
                                 total_angular_momentum_nominator=total_angular_momentum_nominator)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _insert_transition(self, engine, transition):
        source_subshell_id = \
            self._require_atomic_subshell(engine, transition.source_subshell)
        destination_subshell_id = \
            self._require_atomic_subshell(engine, transition.destination_subshell)
        if transition.secondary_destination_subshell:
            secondary_destination_subshell_id = \
                self._require_atomic_subshell(engine, transition.secondary_destination_subshell)
        else:
            secondary_destination_subshell_id = None

        tbl = table.transition
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(source_subshell_id=source_subshell_id,
                                 destination_subshell_id=destination_subshell_id,
                                 secondary_destination_subshell_id=secondary_destination_subshell_id)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _insert_transitionset(self, engine, transitionset):
        transition_ids = set()
        for transition in transitionset.transitions:
            transition_id = self._require_transition(engine, transition)
            transition_ids.add(transition_id)

        table.transitionset.create(engine, checkfirst=True)
        table.transitionset_association.create(engine, checkfirst=True)

        # Create empty transitionset row
        command = sql.insert(table.transitionset)
        with engine.begin() as conn:
            result = conn.execute(command)
            transitionset_id = result.inserted_primary_key[0]

        # Populate association table
        values = []
        for transition_id in transition_ids:
            values.append({'transitionset_id': transitionset_id,
                           'transition_id': transition_id})

        command = sql.insert(table.transitionset_association)
        command = command.values(values)
        with engine.begin() as conn:
            conn.execute(command)

        return transitionset_id

    def _insert_language(self, engine, language):
        code = language.code

        tbl = table.language
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(code=code)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _insert_notation(self, engine, notation):
        name = notation.name

        tbl = table.notation
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(name=name)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _insert_reference(self, engine, reference):
        tbl = table.reference
        tbl.create(engine, checkfirst=True)

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
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_element(self, engine, element):
        try:
            return self._get_element(engine, element)
        except NotFound:
            return self._insert_element(engine, element)

    def _require_atomic_shell(self, engine, atomic_shell):
        try:
            return self._get_atomic_shell(engine, atomic_shell)
        except NotFound:
            return self._insert_atomic_shell(engine, atomic_shell)

    def _require_atomic_subshell(self, engine, atomic_subshell):
        try:
            return self._get_atomic_subshell(engine, atomic_subshell)
        except NotFound:
            return self._insert_atomic_subshell(engine, atomic_subshell)

    def _require_transition(self, engine, transition):
        try:
            return self._get_transition(engine, transition)
        except NotFound:
            return self._insert_transition(engine, transition)

    def _require_transitionset(self, engine, transitionset):
        try:
            return self._get_transitionset(engine, transitionset)
        except NotFound:
            return self._insert_transitionset(engine, transitionset)

    def _require_language(self, engine, language):
        try:
            return self._get_language(engine, language)
        except NotFound:
            return self._insert_language(engine, language)

    def _require_notation(self, engine, notation):
        try:
            return self._get_notation(engine, notation)
        except NotFound:
            return self._insert_notation(engine, notation)

    def _require_reference(self, engine, reference):
        try:
            return self._get_reference(engine, reference)
        except NotFound:
            return self._insert_reference(engine, reference)

    def _add_element_symbol_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        symbol = prop.symbol

        tbl = table.element_symbol
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 symbol=symbol)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_element_name_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        language_id = self._require_language(engine, prop.language)
        name = prop.name

        tbl = table.element_name
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 language_id=language_id,
                                 name=name)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_element_atomic_weight_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        value = prop.value

        tbl = table.element_atomic_weight
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 value=value)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_element_mass_density_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        value_kg_per_m3 = prop.value_kg_per_m3

        tbl = table.element_mass_density
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 value_kg_per_m3=value_kg_per_m3)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_atomic_shell_notation_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        atomic_shell_id = self._require_atomic_shell(engine, prop.atomic_shell)
        notation_id = self._require_notation(engine, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.atomic_shell_notation
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 atomic_shell_id=atomic_shell_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_atomic_subshell_notation_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        atomic_subshell_id = self._require_atomic_subshell(engine, prop.atomic_subshell)
        notation_id = self._require_notation(engine, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.atomic_subshell_notation
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_atomic_subshell_binding_energy_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(engine, prop.atomic_subshell)
        value_eV = prop.value_eV

        tbl = table.atomic_subshell_binding_energy
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value_eV=value_eV)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_atomic_subshell_radiative_width_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(engine, prop.atomic_subshell)
        value_eV = prop.value_eV

        tbl = table.atomic_subshell_radiative_width
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value_eV=value_eV)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_atomic_subshell_nonradiative_width_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(engine, prop.atomic_subshell)
        value_eV = prop.value_eV

        tbl = table.atomic_subshell_nonradiative_width
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value_eV=value_eV)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_atomic_subshell_occupancy_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        atomic_subshell_id = self._require_atomic_subshell(engine, prop.atomic_subshell)
        value = prop.value

        tbl = table.atomic_subshell_occupancy
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 atomic_subshell_id=atomic_subshell_id,
                                 value=value)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_transition_notation_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        transition_id = self._require_transition(engine, prop.transition)
        notation_id = self._require_notation(engine, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.transition_notation
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 transition_id=transition_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_transition_energy_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        transition_id = self._require_transition(engine, prop.transition)
        value_eV = prop.value_eV

        tbl = table.transition_energy
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transition_id=transition_id,
                                 value_eV=value_eV)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_transition_propability_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        transition_id = self._require_transition(engine, prop.transition)
        value = prop.value

        tbl = table.transition_probability
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transition_id=transition_id,
                                 value=value)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_transitionset_notation_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        transitionset_id = self._require_transitionset(engine, prop.transitionset)
        notation_id = self._require_notation(engine, prop.notation)
        ascii = prop.ascii
        utf16 = prop.utf16
        html = prop.html
        latex = prop.latex

        tbl = table.transitionset_notation
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 transitionset_id=transitionset_id,
                                 notation_id=notation_id,
                                 ascii=ascii,
                                 utf16=utf16,
                                 html=html,
                                 latex=latex)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _add_transitionset_energy_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        transitionset_id = self._require_transitionset(engine, prop.transitionset)
        value_eV = prop.value_eV

        tbl = table.transitionset_energy
        tbl.create(engine, checkfirst=True)

        command = sql.insert(tbl)
        command = command.values(reference_id=reference_id,
                                 element_id=element_id,
                                 transitionset_id=transitionset_id,
                                 value_eV=value_eV)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

class SqliteDatabaseBuilder(_DatabaseBuilder):

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
        return create_engine('sqlite:///' + self.filepath)

    @property
    def filepath(self):
        return self._filepath

def main():
    parser = argparse.ArgumentParser(description='Build the SQL database')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show debug information')

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(level)
    logging.basicConfig()

    builder = SqliteDatabaseBuilder()
    builder.build()

if __name__ == '__main__':
    main()
