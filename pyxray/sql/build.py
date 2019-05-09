"""
Build the SQL database from the registered parsers.
"""

# Standard library modules.
import dataclasses
import logging

# Third party modules.
import tqdm

# Local modules.
from pyxray.parser.base import find_parsers
from pyxray.sql.base import SqlBase

# Globals and constants variables.
logger = logging.getLogger(__name__)

class SqlDatabaseBuilder(SqlBase):

    def _convert_dataclass_to_params(self, dataclass):
        params = {}
        for field in dataclasses.fields(dataclass):
            name = field.name
            value = getattr(dataclass, name)

            if dataclasses.is_dataclass(value):
                row_id = self.insert(value, check_duplicate=True)
                params[name + '_id'] = row_id
            else:
                params[name] = value

        return params

    def insert(self, dataclass, check_duplicate=False):
        """
        Inserts a dataclass instance.

        Args:
            dataclass (dataclasses.dataclass): instance
            check_duplicate (bool): whether to check if the dataclass already
                contains a matching row

        Returns:
            int: row of the dataclass instance in its table
        """
        # Check if already exists
        if check_duplicate:
            row_id = self._get_row(dataclass)
            if row_id is not None:
                return row_id

        # Create insert statement
        table = self.require_table(dataclass)
        params = self._convert_dataclass_to_params(dataclass)
        ins = table.insert().values(**params)

        logger.debug('Insert in "{}": {!r}'.format(table.name, params))

        # Insert
        with self.engine.begin() as conn:
            result = conn.execute(ins)
            return result.inserted_primary_key[0]

    def insert_many(self, list_dataclass):
        clasz = type(list_dataclass[0])

        list_params = []
        for dataclass in list_dataclass:
            if type(dataclass) != clasz:
                raise ValueError('All dataclasses do not have the same type')

            params = self._convert_dataclass_to_params(dataclass)
            list_params.append(params)

        table = self.require_table(clasz)

        # Insert
        with self.engine.begin() as conn:
            conn.execute(table.insert(), list_params)

    def _find_parsers(self):
        return find_parsers()

    def build(self):
        """
        Find all parsers and insert their properties in the database.
        """
        parsers = self._find_parsers()
        logger.info('Found {:d} parsers'.format(len(parsers)))

        for name, parser in tqdm.tqdm(parsers, desc='Building database'):
            buffer = {}

            for prop in tqdm.tqdm(parser, desc='Processing {}'.format(name)):
                buffer.setdefault(type(prop), []).append(prop)

            for list_dataclass in tqdm.tqdm(buffer.values(), desc='Inserting {}'.format(name)):
                self.insert_many(list_dataclass)


