"""
Base SQL.
"""

# Standard library modules.
import re
import dataclasses
import inspect
import logging

# Third party modules.
import sqlalchemy.sql

# Local modules.

# Globals and constants variables.
logger = logging.getLogger(__name__)

def camelcase_to_words(text):
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', text)

class SqlBase:

    FIELDS_TO_SQLTYPE = {int: sqlalchemy.Integer,
                         float: sqlalchemy.Float,
                         str: sqlalchemy.String}

    def __init__(self, engine):
        self.engine = engine
        self.metadata = sqlalchemy.MetaData()

    def _get_table_name(self, dataclass):
        """
        Creates a table name from a dataclass class or instance.

        Args:
            dataclass (dataclasses.dataclass): class or instance

        Returns:
            str: name of table
        """
        if not inspect.isclass(dataclass):
            dataclass = type(dataclass)
        return '_'.join(camelcase_to_words(dataclass.__name__).split()).lower()

    def _create_table(self, table_name, dataclass):
        """
        Creates a table in the database.

        Args:
            table_name (str): name of table
            dataclass (dataclasses.dataclass): class or instance

        Returns:
            :class:`sqlalchemy.Table`: table instance
        """
        columns = [sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True)]

        for field in dataclasses.fields(dataclass):
            if dataclasses.is_dataclass(field.type):
                subtable = self.require_table(field.type)
                column = sqlalchemy.Column(field.name + '_id', None, sqlalchemy.ForeignKey(subtable.name + '.id'))

            elif field.type in self.FIELDS_TO_SQLTYPE:
                nullable = field.default is None

                if field.type == str and (field.name.startswith('key') or field.name.endswith('key')):
                    columntype = sqlalchemy.String(collation='NOCASE')
                else:
                    columntype = self.FIELDS_TO_SQLTYPE[field.type]

                column = sqlalchemy.Column(field.name, columntype, nullable=nullable)

            else:
                raise ValueError('Unknown field: {}'.format(field.type))

            columns.append(column)

        table = sqlalchemy.Table(table_name, self.metadata, *columns)

        self.metadata.create_all(self.engine, tables=[table])
        logger.debug('Create table "{}"'.format(table_name))

        return table

    def require_table(self, dataclass):
        """
        Returns the table for the specified dataclass.
        If no table exists, it is created first.

        Args:
            dataclass (dataclasses.dataclass): class or instance

        Returns:
            :class:`sqlalchemy.Table`: table instance
        """
        table_name = self._get_table_name(dataclass)
        table = self.metadata.tables.get(table_name)

        if table is None:
            table = self._create_table(table_name, dataclass)

        return table

    def _get_row(self, dataclass):
        """
        Returns the row of the dataclass if it exists.
        If not, ``None`` is returned

        Args:
            dataclass (dataclasses.dataclass): instance

        Returns:
            int: row of the dataclass instance in its table, ``None`` if not found
        """
        table = self.require_table(dataclass)

        clauses = []
        for field in dataclasses.fields(dataclass):
            name = field.name
            value = getattr(dataclass, name)

            if dataclasses.is_dataclass(field.type):
                row_id = self._get_row(value)
                clause = table.c[name + '_id'] == row_id

            else:
                clause = table.c[name] == value

            clauses.append(clause)

        statement = sqlalchemy.sql.select([table.c.id]).where(sqlalchemy.sql.and_(*clauses))

        with self.engine.begin() as conn:
            return conn.execute(statement).scalar()
