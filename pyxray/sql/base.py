"""
Base SQL engine
"""

# Standard library modules.
from operator import itemgetter
import collections

# Third party modules.
import sqlalchemy.sql as sql

# Local modules.
from pyxray.descriptor import \
    (Element, Language, Reference, Notation, AtomicShell, AtomicSubshell,
     Transition, TransitionSet)
import pyxray.cbook as cbook
import pyxray.sql.table as table
from pyxray.base import NotFound

# Globals and constants variables.

class SqlEngineDatabaseMixin:

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

    def _get_transition_id(self, conn, transition):
        if isinstance(transition, str):
            tbl = table.transition_notation
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.transition_id])
            command = command.where(sql.or_(tbl.c.ascii == transition,
                                            tbl.c.utf16 == transition))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        source_subshell = None
        destination_subshell = None
        secondary_destination_subshell = None
        if isinstance(transition, Transition):
            source_subshell = transition.source_subshell
            destination_subshell = transition.destination_subshell
            secondary_destination_subshell = transition.secondary_destination_subshell
        elif isinstance(transition, collections.Sequence) and \
                len(transition) >= 2:
            source_subshell = transition[0]
            destination_subshell = transition[1]
            if len(transition) == 3:
                secondary_destination_subshell = transition[2]

        if source_subshell is not None and \
                destination_subshell is not None:
            source_subshell_id = self._get_atomic_subshell_id(conn, source_subshell)
            destination_subshell_id = self._get_atomic_subshell_id(conn, destination_subshell)
            if secondary_destination_subshell:
                secondary_destination_subshell_id = \
                    self._get_atomic_subshell_id(conn, secondary_destination_subshell)
            else:
                secondary_destination_subshell_id = None

            tbl = table.transition
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.id])
            command = command.where(sql.and_(tbl.c.source_subshell_id == source_subshell_id,
                                             tbl.c.destination_subshell_id == destination_subshell_id,
                                             tbl.c.secondary_destination_subshell_id == secondary_destination_subshell_id))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        raise NotFound('Unknown transition: {0}'.format(transition))

    def _get_transitionset_id(self, conn, transitionset):
        if isinstance(transitionset, str):
            tbl = table.transitionset_notation
            tbl.create(conn, checkfirst=True)

            command = sql.select([tbl.c.transitionset_id])
            command = command.where(sql.or_(tbl.c.ascii == transitionset,
                                            tbl.c.utf16 == transitionset))
            out = self._retrieve_first(conn, command)
            if out is not None:
                return out

        transitions = set()
        if isinstance(transitionset, TransitionSet):
            transitions.update(transitionset.transitions)
        elif isinstance(transitionset, collections.Sequence):
            transitions.update(transitionset)

        if transitions:
            transition_ids = set()
            for transition in transitions:
                transition_id = self._get_transition_id(conn, transition)
                transition_ids.add(transition_id)

            table.transitionset.create(conn, checkfirst=True)
            table.transitionset_association.create(conn, checkfirst=True)

            tbl = table.transitionset_association
            conditions = []
            for transition_id in transition_ids:
                conditions.append(tbl.c.transition_id == transition_id)

            command = sql.select([table.transitionset_association])
            command = command.where(sql.or_(*conditions))

            result = conn.execute(command)
            rows = result.fetchall()
            if rows and cbook.allequal(map(itemgetter(0), rows)):
                return rows[0]['transitionset_id']

        raise NotFound('Unknown transition set: {0}'.format(transitionset))

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

