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

class TransitionNotation(metaclass=_Property,
                         attrs=('reference', 'transition', 'notation',
                                'ascii', 'utf16', 'html', 'latex')):

    @classmethod
    def validate(cls, reference, transition, notation,
                 ascii, utf16=None, html=None, latex=None):
        pass

class TransitionEnergy(metaclass=_Property,
                       attrs=('reference', 'element', 'transition', 'value_eV')):

    @classmethod
    def validate(cls, reference, element, transition, value_eV):
        pass

class TransitionProbability(metaclass=_Property,
                            attrs=('reference', 'element', 'transition', 'value')):

    @classmethod
    def validate(cls, reference, element, transition, value):
        pass

class TransitionRelativeWeight(metaclass=_Property,
                            attrs=('reference', 'element', 'transition', 'value')):

    @classmethod
    def validate(cls, reference, element, transition, value):
        pass

class TransitionSetNotation(metaclass=_Property,
                            attrs=('reference', 'transitionset', 'notation',
                                   'ascii', 'utf16', 'html', 'latex')):

    @classmethod
    def validate(cls, reference, transitionset, notation,
                 ascii, utf16=None, html=None, latex=None):
        pass

class TransitionSetEnergy(metaclass=_Property,
                          attrs=('reference', 'element', 'transitionset',
                                 'value_eV')):

    @classmethod
    def validate(cls, reference, element, transitionset, value_eV):
        pass

class TransitionSetRelativeWeight(metaclass=_Property,
                          attrs=('reference', 'element', 'transitionset',
                                 'value')):

    @classmethod
    def validate(cls, reference, element, transitionset, value):
        pass
