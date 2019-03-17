""""""

# Standard library modules.

# Third party modules.
import pytest

import sqlalchemy

# Local modules.
from pyxray.sql.build import SqlDatabaseBuilder
from pyxray.parser.parser import _Parser
import pyxray.descriptor as descriptor
import pyxray.property as property

# Globals and constants variables.

class MockParser(_Parser):
    K = descriptor.AtomicSubshell(1, 0, 1)
    L3 = descriptor.AtomicSubshell(2, 1, 3)
    L2 = descriptor.AtomicSubshell(2, 1, 1)

    def __iter__(self):
        reference = descriptor.Reference('lee1966')
        reference2 = descriptor.Reference('doe2016')
        element = descriptor.Element(118)
        atomic_shell = descriptor.AtomicShell(1)
        transition = descriptor.XrayTransition(self.L3, self.K)
        transition2 = descriptor.XrayTransition(self.L2, self.K)
        transitionset = descriptor.XrayTransitionSet([transition, transition2])
        notation = descriptor.Notation('mock')
        notation_iupac = descriptor.Notation('iupac')
        language = descriptor.Language('en')

        yield property.ElementName(reference, element, language, 'Vibranium')
        yield property.ElementSymbol(reference, element, 'Vi')
        yield property.ElementAtomicWeight(reference, element, 999.1)
        yield property.ElementAtomicWeight(reference2, element, 111.1)
        yield property.ElementMassDensity(reference, element, 999.2)

        yield property.AtomicShellNotation(reference, atomic_shell, notation,
                                           'a', 'b', 'c', 'd')

        yield property.AtomicSubshellNotation(reference, self.K, notation,
                                              'a', 'b', 'c', 'd')
        yield property.AtomicSubshellBindingEnergy(reference, element, self.K, 0.1)
        yield property.AtomicSubshellRadiativeWidth(reference, element, self.K, 0.01)
        yield property.AtomicSubshellNonRadiativeWidth(reference, element, self.K, 0.001)
        yield property.AtomicSubshellOccupancy(reference, element, self.K, 1)

        yield property.XrayTransitionNotation(reference, transition, notation,
                                              'a', 'b', 'c', 'd')
        yield property.XrayTransitionNotation(reference, transition2, notation,
                                              'e', 'f', 'g', 'h')
        yield property.XrayTransitionNotation(reference, transition, notation_iupac,
                                              'aa', 'bb', 'cc', 'dd')
        yield property.XrayTransitionEnergy(reference, element, transition, 0.2)
        yield property.XrayTransitionEnergy(reference, element, transition2, 0.4)
        yield property.XrayTransitionProbability(reference, element, transition, 0.02)
        yield property.XrayTransitionProbability(reference, element, transition2, 0.04)
        yield property.XrayTransitionRelativeWeight(reference, element, transition, 0.002)
        yield property.XrayTransitionRelativeWeight(reference, element, transition2, 0.004)

#        yield property.XrayTransitionSetNotation(reference, transitionset, notation,
#                                                 'a', 'b', 'c', 'd')
#        yield property.XrayTransitionSetEnergy(reference, element, transitionset, 0.3)
#        yield property.XrayTransitionSetRelativeWeight(reference, element, transitionset, 0.003)

class MockBadParser(_Parser):

    def __iter__(self):
        raise Exception

@pytest.fixture
def engine():
    return sqlalchemy.create_engine('sqlite:///:memory:')

@pytest.fixture
def builder(engine):
    return SqlDatabaseBuilder(engine)

def test_builder_require_table(builder):
    builder.require_table(property.ElementSymbol)
    assert len(builder.metadata.tables) == 3
    assert 'reference' in builder.metadata.tables
    assert 'element' in builder.metadata.tables
    assert 'element_symbol' in builder.metadata.tables

def test_builder_insert_descriptor(builder):
    builder.insert(descriptor.Element(5))
    assert builder._get_row(descriptor.Element(5)) == 1
    assert builder._get_row(descriptor.Element(6)) is None

def test_builder_insert_property(builder):
    reference = descriptor.Reference('doe2016')
    element = descriptor.Element(5)
    prop = property.ElementSymbol(reference, element, 'B')
    builder.insert(prop)

    assert builder._get_row(reference) == 1
    assert builder._get_row(element) == 1
    assert builder._get_row(prop) == 1

def test_builder_build(builder):
    builder._find_parsers = lambda: [('mock', MockParser())]
    builder.build()

