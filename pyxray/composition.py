""""""

__all__ = ['Composition']

# Standard library modules.
import math
from types import MappingProxyType
import itertools
from fractions import Fraction
import re

# Third party modules.
import pyxray

# Local modules.

# Globals and constants variables.
CHEMICAL_FORMULA_PATTERN = re.compile(r'([A-Z][a-z]?)([0-9\.]*)')

def process_wildcard(fractions):
    """
    Processes element with a wildcard ``?`` weight fraction and returns
    composition balanced to 1.0.
    """
    wildcard_zs = set()
    total_fraction = 0.0
    for z, fraction in fractions.items():
        if fraction == '?':
            wildcard_zs.add(z)
        else:
            total_fraction += fraction

    if not wildcard_zs:
        return fractions

    balance_fraction = (1.0 - total_fraction) / len(wildcard_zs)
    for z in wildcard_zs:
        fractions[z] = balance_fraction

    return fractions

def convert_mass_to_atomic_fractions(mass_fractions):
    """
    Converts a mass fraction :class:`dict` to an atomic fraction :class:`dict`.

    Args:
        mass_fractions (dict): mass fraction :class:`dict`.
            The composition is specified by a dictionary.
            The keys are atomic numbers and the values weight fractions.
            No wildcard are accepted.
    """
    atomic_fractions = {}

    for z, mass_fraction in mass_fractions.items():
        atomic_fractions[z] = mass_fraction / pyxray.element_atomic_weight(z)

    total_fraction = sum(atomic_fractions.values())

    for z, fraction in atomic_fractions.items():
        try:
            atomic_fractions[z] = fraction / total_fraction
        except ZeroDivisionError:
            atomic_fractions[z] = 0.0

    return atomic_fractions

def convert_atomic_to_mass_fractions(atomic_fractions):
    """
    Converts an atomic fraction :class:`dict` to a mass fraction :class:`dict`.

    Args:
        atomic_fractions (dict): atomic fraction :class:`dict`.
            The composition is specified by a dictionary.
            The keys are atomic numbers and the values atomic fractions.
            No wildcard are accepted.
    """
    # Calculate total atomic mass
    atomic_masses = {}
    total_atomic_mass = 0.0
    for z, atomic_fraction in atomic_fractions.items():
        atomic_mass = pyxray.element_atomic_weight(z)
        atomic_masses[z] = atomic_mass
        total_atomic_mass += atomic_fraction * atomic_mass

    # Create mass fraction
    mass_fractions = {}
    for z, atomic_fraction in atomic_fractions.items():
        mass_fractions[z] = atomic_fraction * atomic_masses[z] / total_atomic_mass

    return mass_fractions

def convert_formula_to_atomic_fractions(formula):
    """
    Converts a chemical formula to an atomic fraction :class:`dict`.

    Args:
        formula (str): chemical formula, like Al2O3. No wildcard are accepted.
    """
    mole_fractions = {}
    total_mole_fraction = 0.0

    for match in CHEMICAL_FORMULA_PATTERN.finditer(formula):
        symbol, mole_fraction = match.groups()

        z = pyxray.element_atomic_number(symbol.strip())

        if mole_fraction == '':
            mole_fraction = 1.0
        mole_fraction = float(mole_fraction)

        mole_fraction = float(mole_fraction)
        mole_fractions[z] = mole_fraction
        total_mole_fraction += mole_fraction

    # Calculate atomic fractions
    atomic_fractions = {}
    for z, mole_fraction in mole_fractions.items():
        atomic_fractions[z] = mole_fraction / total_mole_fraction

    return atomic_fractions

def generate_name(atomic_fractions):
    """
    Generates a name from the composition.
    The name is generated on the basis of a classical chemical formula.
    """
    if not atomic_fractions:
        return ''

    if len(atomic_fractions) == 1:
        z = list(atomic_fractions.keys())[0]
        return pyxray.element_symbol(z)

    symbols = []
    fractions = []
    for z in sorted(atomic_fractions.keys(), reverse=True):
        symbols.append(pyxray.element_symbol(z))
        fractions.append(Fraction(atomic_fractions[z]).limit_denominator())

    # Find gcd of the fractions
    gcds = []
    for a, b in itertools.combinations(fractions, 2):
        gcds.append(math.gcd(a.denominator, b.denominator))
    smallest_gcd = min(gcds)

    # Write formula
    name = ''
    for symbol, fraction in zip(symbols, fractions):
        mole_fraction = int(fraction * smallest_gcd)
        if mole_fraction == 0:
            continue
        elif mole_fraction == 1:
            name += "%s" % symbol
        else:
            name += '%s%i' % (symbol, mole_fraction)

    return name

class Composition:
    """
    Defines a composition of a compound.

    To create a composition, use the class methods:

        - :meth:`from_pure`
        - :meth:`from_formula`
        - :meth:`from_mass_fractions`
        - :meth:`from_atomic_fractions`

    Use the following attributes to access the composition values:

        - :attr:`mass_fractions`: :class:`dict` where the keys are atomic numbers and the values weight fractions.
        - :attr:`atomic_fractions`: :class:`dict` where the keys are atomic numbers and the values atomic fractions.
        - :attr:`formula`: chemical formula

    The composition object is immutable, i.e. it cannot be modified once created.
    Equality can be checked.
    It is hashable.
    It can be pickled or copied.
    """

    _key = object()
    PRECISION = 0.000000001 # 1ppb

    def __init__(self, key, mass_fractions, atomic_fractions, formula):
        """
        Private constructor. It should never be used.
        """
        if key != Composition._key:
            raise TypeError('Composition cannot be created using constructor')
        if set(mass_fractions.keys()) != set(atomic_fractions.keys()):
            raise ValueError('Mass and atomic fractions must have the same elements')

        self.mass_fractions = MappingProxyType(mass_fractions)
        self.atomic_fractions = MappingProxyType(atomic_fractions)
        self._formula = formula

    @classmethod
    def from_pure(cls, z):
        """
        Creates a pure composition.

        Args:
            z (int): atomic number
        """
        return cls(cls._key, {z: 1.0}, {z: 1.0}, pyxray.element_symbol(z))

    @classmethod
    def from_formula(cls, formula):
        """
        Creates a composition from a chemical formula.

        Args:
            formula (str): chemical formula
        """
        atomic_fractions = convert_formula_to_atomic_fractions(formula)
        return cls.from_atomic_fractions(atomic_fractions)

    @classmethod
    def from_mass_fractions(cls, mass_fractions, formula=None):
        """
        Creates a composition from a mass fraction :class:`dict`.

        Args:
            mass_fractions (dict): mass fraction :class:`dict`.
                The keys are atomic numbers and the values weight fractions.
                Wildcard are accepted, e.g. ``{5: '?', 25: 0.4}`` where boron
                will get a mass fraction of 0.6.
            formula (str): optional chemical formula for the composition.
                If ``None``, a formula will be generated for the composition.
        """
        mass_fractions = process_wildcard(mass_fractions)
        atomic_fractions = convert_mass_to_atomic_fractions(mass_fractions)
        if not formula:
            formula = generate_name(atomic_fractions)
        return cls(cls._key, mass_fractions, atomic_fractions, formula)

    @classmethod
    def from_atomic_fractions(cls, atomic_fractions, formula=None):
        """
        Creates a composition from an atomic fraction :class:`dict`.

        Args:
            atomic_fractions (dict): atomic fraction :class:`dict`.
                The keys are atomic numbers and the values atomic fractions.
                Wildcard are accepted, e.g. ``{5: '?', 25: 0.4}`` where boron
                will get a atomic fraction of 0.6.
            formula (str): optional chemical formula for the composition.
                If ``None``, a formula will be generated for the composition.
        """
        atomic_fractions = process_wildcard(atomic_fractions)
        mass_fractions = convert_atomic_to_mass_fractions(atomic_fractions)
        if not formula:
            formula = generate_name(atomic_fractions)
        return cls(cls._key, mass_fractions, atomic_fractions, formula)

    def __len__(self):
        return len(self.mass_fractions)

    def __contains__(self, z):
        return z in self.mass_fractions

    def __iter__(self):
        return iter(self.mass_fractions.keys())

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.inner_repr())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if len(self) != len(other):
            return False

        for z in self.mass_fractions:
            if z not in other.mass_fractions:
                return False

            fraction = self.mass_fractions[z]
            other_fraction = other.mass_fractions[z]

            if not math.isclose(fraction, other_fraction, abs_tol=self.PRECISION):
                return False

        return True

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        out = []
        for z in sorted(self.mass_fractions):
            out.append(z)
            out.append(int(self.mass_fractions[z] / self.PRECISION))

        return hash(tuple(out))

    def __getstate__(self):
        return {'mass_fractions': dict(self.mass_fractions),
                'atomic_fractions': dict(self.atomic_fractions),
                'formula': self.formula}

    def __setstate__(self, state):
        self.mass_fractions = MappingProxyType(state.get('mass_fractions', {}))
        self.atomic_fractions = MappingProxyType(state.get('atomic_fractions', {}))
        self._formula = state.get('formula', '')

    def is_normalized(self):
        return math.isclose(sum(self.mass_fractions.values()), 1.0, abs_tol=self.PRECISION)

    def inner_repr(self):
        return ', '.join('{}: {:.4f}'.format(pyxray.element_symbol(z), mass_fraction) for z, mass_fraction in self.mass_fractions.items())

    @property
    def formula(self):
        return self._formula
