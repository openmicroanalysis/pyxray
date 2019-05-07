""""""

# Standard library modules.
import pickle
import copy

# Third party modules.
import pytest

# Local modules.
import pyxray
from pyxray.composition import Composition, convert_atomic_to_mass_fractions, convert_mass_to_atomic_fractions

# Globals and constants variables.

@pytest.fixture
def al2o3():
    return Composition.from_formula('Al2O3')

def test_convert_al2o3(al2o3):
    atomic_fractions = al2o3.atomic_fractions

    mass_fractions = convert_atomic_to_mass_fractions(atomic_fractions)
    assert mass_fractions[13] == pytest.approx(0.52925, 1e-4)
    assert mass_fractions[8] == pytest.approx(0.47075, 1e-4)

    atomic_fractions2 = convert_mass_to_atomic_fractions(mass_fractions)
    assert atomic_fractions2[13] == pytest.approx(atomic_fractions2[13], 1e-4)
    assert atomic_fractions2[8] == pytest.approx(atomic_fractions2[8], 1e-4)

@pytest.mark.parametrize('z', [5, 26, 92])
def test_from_pure(z):
    comp = Composition.from_pure(z)

    assert comp.mass_fractions[z] == pytest.approx(1.0, 1e-4)
    assert comp.atomic_fractions[z] == pytest.approx(1.0, 1e-4)
    assert comp.formula == pyxray.element_symbol(z)
    assert comp.is_normalized()

@pytest.mark.parametrize('formula', ['Al2Na3B12', 'Al2 Na3 B12', 'Al2.0 Na3.0 B12.0'])
def test_from_formula(formula):
    comp = Composition.from_formula(formula)

    assert comp.mass_fractions[13] == pytest.approx(0.21358626371988801, 1e-4)
    assert comp.mass_fractions[11] == pytest.approx(0.27298103136883051, 1e-4)
    assert comp.mass_fractions[5] == pytest.approx(0.51343270491128157, 1e-4)

    assert comp.atomic_fractions[13] == pytest.approx(2 / 17, 1e-4)
    assert comp.atomic_fractions[11] == pytest.approx(3 / 17, 1e-4)
    assert comp.atomic_fractions[5] == pytest.approx(12 / 17, 1e-4)

    assert comp.formula == 'Al2Na3B12'

    assert comp.is_normalized()

@pytest.mark.parametrize('formula', ['Al', 'Al2', 'Al3.0'])
def test_from_formula_pure(formula):
    comp = Composition.from_formula(formula)

    assert comp.mass_fractions[13] == pytest.approx(1.0, 1e-4)
    assert comp.atomic_fractions[13] == pytest.approx(1.0, 1e-4)
    assert comp.formula == 'Al'
    assert comp.is_normalized()

@pytest.mark.parametrize('z', range(1, 100))
def test_from_formula_symbol(z):
    formula = pyxray.element_symbol(z)
    comp = Composition.from_formula(formula)
    assert comp.formula == formula

def test_from_formula_exception():
    with pytest.raises(Exception):
        Composition.from_formula('Aq2 Na3 B12')

def test_from_massfractions():
    comp = Composition.from_mass_fractions({13: 0.52925, 8: 0.47075})

    assert comp.mass_fractions[13] == pytest.approx(0.52925, 1e-4)
    assert comp.mass_fractions[8] == pytest.approx(0.47075, 1e-4)

    assert comp.atomic_fractions[13] == pytest.approx(0.4, 1e-4)
    assert comp.atomic_fractions[8] == pytest.approx(0.6, 1e-4)

    assert comp.is_normalized()

def test_from_massfractions_unnormalized():
    comp = Composition.from_mass_fractions({13: 0.52925, 8: 0.3})

    assert comp.mass_fractions[13] == pytest.approx(0.52925, 1e-4)
    assert comp.mass_fractions[8] == pytest.approx(0.3, 1e-4)

    assert comp.atomic_fractions[13] == pytest.approx(0.51127, 1e-4)
    assert comp.atomic_fractions[8] == pytest.approx(0.48873, 1e-4)

    assert not comp.is_normalized()

def test_from_massfractions_wildcard():
    comp = Composition.from_mass_fractions({13: 0.52925, 8: '?'})

    assert comp.mass_fractions[13] == pytest.approx(0.52925, 1e-4)
    assert comp.mass_fractions[8] == pytest.approx(0.47075, 1e-4)

    assert comp.atomic_fractions[13] == pytest.approx(0.4, 1e-4)
    assert comp.atomic_fractions[8] == pytest.approx(0.6, 1e-4)

    assert comp.is_normalized()

def test_eq(al2o3):
    assert al2o3 == Composition.from_atomic_fractions({13: 0.4, 8: 0.6})

def test_ne(al2o3):
    assert al2o3 != Composition.from_mass_fractions({13: 0.52925, 8: 0.47075})

def test_hash1(al2o3):
    assert hash(al2o3) == hash(Composition.from_atomic_fractions({13: 0.4, 8: 0.6}))

def test_hash2(al2o3):
    assert hash(al2o3) != hash(Composition.from_mass_fractions({13: 0.52925, 8: 0.47075}))

def test_mass_fractions(al2o3):
    with pytest.raises(TypeError):
        al2o3.mass_fractions[13] = 0.5

def test_atomic_fractions(al2o3):
    with pytest.raises(TypeError):
        al2o3.atomic_fractions[13] = 0.5

def test_formula(al2o3):
    assert al2o3.formula == 'Al2O3'

    comp = Composition.from_atomic_fractions(al2o3.atomic_fractions)
    assert comp.formula == 'Al2O3'

    comp = Composition.from_mass_fractions(al2o3.mass_fractions)
    assert comp.formula == 'Al2O3'

def test__contains__(al2o3):
    assert 13 in al2o3
    assert 8 in al2o3

def test_inner_repr(al2o3):
    assert 'Al: 0.5293, O: 0.4707' == al2o3.inner_repr()

def test__init__():
    with pytest.raises(TypeError):
        Composition(None, {}, {}, 'foo')

def test_pickle(al2o3):
    s = pickle.dumps(al2o3)
    assert al2o3 == pickle.loads(s)

def test_copy(al2o3):
    assert al2o3 == copy.copy(al2o3)

def test_deepcopy(al2o3):
    assert al2o3 == copy.deepcopy(al2o3)
