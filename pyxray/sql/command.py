"""
Base SQL engine
"""

# Standard library modules.
import functools
import itertools

# Third party modules.

# Local modules.

# Globals and constants variables.

def take(n, iterable):
    """Return first n items of the iterable as a list

        >>> take(3, range(10))
        [0, 1, 2]
        >>> take(5, range(3))
        [0, 1, 2]

    Effectively a short replacement for ``next`` based iterator consumption
    when you want more than one item, but less than the whole iterator.
    
    Taken from more_itertools
    
    """
    return list(itertools.islice(iterable, n))

def chunked(iterable, n):
    """Break an iterable into lists of a given length::

        >>> list(chunked([1, 2, 3, 4, 5, 6, 7], 3))
        [[1, 2, 3], [4, 5, 6], [7]]

    If the length of ``iterable`` is not evenly divisible by ``n``, the last
    returned list will be shorter.

    This is useful for splitting up a computation on a large number of keys
    into batches, to be pickled and sent off to worker processes. One example
    is operations on rows in MySQL, which does not implement server-side
    cursors properly and would otherwise load the entire dataset into RAM on
    the client.
    
    Taken from more_itertools

    """
    return iter(functools.partial(take, n, iter(iterable)), [])

class SelectBuilder:

    def __init__(self):
        self.distinct = False
        self.selects = []
        self.froms = []
        self.joins = []
        self.wheres = []
        self.orderbys = []

    def set_distinct(self, distinct):
        self.distinct = distinct

    def add_select(self, table, column):
        self.selects.append((table, column))

    def add_from(self, table):
        self.froms.append(table)

    def add_join(self, table1, column1, table2, column2, alias1=None):
        self.joins.append((table1, column1, table2, column2, alias1))

    def add_where(self, table, column, operator, variable, *args):
        where = [(table, column, operator, variable)]
        for table, column, operator, variable in chunked(args, 4):
            where.append((table, column, operator, variable))
        self.wheres.append(where)

    def add_orderby(self, table, column, order='ASC'):
        self.orderbys.append((table, column, order))

    def build(self):
        sql = []
        params = {}
        variable_index = 0

        # Select
        sql += ['SELECT ' + \
                ('DISTINCT ' if self.distinct else '') + \
                ', '.join('{}.{}'.format(t, c) for t, c in self.selects)]

        # From
        tables = [t1 for t1, _, t2, _, a1 in self.joins if not a1 and t1 != t2]
        sql += ['FROM ' + ', '.join(set(self.froms) - set(tables))]

        # Join
        for t1, c1, t2, c2, a1 in self.joins:
            if t1 == t2 and a1 is None:
                continue

            if a1:
                fmt = 'JOIN {0} AS {4} ON {4}.{1} = {2}.{3}'
            else:
                fmt = 'JOIN {0} ON {0}.{1} = {2}.{3}'
            sql += [fmt.format(t1, c1, t2, c2, a1)]

        # Where
        subsql = []
        for conditions in self.wheres:
            subsubsql = []
            for t, c, o, vs in conditions:
                if o.lower() == 'in':
                    values = []
                    for v in vs:
                        key = 'v{:d}'.format(variable_index)
                        values.append(key)
                        params[key] = v
                        variable_index += 1

                    subsubsql += ['{}.{} {} ('.format(t, c, o) + \
                                  ', '.join(':{}'.format(v) for v in values) + \
                                  ')']
                else:
                    key = 'v{:d}'.format(variable_index)
                    params[key] = vs
                    variable_index += 1
                    subsubsql += ['{}.{} {} :{}'.format(t, c, o, key)]

            subsql += ['(' + ' OR '.join(subsubsql) + ')']

        if subsql:
            sql += ['WHERE ' + ' AND '.join(subsql)]

        # Order by
        if self.orderbys:
            sql += ['ORDER BY ' + \
                    ', '.join('{}.{} {}'.format(t, c, o)
                              for t, c, o in self.orderbys)]

        return '\n'.join(sql), params

class CreateTableBuilder:

    def __init__(self, table):
        self.table = table
        self.columns = []
        self.keys = []

    def add_primarykey_column(self, column):
        self.add_integer_column(column, nullable=False)
        self.keys.append('PRIMARY KEY ({})'.format(column))

    def add_foreignkey_column(self, column, reftable, refcolumn):
        self.add_integer_column(column, nullable=False)
        self.keys.append('FOREIGN KEY ({}) REFERENCES {} ({})'
                         .format(column, reftable, refcolumn))

    def add_integer_column(self, column, nullable=True):
        sql = '{} INTEGER'.format(column)
        if not nullable:
            sql += ' NOT NULL'
        self.columns.append(sql)

    def add_string_column(self, column, length=None, nullable=True, casesensitive=True):
        sql = '{} VARCHAR'.format(column)
        if length:
            sql += '({})'.format(length)
        if not casesensitive:
            sql += ' COLLATE NOCASE'
        if not nullable:
            sql += ' NOT NULL'
        self.columns.append(sql)

    def add_float_column(self, column, nullable=True):
        sql = '{} FLOAT'.format(column)
        if not nullable:
            sql += ' NOT NULL'
        self.columns.append(sql)

    def build(self):
        sql = 'CREATE TABLE IF NOT EXISTS {} (\n'.format(self.table)
        sql += ',\n'.join(self.columns + self.keys)
        sql += ')'
        return sql

class InsertBuilder:

    def __init__(self, table):
        self.table = table
        self.columns = []
        self.variables = []

    def add_column(self, column, variable):
        self.columns.append(column)
        self.variables.append(variable)

    def build(self):
        params = {}

        values = []
        variable_index = 0
        for v in self.variables:
            key = 'v{:d}'.format(variable_index)
            values.append(key)
            params[key] = v
            variable_index += 1

        sql = 'INSERT INTO {}'.format(self.table)
        sql += ' ({})'.format(','.join(self.columns))
        sql += '\n'
        sql += 'VALUES ({})'.format(','.join(':{}'.format(v) for v in values))

        return sql, params
