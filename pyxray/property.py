"""
Definition of properties.
"""

# Standard library modules.
import dataclasses

# Third party modules.

# Local modules.
from pyxray.descriptor import \
    (Element, Reference, AtomicShell, AtomicSubshell, XrayTransition, 
     XrayTransitionSet, Notation, Language)

# Globals and constants variables.

@dataclasses.dataclass(frozen=True)
class ElementSymbol:
    reference: Reference
    element: Element
    symbol: str

    def __post_init__(self):
        if len(self.symbol) == 0 or len(self.symbol) > 3:
            raise ValueError('Symbol should be between 1 and 3 characters')
        
        if not self.symbol[0].isupper():
            raise ValueError("Symbol should start with a capital letter")

@dataclasses.dataclass(frozen=True)
class ElementName:
    reference: Reference
    element: Element
    language: Language
    name: str
    
    def __post_init__(self):
        if not self.name:
            raise ValueError('A name must be specified')

@dataclasses.dataclass(frozen=True)
class ElementAtomicWeight:
    reference: Reference
    element: Element
    value: float

    def __post_init__(self):
        if self.value <= 0.0:
            raise ValueError('Value must be greater than 0.0')

@dataclasses.dataclass(frozen=True)
class ElementMassDensity:
    reference: Reference
    element: Element
    value_kg_per_m3: float

    def __post_init__(self):
        if self.value_kg_per_m3 <= 0.0:
            raise ValueError('Value must be greater than 0.0')

@dataclasses.dataclass(frozen=True)
class AtomicShellNotation:
    reference: Reference
    atomic_shell: AtomicShell
    notation: Notation
    ascii: str
    utf16: str
    html: str
    latex: str

@dataclasses.dataclass(frozen=True)
class AtomicSubshellNotation:
    reference: Reference
    atomic_subshell: AtomicSubshell
    notation: Notation
    ascii: str
    utf16: str
    html: str
    latex: str

@dataclasses.dataclass(frozen=True)
class AtomicSubshellBindingEnergy:
    reference: Reference
    element: Element
    atomic_subshell: AtomicSubshell
    value_eV: float

@dataclasses.dataclass(frozen=True)
class AtomicSubshellRadiativeWidth:
    reference: Reference
    element: Element
    atomic_subshell: AtomicSubshell
    value_eV: float

@dataclasses.dataclass(frozen=True)
class AtomicSubshellNonRadiativeWidth:
    reference: Reference
    element: Element
    atomic_subshell: AtomicSubshell
    value_eV: float

@dataclasses.dataclass(frozen=True)
class AtomicSubshellOccupancy:
    reference: Reference
    element: Element
    atomic_subshell: AtomicSubshell
    value: float

@dataclasses.dataclass(frozen=True)
class XrayTransitionNotation:
    reference: Reference
    xraytransition: XrayTransition
    notation: Notation
    ascii: str
    utf16: str
    html: str
    latex: str

@dataclasses.dataclass(frozen=True)
class XrayTransitionEnergy:
    reference: Reference
    element: Element
    xraytransition: XrayTransition
    value_eV: float

@dataclasses.dataclass(frozen=True)
class XrayTransitionProbability:
    reference: Reference
    element: Element
    xraytransition: XrayTransition
    value: float

@dataclasses.dataclass(frozen=True)
class XrayTransitionRelativeWeight:
    reference: Reference
    element: Element
    xraytransition: XrayTransition
    value: float

@dataclasses.dataclass(frozen=True)
class XrayTransitionSetNotation:
    reference: Reference
    xraytransitionset: XrayTransitionSet
    notation: Notation
    ascii: str
    utf16: str
    html: str
    latex: str

@dataclasses.dataclass(frozen=True)
class XrayTransitionSetEnergy:
    reference: Reference
    element: Element
    xraytransitionset: XrayTransitionSet
    value_eV: float

@dataclasses.dataclass(frozen=True)
class XrayTransitionSetRelativeWeight:
    reference: Reference
    element: Element
    xraytransitionset: XrayTransitionSet
    value: float
