#!/usr/bin/env python
""" """

# Standard library modules.
import dataclasses

# Third party modules.
import pytest

# Local modules.
from pyxray.descriptor import Element, AtomicShell, AtomicSubshell, Reference, XrayLine, XrayTransition, Language, Notation

# Globals and constants variables.

@pytest.fixture
def element():
    return Element(6)

def test_element(element):
    assert element.z == 6
    assert element.atomic_number == 6

def test_element_eq(element):
    assert element == Element(6)

def test_element_hash(element):
    assert hash(element) == hash(Element(6))

def test_element_repr(element):
    assert repr(element) == 'Element(z=6)'

def test_element_validate():
    with pytest.raises(ValueError):
        Element(0)

    with pytest.raises(ValueError):
        Element(119)

def test_element_frozen(element):
    with pytest.raises(dataclasses.FrozenInstanceError):
        element.atomic_number = 7

    with pytest.raises(dataclasses.FrozenInstanceError):
        del element.atomic_number

    with pytest.raises(dataclasses.FrozenInstanceError):
        element.abc = 7

@pytest.fixture
def atomicshell():
    return AtomicShell(3)

def test_atomicshell(atomicshell):
    assert atomicshell.n == 3
    assert atomicshell.principal_quantum_number == 3

def test_atomicshell_eq(atomicshell):
    assert atomicshell == AtomicShell(3)

def test_atomicshell_hash(atomicshell):
    assert hash(atomicshell) == hash(AtomicShell(3))

def test_atomicshell_repr(atomicshell):
    assert repr(atomicshell) == 'AtomicShell(n=3)'

def test_atomicshell_validable():
    with pytest.raises(ValueError):
        AtomicShell(0)

def test_atomicshell_frozen(atomicshell):
    with pytest.raises(dataclasses.FrozenInstanceError):
        atomicshell.n = 7

    with pytest.raises(dataclasses.FrozenInstanceError):
        del atomicshell.n

    with pytest.raises(dataclasses.FrozenInstanceError):
        atomicshell.abc = 7

@pytest.fixture
def atomicsubshell():
    return AtomicSubshell(3, 0, 1)

def test_atomicsubshell(atomicsubshell):
    assert atomicsubshell.n == 3
    assert atomicsubshell.atomic_shell == AtomicShell(3)
    assert atomicsubshell.principal_quantum_number == 3
    assert atomicsubshell.l == 0
    assert atomicsubshell.azimuthal_quantum_number == 0
    assert atomicsubshell.j_n == 1
    assert atomicsubshell.total_angular_momentum_nominator == 1
    assert atomicsubshell.j == 0.5
    assert atomicsubshell.total_angular_momentum == 0.5

def test_atomicsubshell_eq(atomicsubshell):
    assert atomicsubshell == AtomicSubshell(3, 0, 1)
    assert atomicsubshell == AtomicSubshell(AtomicShell(3), 0, 1)

def test_atomicsubshell_hash(atomicsubshell):
    assert hash(atomicsubshell) == hash(AtomicSubshell(3, 0, 1))
    assert hash(atomicsubshell) == hash(AtomicSubshell(AtomicShell(3), 0, 1))

def test_atomicsubshell_repr(atomicsubshell):
    assert repr(atomicsubshell) == 'AtomicSubshell(n=3, l=0, j=0.5)'

def test_atomicsubshell_validate():
    with pytest.raises(ValueError):
        AtomicSubshell(3, 0, 5)

    with pytest.raises(ValueError):
        AtomicSubshell(3, -1, 1)

    with pytest.raises(ValueError):
        AtomicSubshell(3, 3, 1)

def test_atomicsubshell_frozen(atomicsubshell):
    with pytest.raises(dataclasses.FrozenInstanceError):
        atomicsubshell.n = 7

    with pytest.raises(dataclasses.FrozenInstanceError):
        del atomicsubshell.n

    with pytest.raises(dataclasses.FrozenInstanceError):
        atomicsubshell.abc = 7

@pytest.fixture(params=[(AtomicSubshell(2, 0, 1), AtomicSubshell(1, 0, 1)),
                        (2, 0, 1, 1, 0, 1),
                        ((2, 0, 1), (1, 0, 1)),
                        (AtomicSubshell(2, 0, 1), 1, 0, 1),
                        (2, 0, 1, AtomicSubshell(1, 0, 1))])
def xraytransition(request):
    return XrayTransition(*request.param)

def test_xraytransition(xraytransition):
    assert xraytransition.source_principal_quantum_number == 2
    assert xraytransition.source_azimuthal_quantum_number == 0
    assert xraytransition.source_total_angular_momentum_nominator == 1
    assert xraytransition.destination_principal_quantum_number == 1
    assert xraytransition.destination_azimuthal_quantum_number == 0
    assert xraytransition.destination_total_angular_momentum_nominator == 1

    assert xraytransition.source_subshell.n == 2
    assert xraytransition.source_subshell.l == 0
    assert xraytransition.source_subshell.j_n == 1
    assert xraytransition.destination_subshell.n == 1
    assert xraytransition.destination_subshell.l == 0
    assert xraytransition.destination_subshell.j_n == 1

def test_xraytransition_eq(xraytransition):
    assert xraytransition == XrayTransition((2, 0, 1), (1, 0, 1))

def test_xraytransition_hash(xraytransition):
    assert hash(xraytransition) == hash(XrayTransition((2, 0, 1), (1, 0, 1)))
    assert hash(xraytransition) == hash(XrayTransition(AtomicSubshell(2, 0, 1), AtomicSubshell(1, 0, 1)))

def test_xraytransition_repr(xraytransition):
    assert repr(xraytransition) == 'XrayTransition([n=2, l=0, j=0.5] -> [n=1, l=0, j=0.5])'

def test_xraytransition_frozen(xraytransition):
    with pytest.raises(dataclasses.FrozenInstanceError):
        xraytransition.source_subshell = AtomicSubshell(2, 0, 1)

    with pytest.raises(dataclasses.FrozenInstanceError):
        del xraytransition.source_subshell

    with pytest.raises(dataclasses.FrozenInstanceError):
        xraytransition.abc = 7

@pytest.fixture
def xraytransitionset():
    return XrayTransition(2, 1, None, 1, 0, 1) # L2 (2, 1, 0.5) and L3 (2, 1, 1.5) to K (1, 0, 0.5)

def test_xraytransitionset(xraytransitionset):
    assert xraytransitionset.source_subshell.n == 2
    assert xraytransitionset.source_subshell.l == 1
    assert xraytransitionset.source_subshell.j_n == None
    assert xraytransitionset.destination_subshell.n == 1
    assert xraytransitionset.destination_subshell.l == 0
    assert xraytransitionset.destination_subshell.j_n == 1

def test_xraytransitionset_repr(xraytransitionset):
    assert repr(xraytransitionset) == 'XrayTransition([n=2, l=1, j=*] -> [n=1, l=0, j=0.5])'

@pytest.fixture
def xrayline():
    return XrayLine(Element(118), XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1, 0.2, 0.3)

def test_xrayline(xrayline):
    assert xrayline.element.z == 118
    assert xrayline.transition == XrayTransition(2, 0, 1, 1, 0, 1)
    assert xrayline.iupac == 'a'
    assert xrayline.siegbahn == 'b'
    assert xrayline.energy_eV == pytest.approx(0.1, abs=1e-4)
    assert xrayline.probability == pytest.approx(0.2, abs=1e-4)
    assert xrayline.relative_weight == pytest.approx(0.3, abs=1e-4)

def test_xrayline_eq(xrayline):
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1)
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'z', 'b', 0.1)
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'z', 0.1)
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 99.0)
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1, 99.0)
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1, 0.2, 99.0)
    assert xrayline == XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1, 0.2, 0.3)

    assert xrayline != XrayLine(117, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1)
    assert xrayline != XrayLine(118, XrayTransition(3, 0, 1, 1, 0, 1), 'a', 'b', 0.1)

@pytest.mark.parametrize('other', [
    XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.1),
    XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'z', 'b', 0.1),
    XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'z', 0.1),
    XrayLine(118, XrayTransition(2, 0, 1, 1, 0, 1), 'a', 'b', 0.2)
])
def test_xrayline_hash(xrayline, other):
    assert hash(xrayline) == hash(other)

def test_xrayline_repr(xrayline):
    assert repr(xrayline) == 'XrayLine(a)'

def test_xrayline_frozen(xrayline):
    with pytest.raises(dataclasses.FrozenInstanceError):
        xrayline.element = 117

    with pytest.raises(dataclasses.FrozenInstanceError):
        del xrayline.element

    with pytest.raises(dataclasses.FrozenInstanceError):
        xrayline.abc = 7

@pytest.fixture
def language():
    return Language('en')

def test_language(language):
    assert language.key == 'en'

def test_language_eq(language):
    assert language == Language('en')
    assert language == Language('EN')
    assert language != Language('fr')

def test_language_hash(language):
    assert hash(language) == hash(Language('EN'))

def test_language_repr(language):
    assert repr(language) == 'Language(en)'

def test_language_validate():
    with pytest.raises(ValueError):
        Language('english')

    with pytest.raises(ValueError):
        Language('e')

def test_language_frozen(language):
    with pytest.raises(dataclasses.FrozenInstanceError):
        language.key = 'fr'

    with pytest.raises(dataclasses.FrozenInstanceError):
        del language.key

    with pytest.raises(dataclasses.FrozenInstanceError):
        language.abc = 7

@pytest.fixture
def notation():
    return Notation('foo')

def test_notation(notation):
    assert notation.key == 'foo'

def test_notation_eq(notation):
    assert notation == Notation('foo')
    assert notation == Notation('FOO')
    assert notation != Notation('bar')

def test_notation_hash(notation):
    assert hash(notation) == hash(Notation('FOO'))

def test_notation_repr(notation):
    assert repr(notation) == 'Notation(foo)'

def test_notation_validate():
    with pytest.raises(ValueError):
        Notation('')

def test_notation_frozen(notation):
    with pytest.raises(dataclasses.FrozenInstanceError):
        notation.key = 'bar'

    with pytest.raises(dataclasses.FrozenInstanceError):
        del notation.key

    with pytest.raises(dataclasses.FrozenInstanceError):
        notation.abc = 7

@pytest.fixture
def reference():
    return Reference('doe2016')

def test_reference(reference):
    assert reference.bibtexkey == 'doe2016'

def test_reference_eq(reference):
    assert reference == Reference('doe2016')
    assert reference != Reference('doe2016', year=2016)

def test_reference_hash(reference):
    assert hash(reference) == hash(Reference('doe2016'))

def test_reference_repr(reference):
    assert repr(reference) == 'Reference(doe2016)'

def test_reference_frozen(reference):
    with pytest.raises(dataclasses.FrozenInstanceError):
        reference.author = 'bar'

    with pytest.raises(dataclasses.FrozenInstanceError):
        del reference.author

    with pytest.raises(dataclasses.FrozenInstanceError):
        reference.abc = 7
