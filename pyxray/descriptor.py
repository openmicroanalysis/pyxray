"""
Definition of descriptors.
"""

__all__ = ['Element', 'AtomicShell', 'AtomicSubshell', 'XrayTransition', 'XrayLine', 'Language', 'Notation', 'Reference']

# Standard library modules.
import dataclasses
import typing
import functools
from collections.abc import Sequence

# Third party modules.

# Local modules.

# Globals and constants variables.

@dataclasses.dataclass(frozen=True, order=True)
class Element:
    atomic_number: int

    def __post_init__(self):
        if self.atomic_number < 1 or self.atomic_number > 118:
            raise ValueError('Atomic number ({0}) must be [1, 118]'
                             .format(self.atomic_number))

    def __repr__(self):
        return '{}(z={})'.format(self.__class__.__name__, self.atomic_number)

    @property
    def z(self):
        return self.atomic_number

@dataclasses.dataclass(frozen=True, order=True)
class AtomicShell:
    principal_quantum_number: int

    def __post_init__(self):
        if self.principal_quantum_number < 1:
            raise ValueError('Principal quantum number ({0}) must be [1, inf['
                             .format(self.principal_quantum_number))

    def __repr__(self):
        return '{}(n={})'.format(self.__class__.__name__, self.principal_quantum_number)

    @property
    def n(self):
        return self.principal_quantum_number

@dataclasses.dataclass(frozen=True, order=True)
class AtomicSubshell:
    principal_quantum_number: int
    azimuthal_quantum_number: int
    total_angular_momentum_nominator: int

    def __post_init__(self):
        if isinstance(self.principal_quantum_number, AtomicShell):
            object.__setattr__(self, 'principal_quantum_number', self.principal_quantum_number.n)

        if self.principal_quantum_number is not None and self.azimuthal_quantum_number is not None:
            lmin = 0
            lmax = self.principal_quantum_number - 1
            if self.azimuthal_quantum_number < lmin or \
                    self.azimuthal_quantum_number > lmax:
                raise ValueError('Azimuthal quantum number ({0}) must be between [{1}, {2}]'
                                .format(self.azimuthal_quantum_number, lmin, lmax))

        if self.azimuthal_quantum_number is not None and self.total_angular_momentum_nominator is not None:
            jmin_n = 2 * abs(self.azimuthal_quantum_number - 0.5)
            jmax_n = 2 * abs(self.azimuthal_quantum_number + 0.5)

            if self.total_angular_momentum_nominator < jmin_n or \
                    self.total_angular_momentum_nominator > jmax_n:
                raise ValueError('Total angular momentum ({0}) must be between [{1}, {2}]'
                                .format(self.total_angular_momentum_nominator, jmin_n, jmax_n))

    def __repr__(self):
        return '{}(n={}, l={}, j={:.1f})'.format(self.__class__.__name__, self.n, self.l, self.j)

    @property
    def atomic_shell(self):
        return AtomicShell(self.principal_quantum_number)

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
        if self.total_angular_momentum_nominator is None:
            return None
        return self.total_angular_momentum_nominator / 2.0

    @property
    def j(self):
        return self.total_angular_momentum

@dataclasses.dataclass(frozen=True)
class XrayTransition:
    source_principal_quantum_number: int = None
    source_azimuthal_quantum_number: int = None
    source_total_angular_momentum_nominator: int = None
    destination_principal_quantum_number: int = None
    destination_azimuthal_quantum_number: int = None
    destination_total_angular_momentum_nominator: int = None

    def __init__(self, *args):
        if len(args) == 6:
            src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n = args

        elif len(args) == 2:
            if isinstance(args[0], Sequence):
                src_n, src_l, src_j_n = args[0]
            elif isinstance(args[0], AtomicSubshell):
                src_n = args[0].n
                src_l = args[0].l
                src_j_n = args[0].j_n
            else:
                raise ValueError('Unknown argument: {}'.format(args[0]))

            if isinstance(args[1], Sequence):
                dst_n, dst_l, dst_j_n = args[1]
            elif isinstance(args[1], AtomicSubshell):
                dst_n = args[1].n
                dst_l = args[1].l
                dst_j_n = args[1].j_n
            else:
                raise ValueError('Unknown argument: {}'.format(args[1]))

        elif len(args) == 4:
            if isinstance(args[0], Sequence):
                src_n, src_l, src_j_n = args[0]
                dst_n, dst_l, dst_j_n = args[1:]
            elif isinstance(args[0], AtomicSubshell):
                src_n = args[0].n
                src_l = args[0].l
                src_j_n = args[0].j_n
                dst_n, dst_l, dst_j_n = args[1:]
            elif isinstance(args[-1], Sequence):
                src_n, src_l, src_j_n = args[:-1]
                dst_n, dst_l, dst_j_n = args[-1]
            elif isinstance(args[-1], AtomicSubshell):
                src_n, src_l, src_j_n = args[:-1]
                dst_n = args[-1].n
                dst_l = args[-1].l
                dst_j_n = args[-1].j_n

        else:
            raise ValueError('Unsupported number of arguments: {}'.format(len(args)))

        object.__setattr__(self, 'source_principal_quantum_number', src_n)
        object.__setattr__(self, 'source_azimuthal_quantum_number', src_l)
        object.__setattr__(self, 'source_total_angular_momentum_nominator', src_j_n)
        object.__setattr__(self, 'destination_principal_quantum_number', dst_n)
        object.__setattr__(self, 'destination_azimuthal_quantum_number', dst_l)
        object.__setattr__(self, 'destination_total_angular_momentum_nominator', dst_j_n)

    @classmethod
    def is_radiative(cls, source_subshell, destination_subshell):
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
            if j0_n == 1 and j1_n == 1:
                return False
            assert delta_j_n == 0 or delta_j_n == 2 or delta_j_n == 4

            delta_l = abs(l1 - l0)
            return delta_l == 0 or delta_l == 2

        n0 = source_subshell.n
        l0 = source_subshell.l
        j0_n = source_subshell.j_n
        n1 = destination_subshell.n
        l1 = destination_subshell.l
        j1_n = destination_subshell.j_n

        if n0 == n1:
            return False

        if not(electric_dipole_permitted(n0, l0, j0_n, n1, l1, j1_n) or \
               electric_quadrupole_permitted(n0, l0, j0_n, n1, l1, j1_n)):
            return False

        return True

    def __repr__(self):
        def _format(value):
            return '*' if value is None else value

        return '{}([n={}, l={}, j={}] -> [n={}, l={}, j={}])'\
            .format(self.__class__.__name__,
                    _format(self.source_principal_quantum_number),
                    _format(self.source_azimuthal_quantum_number),
                    _format(self.source_total_angular_momentum),
                    _format(self.destination_principal_quantum_number),
                    _format(self.destination_azimuthal_quantum_number),
                    _format(self.destination_total_angular_momentum))

    @property
    def source_subshell(self):
        return AtomicSubshell(self.source_principal_quantum_number,
                              self.source_azimuthal_quantum_number,
                              self.source_total_angular_momentum_nominator)

    @property
    def destination_subshell(self):
        return AtomicSubshell(self.destination_principal_quantum_number,
                              self.destination_azimuthal_quantum_number,
                              self.destination_total_angular_momentum_nominator)

    @property
    def source_total_angular_momentum(self):
        if self.source_total_angular_momentum_nominator is None:
            return None
        return self.source_total_angular_momentum_nominator / 2.0

    @property
    def destination_total_angular_momentum(self):
        if self.destination_total_angular_momentum_nominator is None:
            return None
        return self.destination_total_angular_momentum_nominator / 2.0

@dataclasses.dataclass(frozen=True)
class XrayLine:
    element: Element
    transition: XrayTransition
    iupac: str = dataclasses.field(compare=False)
    siegbahn: str = dataclasses.field(compare=False)
    energy_eV: float = dataclasses.field(compare=False)
    probability: float = dataclasses.field(default=None, compare=False)
    relative_weight: float = dataclasses.field(default=None, compare=False)

    def __post_init__(self):
        if not isinstance(self.element, Element):
            object.__setattr__(self, 'element', Element(self.element))
        if not isinstance(self.transition, XrayTransition):
            object.__setattr__(self, 'transition', XrayTransition(self.transition))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.iupac)

    @property
    def atomic_number(self):
        return self.element.atomic_number

    @property
    def z(self):
        return self.element.atomic_number

@dataclasses.dataclass(frozen=True)
class Language:
    key: str

    def __post_init__(self):
        lencode = len(self.key)
        if lencode < 2 or lencode > 3:
            raise ValueError('Code must be between 2 and 3 characters')

        object.__setattr__(self, 'key', self.key.lower())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.key)

@dataclasses.dataclass(frozen=True)
class Notation:
    key: str

    def __post_init__(self):
        if not self.key:
            raise ValueError('Name cannot be empty')

        object.__setattr__(self, 'key', self.key.lower())

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.key)

@dataclasses.dataclass(frozen=True)
class Reference:
    bibtexkey: str
    author: str = None
    year: str = None
    title: str = None
    type: str = None
    booktitle: str = None
    editor: str = None
    pages: str = None
    edition: str = None
    journal: str = None
    school: str = None
    address: str = None
    url: str = None
    note: str = None
    number: str = None
    series: str = None
    volume: str = None
    publisher: str = None
    organization: str = None
    chapter: str = None
    howpublished: str = None
    doi: str = None

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.bibtexkey)
