""""""

# Standard library modules.
import os
import logging
logger = logging.getLogger(__name__)
import abc
import argparse
import shutil

# Third party modules.
from sqlalchemy import create_engine

import pkg_resources

import six

# Local modules.
from pyxray.sql.model import Base

# Globals and constants variables.

_ENTRY_POINT_GROUP = 'pyxray.sql.mapping'

@six.add_metaclass(abc.ABCMeta)
class _DatabaseBuilder:

    def __init__(self, purge=False):
        self._purge = purge

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

    def _find_mappers(self):
        mappers = []
        for entry_point in pkg_resources.iter_entry_points(_ENTRY_POINT_GROUP):
            name = entry_point.name
            mapper = entry_point.load()
            mappers.append((name, mapper))
        return mappers

    def _organize_mappers(self, mappers):
        mappers2 = []
        for name, mapper in mappers:
            if not mapper.dependencies:
                mappers2.insert(0, (name, mapper))
            else:
                mappers2.append((name, mapper))
        return mappers2

    def purge_database(self, engine):
        Base.metadata.drop_all(engine) #@UndefinedVariable

    def build(self):
        mappers = self._find_mappers()
        mappers = self._organize_mappers(mappers)
        logger.info('Found {:d} mappers'.format(len(mappers)))

        backuped = self._backup_existing_database()
        if backuped:
            logger.info('Backup existing database')

        try:
            engine = self._create_database_engine()
            logger.info('Created database engine')

            if self.purge:
                self.purge_database(engine)
                logger.info('Purged database')

            for name, mapper in mappers:
                mapper.populate(engine)
                logger.info('Populated {0}'.format(name))

        except:
            reverted = self._revert_to_backup_database()
            if reverted:
                logger.info('Reverted to previous database')
            raise

        self._cleanup()

    @property
    def purge(self):
        return self._purge

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

    builder = SqliteDatabaseBuilder(purge=False)
    builder.build()

if __name__ == '__main__':
    main()
