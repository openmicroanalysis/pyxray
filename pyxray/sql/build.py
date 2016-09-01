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

# Local modules.
from pyxray.parser.parser import find_parsers
import pyxray.sql.table as table
import pyxray.property as props

# Globals and constants variables.

class _DatabaseBuilder(metaclass=abc.ABCMeta):

    def __init__(self, purge=False):
        self.purge = purge

        self._propfuncs = {}
        self._propfuncs[props.ElementSymbol] = self._add_element_symbol_property
        self._propfuncs[props.ElementName] = self._add_element_name_property
        self._propfuncs[props.ElementAtomicWeight] = self._add_element_atomic_weight_property
        self._propfuncs[props.ElementMassDensity] = self._add_element_mass_density_property
        self._propfuncs[props.AtomicShellNotation] = self._add_atomic_shell_notation_property
        self._propfuncs[props.AtomicSubshellNotation] = self._add_atomic_subshell_notation_property
        self._propfuncs[props.TransitionNotation] = self._add_transition_notation_property

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

    def _process_parser(self, engine, parser):
        for prop in parser:
            func = self._propfuncs[type(prop)]
            func(engine, prop)

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

            if self.purge:
                self.purge_database(engine)
                logger.info('Purged database')

            for name, parser in parsers:
                self._process_parser(engine, parser)
                logger.info('Populated {0}'.format(name))

        except:
            reverted = self._revert_to_backup_database()
            if reverted:
                logger.info('Reverted to previous database')
            raise

        self._cleanup()

    def _require_element(self, engine, element):
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

        command = sql.insert(tbl)
        command = command.values(atomic_number=atomic_number)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_atomic_shell(self, engine, atomic_shell):
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

        command = sql.insert(tbl)
        command = command.values(principal_quantum_number=principal_quantum_number)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_atomic_subshell(self, engine, atomic_subshell):
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

        command = sql.insert(tbl)
        command = command.values(atomic_shell_id=atomic_shell_id,
                                 azimuthal_quantum_number=azimuthal_quantum_number,
                                 total_angular_momentum_nominator=total_angular_momentum_nominator)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_transition(self, engine, transition):
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

        command = sql.insert(tbl)
        command = command.values(source_subshell_id=source_subshell_id,
                                 destination_subshell_id=destination_subshell_id,
                                 secondary_destination_subshell_id=secondary_destination_subshell_id)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_transitionset(self, engine, transitionset):
        transition_ids = set()
        for transition in transitionset.transition:
            transition_id = self._require_transition(engine, transition)
            transition_ids.add(transition_id)

#        tbl = table.transition
#        tbl.create(engine, checkfirst=True)
#
#        command = sql.select([tbl])
#        command = command.where(sql.and_(tbl.c.source_subshell_id == source_subshell_id,
#                                         tbl.c.destination_subshell_id == destination_subshell_id,
#                                         tbl.c.second_destination_subshell_id == second_destination_subshell_id))
#        with engine.begin() as conn:
#            result = conn.execute(command)
#            row = result.first()
#            if row is not None:
#                return row['id']
#
#        command = sql.insert(tbl)
#        command = command.values(source_subshell_id=source_subshell_id,
#                                 destination_subshell_id=destination_subshell_id,
#                                 second_destination_subshell_id=second_destination_subshell_id)
#        with engine.begin() as conn:
#            result = conn.execute(command)
#            return result.inserted_primary_key[0]

    def _require_language(self, engine, language):
        tbl = table.language
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.code == language.code)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        command = sql.insert(tbl)
        command = command.values(code=language.code)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_notation(self, engine, notation):
        tbl = table.notation
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.name == notation.name)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

        command = sql.insert(tbl)
        command = command.values(name=notation.name)
        with engine.begin() as conn:
            result = conn.execute(command)
            return result.inserted_primary_key[0]

    def _require_reference(self, engine, reference):
        tbl = table.reference
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(tbl.c.bibtexkey == reference.bibtexkey)
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

    def _add_element_symbol_property(self, engine, prop):
        reference_id = self._require_reference(engine, prop.reference)
        element_id = self._require_element(engine, prop.element)
        symbol = prop.symbol

        tbl = table.element_symbol
        tbl.create(engine, checkfirst=True)

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.element_id == element_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.element_id == element_id,
                                         tbl.c.language_id == language_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.element_id == element_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.element_id == element_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.atomic_shell_id == atomic_shell_id,
                                         tbl.c.notation_id == notation_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.atomic_subshell_id == atomic_subshell_id,
                                         tbl.c.notation_id == notation_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

        command = sql.select([tbl])
        command = command.where(sql.and_(tbl.c.reference_id == reference_id,
                                         tbl.c.transition_id == transition_id,
                                         tbl.c.notation_id == notation_id))
        with engine.begin() as conn:
            result = conn.execute(command)
            row = result.first()
            if row is not None:
                return row['id']

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

class SqliteDatabaseBuilder(_DatabaseBuilder):

    def __init__(self, filepath=None, purge=False):
        super().__init__(purge)
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

    builder = SqliteDatabaseBuilder(purge=True)
    builder.build()

if __name__ == '__main__':
    main()
