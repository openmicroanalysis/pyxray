""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.cbook import Immutable, Cachable, Validable

# Globals and constants variables.

class _Descriptor(Immutable, Cachable, Validable):
    pass

class Element(metaclass=_Descriptor,
              attrs=('atomic_number',)):

    @classmethod
    def validate(cls, atomic_number):
        if atomic_number < 1 or atomic_number > 118:
            raise ValueError('Atomic number ({0}) must be [1, 118]'
                             .format(atomic_number))
        return (atomic_number,)

    def __repr__(self):
        return '{0}(z={1})'.format(self.__class__.__name__, self.z)

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
        return (principal_quantum_number,)

    def __repr__(self):
        return '{0}(n={1})'.format(self.__class__.__name__, self.n)

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

    def __repr__(self):
        return '{0}(n={1}, l={2}, j={3:.1f})'.format(self.__class__.__name__,
                                                     self.n, self.l, self.j)

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
        #TODO: Validate transition
        return (source_subshell,
                destination_subshell,
                secondary_destination_subshell)

    def __repr__(self):
        r = '{0}('
        r += '[n={src.n}, l={src.l}, j={src.j:.1f}]'
        r += ' -> [n={dest.n}, l={dest.l}, j={dest.j:.1f}]'
        if self.secondary_destination_subshell is not None:
            r += ' -> [n={dest2.n}, l={dest2.l}, j={dest2.j:.1f}]'
        r += ')'

        return r.format(self.__class__.__name__,
                        src=self.source_subshell,
                        dest=self.destination_subshell,
                        dest2=self.secondary_destination_subshell)

    def is_radiative(self):
        return self.secondary_destination_subshell is None

    def is_nonradiative(self):
        return not self.is_radiative()

    def is_coster_kronig(self):
        return self.source_subshell.n == self.destination_subshell.n

class TransitionSet(metaclass=_Descriptor,
                    attrs=('transitions',)):

    @classmethod
    def validate(cls, transitions):
        transitions = frozenset(transitions)
        return (transitions,)

    def __repr__(self):
        return '{0}({1:d} transitions)'.format(self.__class__.__name__,
                                               len(self.transitions))

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

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.bibtexkey)
