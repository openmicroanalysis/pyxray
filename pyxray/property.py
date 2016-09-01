"""
Definition of properties.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.cbook import Immutable, Validable

# Globals and constants variables.

class _Property(Immutable, Validable):
    pass

class ElementSymbol(metaclass=_Property,
                    attrs=('reference', 'element', 'symbol')):

    @classmethod
    def validate(cls, reference, element, symbol):
        if len(symbol) == 0 or len(symbol) > 3:
            raise ValueError('Symbol should be between 1 and 3 characters')
        if not symbol[0].isupper():
            raise ValueError("Symbol should start with a capital letter")
        return reference, element, symbol

class ElementName(metaclass=_Property,
                  attrs=('reference', 'element', 'language', 'name')):

    @classmethod
    def validate(cls, reference, element, language, name):
        if not name:
            raise ValueError('A name must be specified')
        return reference, element, language, name

class ElementAtomicWeight(metaclass=_Property,
                          attrs=('reference', 'element', 'value')):

    @classmethod
    def validate(cls, reference, element, value):
        if value <= 0.0:
            raise ValueError('Value must be greater than 0.0')
        return reference, element, value

class ElementMassDensity(metaclass=_Property,
                          attrs=('reference', 'element', 'value_kg_per_m3')):

    @classmethod
    def validate(cls, reference, element, value_kg_per_m3):
        if value_kg_per_m3 <= 0.0:
            raise ValueError('Value must be greater than 0.0')
        return reference, element, value_kg_per_m3

class AtomicShellNotation(metaclass=_Property,
                          attrs=('reference', 'atomic_shell', 'notation',
                                 'value', 'value_html', 'value_latex')):

    @classmethod
    def validate(cls, reference, atomic_shell, notation,
                 value, value_html=None, value_latex=None):
        return (reference, atomic_shell, notation,
                value, value_html, value_latex)

class AtomicSubshellNotation(metaclass=_Property,
                          attrs=('reference', 'atomic_subshell', 'notation',
                                 'value', 'value_html', 'value_latex')):

    @classmethod
    def validate(cls, reference, atomic_shell, notation,
                 value, value_html=None, value_latex=None):
        return (reference, atomic_shell, notation,
                value, value_html, value_latex)