""""""

# Standard library modules.

# Third party modules.
import pytest

import sqlalchemy

# Local modules.
from pyxray.sql.test_build import MockParser
from pyxray.sql.build import SqlDatabaseBuilder
from pyxray.sql.data import SqlDatabase
import pyxray.descriptor as descriptor
from pyxray.base import NotFound

# Globals and constants variables.

@pytest.fixture(scope='module')
def engine():
    return sqlalchemy.create_engine('sqlite:///:memory:')

@pytest.fixture(scope='module')
def database(engine):
    builder = SqlDatabaseBuilder(engine)
    builder._find_parsers = lambda: [('mock', MockParser())]
    builder.build()

    return SqlDatabase(engine)

@pytest.mark.parametrize('element', [118, 'Vi', 'Vibranium'])
def test_element(database, element):
    assert database.element(element) == descriptor.Element(118)

@pytest.mark.parametrize('element', ['Al', 13, 'Aluminum'])
def test_element_notfound(database, element):
    with pytest.raises(NotFound):
        database.element(element)

@pytest.mark.parametrize('element', [118, 'Vi', 'Vibranium'])
def test_element_atomic_number(database, element):
    assert database.element_atomic_number(element) == 118

@pytest.mark.parametrize('element', ['Al', 13, 'Aluminum'])
def test_element_atomic_number_notfound(database, element):
    with pytest.raises(NotFound):
        database.element_atomic_number(element)

@pytest.mark.parametrize('element', [118, 'Vi', 'Vibranium'])
def test_element_symbol(database, element):
    assert database.element_symbol(element) == 'Vi'

@pytest.mark.parametrize('element', ['Al', 13, 'Aluminum'])
def test_element_symbol_notfound(database, element):
    with pytest.raises(NotFound):
        database.element_symbol(element)

@pytest.mark.parametrize('element', [118, 'Vi', 'Vibranium'])
def test_element_name(database, element):
    assert database.element_name(element, 'en') == 'Vibranium'
    assert database.element_name(element, 'en', 'lee1966') == 'Vibranium'

@pytest.mark.parametrize('element', ['Al', 13, 'Aluminum'])
def test_element_name_notfound(database, element):
    with pytest.raises(NotFound):
        database.element_name(element, 'en')

def test_element_name_notfound_wrong_language(database):
    with pytest.raises(NotFound):
        database.element_name(118, 'fr')

def test_element_name_notfound_wrong_reference(database):
    with pytest.raises(NotFound):
        database.element_name(118, 'en', 'doe2016')

def test_element_atomic_weight_no_reference(database):
    assert database.element_atomic_weight(118) == pytest.approx(999.1, abs=1e-2)

def test_element_atomic_weight_lee1966(database):
    assert database.element_atomic_weight(118, 'lee1966') == pytest.approx(999.1, abs=1e-2)

def test_element_atomic_weight_doe2016(database):
    assert database.element_atomic_weight(118, 'doe2016') == pytest.approx(111.1, abs=1e-2)

@pytest.mark.parametrize('element', [118, 'Vi', 'Vibranium'])
def test_element_mass_density_kg_per_m3(database, element):
    assert database.element_mass_density_kg_per_m3(element) == pytest.approx(999.2, abs=1e-2)

@pytest.mark.parametrize('element', [118, 'Vi', 'Vibranium'])
def test_element_mass_density_g_per_cm3(database, element):
    assert database.element_mass_density_g_per_cm3(element) == pytest.approx(0.9992, abs=1e-4)

#def testelement_xray_transitions(self):
#    transitions = self.db.element_xray_transitions(118)
#    self.assertEqual(1, len(transitions))
#
#    K = descriptor.AtomicSubshell(1, 0, 1)
#    L3 = descriptor.AtomicSubshell(2, 1, 3)
#    expected = descriptor.XrayTransition(L3, K)
#    self.assertEqual(expected, transitions[0])
#
#def testelement_xray_transitions2(self):
#    transitions = self.db.element_xray_transitions(118, 'a')
#    self.assertEqual(1, len(transitions))
#
#    K = descriptor.AtomicSubshell(1, 0, 1)
#    L3 = descriptor.AtomicSubshell(2, 1, 3)
#    expected = descriptor.XrayTransition(L3, K)
#    self.assertEqual(expected, transitions[0])
#
#def testelement_xray_transition(self):
#    transition = self.db.element_xray_transition(118, 'a')
#
#    K = descriptor.AtomicSubshell(1, 0, 1)
#    L3 = descriptor.AtomicSubshell(2, 1, 3)
#    expected = descriptor.XrayTransition(L3, K)
#    self.assertEqual(expected, transition)
#
#    self.assertRaises(NotFound, self.db.element_xray_transition, 1, 'a')
#    self.assertRaises(NotFound, self.db.element_xray_transition, 118, 'g')

@pytest.mark.parametrize('atomic_shell', [1, 'a', 'b'])
def test_atomic_shell(database, atomic_shell):
    assert database.atomic_shell(atomic_shell) == descriptor.AtomicShell(1)

@pytest.mark.parametrize('atomic_shell', ['c', 3])
def test_atomic_shell_notfound(database, atomic_shell):
    with pytest.raises(NotFound):
        database.atomic_shell(atomic_shell)

@pytest.mark.parametrize('encoding,expected', [('ascii', 'a'), ('utf16', 'b'), ('html', 'c'), ('latex', 'd')])
def test_atomic_shell_notation(database, encoding, expected):
    assert database.atomic_shell_notation(1, 'mock', encoding) == expected

@pytest.mark.parametrize('atomic_subshell', [descriptor.AtomicSubshell(1, 0, 1), (1, 0, 1), 'a', 'b'])
def test_atomic_subshell(database, atomic_subshell):
    assert database.atomic_subshell(atomic_subshell) == descriptor.AtomicSubshell(1, 0, 1)

@pytest.mark.parametrize('atomic_subshell', ['c', (3, 3, 3)])
def test_atomic_subshell_notfound(database, atomic_subshell):
    with pytest.raises(NotFound):
        database.atomic_subshell(atomic_subshell)

@pytest.mark.parametrize('encoding,expected', [('ascii', 'a'), ('utf16', 'b'), ('html', 'c'), ('latex', 'd')])
def testatomic_subshell_notation(database, encoding, expected):
    assert database.atomic_subshell_notation(descriptor.AtomicSubshell(1, 0, 1), 'mock', encoding) == expected

@pytest.mark.parametrize('atomic_subshell', [descriptor.AtomicSubshell(1, 0, 1), (1, 0, 1), 'a', 'b'])
def test_atomic_subshell_binding_energy_eV(database, atomic_subshell):
    assert database.atomic_subshell_binding_energy_eV(118, atomic_subshell) == pytest.approx(0.1, abs=1e-4)

@pytest.mark.parametrize('atomic_subshell', [descriptor.AtomicSubshell(1, 0, 1), (1, 0, 1), 'a', 'b'])
def testatomic_subshell_radiative_width_eV(database, atomic_subshell):
    assert database.atomic_subshell_radiative_width_eV(118, atomic_subshell) == pytest.approx(0.01, abs=1e-4)

@pytest.mark.parametrize('atomic_subshell', [descriptor.AtomicSubshell(1, 0, 1), (1, 0, 1), 'a', 'b'])
def testatomic_subshell_nonradiative_width_eV(database, atomic_subshell):
    assert database.atomic_subshell_nonradiative_width_eV(118, atomic_subshell) == pytest.approx(0.001, abs=1e-4)

@pytest.mark.parametrize('atomic_subshell', [descriptor.AtomicSubshell(1, 0, 1), (1, 0, 1), 'a', 'b'])
def testatomic_subshell_occupancy(database, atomic_subshell):
    assert database.atomic_subshell_occupancy(118, atomic_subshell) == 1

@pytest.mark.parametrize('xray_transition', ['a', ((2, 1, 3), (1, 0, 1)), (MockParser.L3, MockParser.K), descriptor.XrayTransition(MockParser.L3, MockParser.K)])
def test_xray_transition(database, xray_transition):
    assert database.xray_transition(xray_transition) == descriptor.XrayTransition(MockParser.L3, MockParser.K)

@pytest.mark.parametrize('encoding,expected', [('ascii', 'a'), ('utf16', 'b'), ('html', 'c'), ('latex', 'd')])
def test_xray_transition_notation(database, encoding, expected):
    xray_transition = descriptor.XrayTransition(MockParser.L3, MockParser.K)
    assert database.xray_transition_notation(xray_transition, 'mock', encoding) == expected

@pytest.mark.parametrize('xray_transition', ['a', ((2, 1, 3), (1, 0, 1)), (MockParser.L3, MockParser.K), descriptor.XrayTransition(MockParser.L3, MockParser.K)])
def test_xray_transition_energy_eV_KL3(database, xray_transition):
    assert database.xray_transition_energy_eV(118, xray_transition) == pytest.approx(0.2, abs=1e-4)

@pytest.mark.parametrize('xray_transition', ['e', ((2, 1, 1), (1, 0, 1)), (MockParser.L2, MockParser.K), descriptor.XrayTransition(MockParser.L2, MockParser.K)])
def test_xray_transition_energy_eV_KL2(database, xray_transition):
    assert database.xray_transition_energy_eV(118, xray_transition) == pytest.approx(0.4, abs=1e-4)

@pytest.mark.parametrize('xray_transition', ['a', ((2, 1, 3), (1, 0, 1)), (MockParser.L3, MockParser.K), descriptor.XrayTransition(MockParser.L3, MockParser.K)])
def test_xray_transition_probability(database, xray_transition):
    assert database.xray_transition_probability(118, xray_transition) == pytest.approx(0.02, abs=1e-4)

@pytest.mark.parametrize('xray_transition', ['a', ((2, 1, 3), (1, 0, 1)), (MockParser.L3, MockParser.K), descriptor.XrayTransition(MockParser.L3, MockParser.K)])
def test_xray_transition_relative_weight(database, xray_transition):
    assert database.xray_transition_relative_weight(118, xray_transition) == pytest.approx(0.002, abs=1e-4)

#def test_xray_line(database):
#    xrayline = database.xray_line(118, 'aa')
#
#    assert xrayline.element.atomic_number == 118
#    assert len(xrayline.transitions) == 1
#    assert xrayline.iupac == 'Vi bb'
#    assert xrayline.siegbahn == 'Vi bb'