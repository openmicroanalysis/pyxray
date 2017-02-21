"""
Base SQL engine
"""

# Standard library modules.
import collections
import functools
import itertools

# Third party modules.
import sqlalchemy.sql as sql

# Local modules.
from pyxray.descriptor import \
    (Element, Language, Reference, Notation, AtomicShell, AtomicSubshell,
     XrayTransition, XrayTransitionSet)
import pyxray.sql.table as table
from pyxray.base import NotFound

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
        self.selects = []
        self.froms = []
        self.joins = []
        self.wheres = []
        self.orderbys = []

    def add_select(self, table, column):
        self.selects.append((table, column))

    def add_from(self, table):
        self.froms.append(table)

    def add_join(self, table1, column1, table2, column2, alias1=None):
        self.joins.append((table1, column1, table2, column2, alias1))

    def add_where(self, table, column, variable, *args):
        where = [(table, column, variable)]
        for table, column, variable in chunked(args, 3):
            where.append((table, column, variable))
        self.wheres.append(where)

    def add_orderby(self, table, column, order='ASC'):
        self.orderbys.append((table, column, order))

    def build(self):
        sql = []

        # Select
        sql += ['SELECT ' + ', '.join('{}.{}'.format(table, column)
                                      for table, column in self.selects)]

        # From
        tables = [table1 for table1, _, table2, _, alias1 in self.joins
                  if not alias1 and table1 != table2]
        sql += ['FROM ' + ', '.join(set(self.froms) - set(tables))]

        # Join
        for table1, column1, table2, column2, alias1 in self.joins:
            if table1 == table2:
                continue

            if alias1:
                fmt = 'JOIN {0} AS {4} ON {4}.{1} = {2}.{3}'
            else:
                fmt = 'JOIN {0} ON {0}.{1} = {2}.{3}'
            sql += [fmt.format(table1, column1, table2, column2, alias1)]

        # Where
        if self.wheres:
            subsql = []
            for conditions in self.wheres:
                subsql += ['(' + \
                           ' OR '.join('{}.{} = :{}'.format(table, column, variable)
                                       for table, column, variable in conditions) + \
                           ')']

            sql += ['WHERE ' + ' AND '.join(subsql)]

        # Order by
        if self.orderbys:
            sql += ['ORDER BY ' + \
                    ', '.join('{}.{} {}'.format(table, column, order)
                              for table, column, order in self.orderbys)]

        return '\n'.join(sql)

class SqlEngineDatabaseMixin:

    def _create_sql(self, select, joins, wheres):
        return '\n'.join([select, '\n'.join(joins), '\n'.join(wheres)])

    def _retrieve_first(self, conn, command, exc=None):
        result = conn.execute(command)
        row = result.first()
        if row is not None:
            return row[0]

        if exc:
            raise exc

        return None

    def _get_element_id(self, conn, element):
        if isinstance(element, str):
            if len(element) <= 2:
                tbl = table.element_symbol
                tbl.create(conn, checkfirst=True)
                command = sql.select([tbl.c.element_id])
                command = command.where(tbl.c.symbol == element)
                out = self._retrieve_first(conn, command)
                if out is not None:
                    return out

            # Outside if because name of an element could also be of length 2,
            # but not a symbol
            tbl = table.element_name
            tbl.create(conn, checkfirst=True)
            command = sql.select([tbl.c.element_id])
            command = command.where(tbl.c.name == element)
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        atomic_number = 0
        if isinstance(element, Element):
            atomic_number = element.atomic_number

        elif isinstance(element, int):
            atomic_number = element

        elif hasattr(element, 'atomic_number'):
            atomic_number = element.atomic_number

        elif hasattr(element, 'z'):
            atomic_number = element.z

        if atomic_number > 0 :
            tbl = table.element
            tbl.create(conn, checkfirst=True)
            command = sql.select([tbl.c.id])
            command = command.where(tbl.c.atomic_number == atomic_number)
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        raise NotFound('Unknown element: {0}'.format(element))

    def _get_element(self, conn, element_id):
        tbl = table.element
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.atomic_number])
        command = command.where(tbl.c.id == element_id)
        atomic_number = \
            self._retrieve_first(conn, command, NotFound('No element found'))

        return Element(atomic_number)

    def _get_atomic_shell_id(self, conn, atomic_shell):
        if isinstance(atomic_shell, str):
            tbl = table.atomic_shell_notation
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.atomic_shell_id])
            command = command.where(sql.or_(tbl.c.ascii == atomic_shell,
                                            tbl.c.utf16 == atomic_shell))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        principal_quantum_number = 0
        if isinstance(atomic_shell, AtomicShell):
            principal_quantum_number = atomic_shell.principal_quantum_number

        elif isinstance(atomic_shell, int):
            principal_quantum_number = atomic_shell

        if principal_quantum_number > 0:
            tbl = table.atomic_shell
            tbl.create(conn, checkfirst=True)
            command = sql.select([tbl.c.id])
            command = command.where(tbl.c.principal_quantum_number == principal_quantum_number)
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        raise NotFound('Unknown atomic shell: {0}'.format(atomic_shell))

    def _get_atomic_shell(self, conn, atomic_shell_id):
        tbl = table.atomic_shell
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.principal_quantum_number])
        command = command.where(tbl.c.id == atomic_shell_id)
        principal_quantum_number = \
            self._retrieve_first(conn, command, NotFound('No atomic shell found'))

        return AtomicShell(principal_quantum_number)

    def _get_atomic_subshell_id(self, conn, atomic_subshell):
        if isinstance(atomic_subshell, str):
            tbl = table.atomic_subshell_notation
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.atomic_subshell_id])
            command = command.where(sql.or_(tbl.c.ascii == atomic_subshell,
                                            tbl.c.utf16 == atomic_subshell))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        principal_quantum_number = 0
        azimuthal_quantum_number = -1
        total_angular_momentum_nominator = 0
        if isinstance(atomic_subshell, AtomicSubshell):
            principal_quantum_number = atomic_subshell.atomic_shell.principal_quantum_number
            azimuthal_quantum_number = atomic_subshell.azimuthal_quantum_number
            total_angular_momentum_nominator = atomic_subshell.total_angular_momentum_nominator

        elif isinstance(atomic_subshell, collections.Sequence) and \
                len(atomic_subshell) == 3:
            principal_quantum_number = atomic_subshell[0]
            azimuthal_quantum_number = atomic_subshell[1]
            total_angular_momentum_nominator = atomic_subshell[2]

        if principal_quantum_number > 0 and \
                azimuthal_quantum_number >= 0 and \
                total_angular_momentum_nominator > 0:
            atomic_shell_id = self._get_atomic_shell_id(conn, principal_quantum_number)

            tbl = table.atomic_subshell
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.id])
            command = command.where(tbl.c.atomic_shell_id == atomic_shell_id)
            command = command.where(tbl.c.azimuthal_quantum_number == azimuthal_quantum_number)
            command = command.where(tbl.c.total_angular_momentum_nominator == total_angular_momentum_nominator)
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        raise NotFound('Unknown atomic subshell: {0}'.format(atomic_subshell))

    def _get_atomic_subshell(self, conn, atomic_subshell_id):
        tbl = table.atomic_subshell
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.atomic_shell_id,
                              tbl.c.azimuthal_quantum_number,
                              tbl.c.total_angular_momentum_nominator])
        command = command.where(tbl.c.id == atomic_subshell_id)
        result = conn.execute(command)
        row = result.first()
        if row is None:
            raise NotFound('No atomic subshell found')
        atomic_shell_id, azimuthal_quantum_number, total_angular_momentum_nominator = row

        atomic_shell = self._get_atomic_shell(conn, atomic_shell_id)

        return AtomicSubshell(atomic_shell,
                              azimuthal_quantum_number,
                              total_angular_momentum_nominator)

    def _get_xray_transition_id(self, conn, xraytransition):
        if isinstance(xraytransition, str):
            tbl = table.xray_transition_notation
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.xray_transition_id])
            command = command.where(sql.or_(tbl.c.ascii == xraytransition,
                                            tbl.c.utf16 == xraytransition))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        source_subshell = None
        destination_subshell = None
        if isinstance(xraytransition, XrayTransition):
            source_subshell = xraytransition.source_subshell
            destination_subshell = xraytransition.destination_subshell
        elif isinstance(xraytransition, collections.Sequence) and \
                len(xraytransition) == 2:
            source_subshell = xraytransition[0]
            destination_subshell = xraytransition[1]

        if source_subshell is not None and \
                destination_subshell is not None:
            source_subshell_id = self._get_atomic_subshell_id(conn, source_subshell)
            destination_subshell_id = self._get_atomic_subshell_id(conn, destination_subshell)

            tbl = table.xray_transition
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.id])
            command = command.where(sql.and_(tbl.c.source_subshell_id == source_subshell_id,
                                             tbl.c.destination_subshell_id == destination_subshell_id))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        raise NotFound('Unknown transition: {0}'.format(xraytransition))

    def _get_xray_transition(self, conn, xray_transition_id):
        tbl = table.xray_transition
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.source_subshell_id,
                              tbl.c.destination_subshell_id])
        command = command.where(tbl.c.id == xray_transition_id)
        result = conn.execute(command)
        row = result.first()
        if row is None:
            raise NotFound('No transition found')
        source_subshell_id, destination_subshell_id = row

        source_subshell = self._get_atomic_subshell(conn, source_subshell_id)
        destination_subshell = self._get_atomic_subshell(conn, destination_subshell_id)
        return XrayTransition(source_subshell,
                              destination_subshell)

    def _get_xray_transitionset_id(self, conn, xraytransitionset):
        if isinstance(xraytransitionset, str):
            tbl = table.xray_transitionset_notation
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.xray_transitionset_id])
            command = command.where(sql.or_(tbl.c.ascii == xraytransitionset,
                                            tbl.c.utf16 == xraytransitionset))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        xraytransitions = set()
        if isinstance(xraytransitionset, XrayTransitionSet):
            xraytransitions.update(xraytransitionset.transitions)
        elif isinstance(xraytransitionset, collections.Sequence):
            xraytransitions.update(xraytransitionset)

        if xraytransitions:
            xraytransition_ids = set()
            for xraytransition in xraytransitions:
                xraytransition_id = self._get_xray_transition_id(conn, xraytransition)
                xraytransition_ids.add(xraytransition_id)

            table.xray_transitionset.create(conn, checkfirst=True)
            table.xray_transitionset_association.create(conn, checkfirst=True)

            tbl = table.xray_transitionset_association
            command = sql.select([tbl.c.xray_transitionset_id])
            command = command.where(tbl.c.xray_transition_id.in_(xraytransition_ids))
            command = command.distinct()
            result = conn.execute(command)

            for row in result:
                command = sql.select([tbl.c.xray_transitionset_id])
                command = command.where(tbl.c.xray_transitionset_id == row[0])
                command = command.group_by(tbl.c.xray_transitionset_id)
                command = command.having(sql.func.count(tbl.c.xray_transition_id) == len(xraytransition_ids))

                result = conn.execute(command)
                if result.fetchone():
                    return row[0]

        raise NotFound('Unknown transition set: {0}'.format(xraytransitionset))

    def _get_xray_transitionset(self, conn, xray_transitionset_id):
        tbl = table.xray_transitionset_association
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.xray_transition_id])
        command = command.where(tbl.c.xray_transitionset_id == xray_transitionset_id)
        result = conn.execute(command)
        rows = result.fetchall()
        if not rows:
            raise NotFound('No transition set found')

        transitions = [self._get_xray_transition(conn, row[0]) for row in rows]

        return XrayTransitionSet(transitions)

    def _get_language_id(self, conn, language):
        if isinstance(language, Language):
            code = language.code
        else:
            code = language

        tbl = table.language
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.id])
        command = command.where(tbl.c.code == code)
        return self._retrieve_first(conn, command,
                                    NotFound('Unknown language: {0}'
                                             .format(language)))

    def _get_notation_id(self, conn, notation):
        if isinstance(notation, Notation):
            name = notation.name
        else:
            name = notation

        tbl = table.notation
        tbl.create(conn, checkfirst=True)

        command = sql.select([tbl.c.id])
        command = command.where(tbl.c.name == name)
        return self._retrieve_first(conn, command,
                                    NotFound('Unknown notation: {0}'
                                             .format(notation)))

    def _get_reference_id(self, conn, reference):
        if isinstance(reference, Reference):
            bibtexkey = reference.bibtexkey
        else:
            bibtexkey = reference

        tbl = table.reference
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.id])
        command = command.where(tbl.c.bibtexkey == bibtexkey)
        return self._retrieve_first(conn, command,
                                    NotFound('Unknown reference: {0}'
                                             .format(reference)))

