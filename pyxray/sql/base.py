"""
Base SQL engine
"""

# Standard library modules.
import collections

# Third party modules.
import sqlalchemy.sql as sql

# Local modules.
from pyxray.descriptor import \
    (Element, Language, Reference, Notation, AtomicShell, AtomicSubshell,
     Transition, TransitionSet)
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

    def _get_transition(self, conn, transition_id):
        tbl = table.transition
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.source_subshell_id,
                              tbl.c.destination_subshell_id,
                              tbl.c.secondary_destination_subshell_id])
        command = command.where(tbl.c.id == transition_id)
        result = conn.execute(command)
        row = result.first()
        if row is None:
            raise NotFound('No transition found')
        source_subshell_id, destination_subshell_id, secondary_destination_subshell_id = row

        source_subshell = self._get_atomic_subshell(conn, source_subshell_id)
        destination_subshell = self._get_atomic_subshell(conn, destination_subshell_id)
        if secondary_destination_subshell_id is not None:
            secondary_destination_subshell = \
                self._get_atomic_subshell(conn, secondary_destination_subshell_id)
        else:
            secondary_destination_subshell = None
        return Transition(source_subshell,
                          destination_subshell,
                          secondary_destination_subshell)

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
            command = sql.select([tbl.c.transitionset_id])
            command = command.where(tbl.c.transition_id.in_(transition_ids))
            command = command.distinct()
            result = conn.execute(command)

            for row in result:
                command = sql.select([tbl.c.transitionset_id])
                command = command.where(tbl.c.transitionset_id == row[0])
                command = command.group_by(tbl.c.transitionset_id)
                command = command.having(sql.func.count(tbl.c.transition_id) == len(transition_ids))

                result = conn.execute(command)
                if result.fetchone():
                    return row[0]

        raise NotFound('Unknown transition set: {0}'.format(transitionset))

    def _get_transitionset(self, conn, transitionset_id):
        tbl = table.transitionset_association
        tbl.create(conn, checkfirst=True)
        command = sql.select([tbl.c.transition_id])
        command = command.where(tbl.c.transitionset_id == transitionset_id)
        result = conn.execute(command)
        rows = result.fetchall()
        if not rows:
            raise NotFound('No transition set found')

        transitions = [self._get_transition(conn, row[0]) for row in rows]

        return TransitionSet(transitions)

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

