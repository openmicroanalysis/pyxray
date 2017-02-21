"""
Definition of properties.
"""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.cbook import Immutable, Validable, Reprable

# Globals and constants variables.

class _Property(Immutable, Validable, Reprable):
    pass

class ElementSymbol(metaclass=_Property,
                    attrs=('reference', 'element', 'symbol')):

    @classmethod
    def validate(cls, reference, element, symbol):
        if len(symbol) == 0 or len(symbol) > 3:
            raise ValueError('Symbol should be between 1 and 3 characters')
        if not symbol[0].isupper():
            raise ValueError("Symbol should start with a capital letter")

class ElementName(metaclass=_Property,
                  attrs=('reference', 'element', 'language', 'name')):

    @classmethod
    def validate(cls, reference, element, language, name):
        if not name:
            raise ValueError('A name must be specified')

class ElementAtomicWeight(metaclass=_Property,
                          attrs=('reference', 'element', 'value')):

    @classmethod
    def validate(cls, reference, element, value):
        if value <= 0.0:
            raise ValueError('Value must be greater than 0.0')

class ElementMassDensity(metaclass=_Property,
                          attrs=('reference', 'element', 'value_kg_per_m3')):

    @classmethod
    def validate(cls, reference, element, value_kg_per_m3):
        if value_kg_per_m3 <= 0.0:
            raise ValueError('Value must be greater than 0.0')
        return reference, element, value_kg_per_m3

class AtomicShellNotation(metaclass=_Property,
                          attrs=('reference', 'atomic_shell', 'notation',
                                 'ascii', 'utf16', 'html', 'latex')):

    @classmethod
    def validate(cls, reference, atomic_shell, notation,
                 ascii, utf16=None, html=None, latex=None):
        pass

class AtomicSubshellNotation(metaclass=_Property,
                             attrs=('reference', 'atomic_subshell', 'notation',
                                    'ascii', 'utf16', 'html', 'latex')):

    @classmethod
    def validate(cls, reference, atomic_subshell, notation,
                 ascii, utf16=None, html=None, latex=None):
        pass

class AtomicSubshellBindingEnergy(metaclass=_Property,
                                  attrs=('reference', 'element', 'atomic_subshell',
                                         'value_eV')):

    @classmethod
    def validate(cls, reference, element, atomic_subshell, value_eV):
        pass

class AtomicSubshellRadiativeWidth(metaclass=_Property,
                                   attrs=('reference', 'element', 'atomic_subshell',
                                          'value_eV')):

    @classmethod
    def validate(cls, reference, element, atomic_subshell, value_eV):
        pass

class AtomicSubshellNonRadiativeWidth(metaclass=_Property,
                                      attrs=('reference', 'element', 'atomic_subshell',
                                             'value_eV')):

    @classmethod
    def validate(cls, reference, element, atomic_subshell, value_eV):
        pass

class AtomicSubshellOccupancy(metaclass=_Property,
                              attrs=('reference', 'element', 'atomic_subshell',
                                     'value')):

    @classmethod
    def validate(cls, reference, element, atomic_subshell, value_eV):
        pass

class XrayTransitionNotation(metaclass=_Property,
                             attrs=('reference', 'xraytransition', 'notation',
                                    'ascii', 'utf16', 'html', 'latex')):

    @classmethod
    def validate(cls, reference, xraytransition, notation,
                 ascii, utf16=None, html=None, latex=None):
        pass

class XrayTransitionEnergy(metaclass=_Property,
                           attrs=('reference', 'element', 'xraytransition', 'value_eV')):

    @classmethod
    def validate(cls, reference, element, xraytransition, value_eV):
        pass

class XrayTransitionProbability(metaclass=_Property,
                                attrs=('reference', 'element', 'xraytransition', 'value')):

    @classmethod
    def validate(cls, reference, element, xraytransition, value):
        pass

class XrayTransitionRelativeWeight(metaclass=_Property,
                                   attrs=('reference', 'element', 'xraytransition', 'value')):

    @classmethod
    def validate(cls, reference, element, xraytransition, value):
        pass

class XrayTransitionSetNotation(metaclass=_Property,
                                attrs=('reference', 'xraytransitionset', 'notation',
                                       'ascii', 'utf16', 'html', 'latex')):

    @classmethod
    def validate(cls, reference, xraytransitionset, notation,
                 ascii, utf16=None, html=None, latex=None):
        pass

class XrayTransitionSetEnergy(metaclass=_Property,
                              attrs=('reference', 'element', 'xraytransitionset',
                                     'value_eV')):

    @classmethod
    def validate(cls, reference, element, xraytransitionset, value_eV):
        pass

class XrayTransitionSetRelativeWeight(metaclass=_Property,
                                      attrs=('reference', 'element', 'xraytransitionset',
                                             'value')):

    @classmethod
    def validate(cls, reference, element, xraytransitionset, value):
        pass
