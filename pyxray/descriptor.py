"""
Definition of descriptors.
"""

__all__ = ['Element', 'AtomicShell', 'AtomicSubshell', 'Transition',
           'TransitionSet', 'Language', 'Notation', 'Reference']

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.cbook import Immutable, Cachable, Validable, Reprable

# Globals and constants variables.

class _Descriptor(Immutable, Validable, Cachable, Reprable):
    pass

class Element(metaclass=_Descriptor,
              attrs=('atomic_number',)):

    @classmethod
    def validate(cls, atomic_number):
        if atomic_number < 1 or atomic_number > 118:
            raise ValueError('Atomic number ({0}) must be [1, 118]'
                             .format(atomic_number))

    def _repr_inner(self):
        return 'z={0}'.format(self.z)

    @property
    def z(self):
        return self.atomic_number

class AtomicShell(metaclass=_Descriptor,
                  attrs=('principal_quantum_number',)):

    @classmethod
    def validate(cls, principal_quantum_number):
        if principal_quantum_number < 1:
            raise ValueError('Principal quantum number ({0}) must be [1, inf['
                             .format(principal_quantum_number))

    def _repr_inner(self):
        return 'n={0}'.format(self.n)

    @property
    def n(self):
        return self.principal_quantum_number

class AtomicSubshell(metaclass=_Descriptor,
                     attrs=('atomic_shell',
                            'azimuthal_quantum_number',
                            'total_angular_momentum_nominator')):

    @classmethod
    def validate(cls,
                 atomic_shell,
                 azimuthal_quantum_number,
                 total_angular_momentum_nominator):
        if not isinstance(atomic_shell, AtomicShell):
            atomic_shell = AtomicShell(atomic_shell)

        lmin = 0
        lmax = atomic_shell.principal_quantum_number - 1
        jmin_n = 2 * abs(azimuthal_quantum_number - 0.5)
        jmax_n = 2 * abs(azimuthal_quantum_number + 0.5)

        if azimuthal_quantum_number < lmin or \
                azimuthal_quantum_number > lmax:
            raise ValueError('Azimuthal quantum number ({0}) must be between [{1}, {2}]'
                             .format(azimuthal_quantum_number, lmin, lmax))
        if total_angular_momentum_nominator < jmin_n or \
                total_angular_momentum_nominator > jmax_n:
            raise ValueError('Total angular momentum ({0}) must be between [{1}, {2}]'
                             .format(total_angular_momentum_nominator, jmin_n, jmax_n))

        return (atomic_shell,
                azimuthal_quantum_number,
                total_angular_momentum_nominator)

    def _repr_inner(self):
        return 'n={0}, l={1}, j={2:.1f}'.format(self.n, self.l, self.j)

    @property
    def principal_quantum_number(self):
        return self.atomic_shell.principal_quantum_number

    @property
    def n(self):
        return self.principal_quantum_number

    @property
    def l(self):
        return self.azimuthal_quantum_number

    @property
    def j_n(self):
        return self.total_angular_momentum_nominator

    @property
    def total_angular_momentum(self):
        return self.total_angular_momentum_nominator / 2.0

    @property
    def j(self):
        return self.total_angular_momentum

class Transition(metaclass=_Descriptor,
                 attrs=('source_subshell',
                        'destination_subshell',
                        'secondary_destination_subshell')):

    @classmethod
    def validate(cls,
                 source_subshell,
                 destination_subshell,
                 secondary_destination_subshell=None):
        if not isinstance(source_subshell, AtomicSubshell):
            source_subshell = AtomicSubshell(source_subshell)
        if not isinstance(destination_subshell, AtomicSubshell):
            destination_subshell = AtomicSubshell(destination_subshell)
        if secondary_destination_subshell and \
                not isinstance(secondary_destination_subshell, AtomicSubshell):
            secondary_destination_subshell = AtomicSubshell(secondary_destination_subshell)

        return (source_subshell,
                destination_subshell,
                secondary_destination_subshell)

    def _repr_inner(self):
        r = '[n={src.n}, l={src.l}, j={src.j:.1f}]'
        r += ' -> [n={dest.n}, l={dest.l}, j={dest.j:.1f}]'
        if self.secondary_destination_subshell is not None:
            r += ' -> [n={dest2.n}, l={dest2.l}, j={dest2.j:.1f}]'
        return r.format(src=self.source_subshell,
                        dest=self.destination_subshell,
                        dest2=self.secondary_destination_subshell)

    def is_radiative(self):
        """
        Inspired from NIST EPQ library by Nicholas Ritchie.
        """
        def electric_dipole_permitted(n0, l0, j0_n, n1, l1, j1_n):
            delta_j_n = abs(j1_n - j0_n)
            if delta_j_n > 2:
                return False
            assert delta_j_n == 0 or delta_j_n == 2
            return abs(l1 - l0) == 1

        def electric_quadrupole_permitted(n0, l0, j0_n, n1, l1, j1_n):
            delta_j_n = abs(j1_n - j0_n)
            if delta_j_n > 4:
                return False
            assert delta_j_n == 0 or delta_j_n == 2 or delta_j_n == 4

            delta_l = abs(l1 - l0)
            return delta_l == 0 or delta_l == 2

        if self.secondary_destination_subshell is None:
            return False

        n0 = self.source_subshell.n
        l0 = self.source_subshell.l
        j0_n = self.source_subshell.j_n
        n1 = self.destination_subshell.n
        l1 = self.destination_subshell.l
        j1_n = self.destination_subshell.j_n

        if n0 == n1:
            return False

        if not(electric_dipole_permitted(n0, l0, j0_n, n1, l1, j1_n) or \
               electric_quadrupole_permitted(n0, l0, j0_n, n1, l1, j1_n)):
            return False

        return True

    def is_nonradiative(self):
        return not self.is_radiative()

    def is_coster_kronig(self):
        return self.source_subshell.n == self.destination_subshell.n

class TransitionSet(metaclass=_Descriptor,
                    attrs=('transitions',)):

    @classmethod
    def validate(cls, transitions):
        transitions2 = set()
        for transition in transitions:
            if not isinstance(transition, Transition):
                transition = Transition(*transition)
            transitions2.add(transition)
        return (frozenset(transitions2),)

    def _repr_inner(self):
        return '{0:d} transitions'.format(len(self.transitions))

class Language(metaclass=_Descriptor,
               attrs=('code',)):

    @classmethod
    def validate(cls, code):
        lencode = len(code)
        if lencode < 2 or lencode > 3:
            raise ValueError('Code must be between 2 and 3 characters')
        code = code.lower()
        return (code,)

class Notation(metaclass=_Descriptor,
               attrs=('name',)):

    @classmethod
    def validate(cls, name):
        if not name:
            raise ValueError('Name cannot be empty')
        name = name.lower()
        return (name,)

class Reference(metaclass=_Descriptor,
                attrs=('bibtexkey', 'author', 'year', 'title', 'type',
                       'booktitle', 'editor', 'pages', 'edition',
                       'journal', 'school', 'address', 'url', 'note',
                       'number', 'series', 'volume', 'publisher',
                       'organization', 'chapter', 'howpublished', 'doi')):

    @classmethod
    def validate(cls, bibtexkey, author=None, year=None, title=None,
                type=None, booktitle=None, editor=None, pages=None, #@ReservedAssignment
                edition=None, journal=None, school=None, address=None,
                url=None, note=None, number=None, series=None, volume=None,
                publisher=None, organization=None, chapter=None,
                howpublished=None, doi=None):
        if not bibtexkey:
            raise ValueError('A BibTeX key must be defined')

        return (bibtexkey, author, year, title, type, booktitle, editor,
                pages, edition, journal, school, address, url, note,
                number, series, volume, publisher, organization,
                chapter, howpublished, doi)

    def _repr_inner(self):
        return '{0}'.format(self.bibtexkey)
