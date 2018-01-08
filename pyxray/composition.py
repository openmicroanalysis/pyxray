""""""

# Standard library modules.
import math
import string
from collections import defaultdict
import itertools

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore

# Local modules.
import pyxray

# Globals and constants variables.

_symbol = Word(string.ascii_uppercase, string.ascii_lowercase)
_digit = Word(string.digits + ".")
_elementRef = Group(_symbol + Optional(_digit, default="1"))
_formula_parser = OneOrMore(_elementRef)

def _process_wildcard(fractions):
    """
    Processes element(s) with a wildcard ``?`` fraction and returns
    composition balanced to 1.0. 
    """
    fractions2 = fractions.copy()

    wildcard_zs = set()
    total_fraction = 0.0
    for z, fraction in fractions.items():
        if fraction == '?':
            wildcard_zs.add(z)
        else:
            total_fraction += fraction

    if not wildcard_zs:
        return fractions2

    balance_wf = (1.0 - total_fraction) / len(wildcard_zs)
    for z in wildcard_zs:
        fractions2[z] = balance_wf

    return fractions2

class CompositionConverter:

    def __init__(self, mass_fractions):
        if not mass_fractions:
            raise ValueError('A composition must contain at least one element.')
        if sum(mass_fractions.values()) <= 0.0:
            raise ValueError('A composition must have a total mass fraction greater than 0.')
        if not all(isinstance(z, int) and z >= 1 for z in mass_fractions.keys()):
            raise ValueError('The keys of the composition dictionary must be integers greater or equal to 1.')
        self._mass_fractions = mass_fractions.copy()

        # Repr
        inner = ' '.join('{1:g}%{0}'.format(pyxray.element_symbol(z), wf * 100.0)
                    for z, wf in self._mass_fractions.items())
        self._repr = '<{}({})>'.format(self.__class__.__name__, inner)

    @classmethod
    def _from_formula(cls, formula):
        # Parse chemical formula
        formula_data = _formula_parser.parseString(formula)

        mole_fractions = {}
        for symbol, mole_fraction in formula_data:
            z = pyxray.element_atomic_number(symbol)
            mole_fractions[z] = float(mole_fraction)

        return mole_fractions

    @classmethod
    def from_formula(cls, formula):
        mole_fractions = cls._from_formula(formula)
        return cls.from_atomic_fractions(mole_fractions)

    @classmethod
    def from_mass_fractions(cls, mass_fractions):
        mass_fractions = _process_wildcard(mass_fractions)
        return cls(mass_fractions)

    @classmethod
    def from_atomic_fractions(cls, atomic_fractions):
        atomic_fractions = _process_wildcard(atomic_fractions)

        # Calculate total atomic mass
        total_atomic_weight = 0.0
        for z, atomic_fraction in atomic_fractions.items():
            atomic_weight = pyxray.element_atomic_weight(z)
            total_atomic_weight += atomic_fraction * atomic_weight

        # Create composition
        mass_fractions = {}

        for z, atomic_fraction in atomic_fractions.items():
            atomic_weight = pyxray.element_atomic_weight(z)
            mass_fraction = atomic_fraction * atomic_weight / total_atomic_weight
            mass_fractions[z] = mass_fraction

        return cls.from_mass_fractions(mass_fractions)

    @classmethod
    def from_oxide_fractions(cls, oxide_fractions):
        mass_proportions = defaultdict(float)

        for oxide_formula, fraction in oxide_fractions.items():
            oxide_mole_fractions = cls._from_formula(oxide_formula)

            oxide_atomic_weight = 0.0
            for z, mole_fraction in oxide_mole_fractions.items():
                atomic_weight = pyxray.element_atomic_weight(z)
                oxide_atomic_weight += mole_fraction * atomic_weight

            composition = cls.from_atomic_fractions(oxide_mole_fractions)
            oxide_mass_fractions = composition.to_mass_fractions()

            for z, mass_fraction in oxide_mass_fractions.items():
                mole_proportion = fraction / oxide_atomic_weight
                mass_proportions[z] += mole_proportion * mass_fraction

        total_mass_proportion = sum(mass_proportions.values())

        mass_fractions = {}
        for z, mass_proportion in mass_proportions.items():
            mass_fractions[z] = mass_proportion / total_mass_proportion

        return cls(mass_fractions)

    def __contains__(self, element):
        """
        Returns whether an element is part of the composition.
        """
        z = pyxray.element_atomic_number(element)
        return z in self._mass_fractions

    def __len__(self):
        """
        Returns number of elements in the composition.
        """
        return len(self._mass_fractions)

    def __repr__(self):
        return self._repr

    def to_formula(self, largest_common_denominator=100):
        atomic_fractions = self.to_atomic_fractions()

        symbols = []
        fractions = []
        for z in sorted(atomic_fractions.keys(), reverse=True):
            symbols.append(pyxray.element_symbol(z))
            fractions.append(int(atomic_fractions[z] * largest_common_denominator))

        # Find gcd of the fractions
        smallest_gcd = largest_common_denominator
        if len(fractions) >= 2:
            smallest_gcd = min(math.gcd(a, b) for a, b in itertools(fractions, 2))

        if smallest_gcd == 0:
            smallest_gcd = largest_common_denominator

        # Write formula
        formula = ''
        for symbol, fraction in zip(symbols, fractions):
            fraction /= smallest_gcd
            if fraction == 0:
                continue
            elif fraction == 1:
                formula += symbol
            else:
                formula += '{}{}'.format(symbol, fraction)

        return formula

    def to_mass_fractions(self, normalize=False):
        mass_fractions = defaultdict(float, self._mass_fractions)

        if normalize:
            total_mass_fraction = sum(mass_fractions.values())

            for z, mass_fraction in mass_fractions.items():
                mass_fractions[z] = mass_fraction / total_mass_fraction

        return mass_fractions

    def to_atomic_fractions(self):
        mass_fractions = self.to_mass_fractions(normalize=True)

        atomic_fractions = {}
        for z, mass_fraction in mass_fractions.items():
            atomic_weight = pyxray.element_atomic_weight(z)
            atomic_fractions[z] = mass_fraction / atomic_weight

        total_atomic_fraction = sum(atomic_fractions.values())
        assert total_atomic_fraction > 0.0

        for z, atomic_fraction in atomic_fractions.items():
            atomic_fractions[z] = atomic_fraction / total_atomic_fraction

        return defaultdict(float, atomic_fractions)

    def to_oxide_fractions(self, charges=None):
        raise NotImplementedError
