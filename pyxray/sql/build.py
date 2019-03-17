"""
Build the SQL database from the registered parsers.
"""

# Standard library modules.
import dataclasses

# Third party modules.
import tqdm

from loguru import logger

# Local modules.
from pyxray.parser.parser import find_parsers
from pyxray.sql.base import SqlBase

# Globals and constants variables.

class SqlDatabaseBuilder(SqlBase):

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
        params = {}
        for field in dataclasses.fields(dataclass):
            name = field.name
            value = getattr(dataclass, name)

            if dataclasses.is_dataclass(value):
                row_id = self.insert(value, check_duplicate=True)
                params[name + '_id'] = row_id
            else:
                params[name] = value

        table = self.require_table(dataclass)
        ins = table.insert().values(**params)

        logger.debug('Insert in "{}": {!r}', table.name, params)

        # Insert
        with self.engine.begin() as conn:
            result = conn.execute(ins)
            return result.inserted_primary_key[0]

    def _find_parsers(self):
        return find_parsers()

    def build(self):
        """
        Find all parsers and insert their properties in the database.
        """
        parsers = self._find_parsers()
        logger.info('Found {:d} parsers'.format(len(parsers)))

        for name, parser in tqdm.tqdm(parsers, desc='Building database'):
            for prop in tqdm.tqdm(parser, desc='Processing {}'.format(name)):
                self.insert(prop)

