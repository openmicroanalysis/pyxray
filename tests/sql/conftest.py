""""""

# Standard library modules.

# Third party modules.
import pytest
import sqlalchemy

# Local modules.
from pyxray.sql.build import SqlDatabaseBuilder
from pyxray.parser.base import _Parser
import pyxray.descriptor as descriptor
import pyxray.property as property

# Globals and constants variables.
K = descriptor.AtomicSubshell(1, 0, 1)
L3 = descriptor.AtomicSubshell(2, 1, 3)
L2 = descriptor.AtomicSubshell(2, 1, 1)

class MockParser(_Parser):

    def __iter__(self):
        reference = descriptor.Reference('lee1966')
        reference2 = descriptor.Reference('doe2016')
        element = descriptor.Element(118)
        atomic_shell = descriptor.AtomicShell(1)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        transitionset = descriptor.XrayTransition(2, 1, None, K)
        notation = descriptor.Notation('mock')
        notation_iupac = descriptor.Notation('iupac')
        language = descriptor.Language('en')

        yield property.ElementName(reference, element, language, 'Vibranium')
        yield property.ElementSymbol(reference, element, 'Vi')
        yield property.ElementAtomicWeight(reference, element, 999.1)
        yield property.ElementAtomicWeight(reference2, element, 111.1)
        yield property.ElementMassDensity(reference, element, 999.2)

        yield property.AtomicShellNotation(reference, atomic_shell, notation, 'a', 'b', 'c', 'd')

        yield property.AtomicSubshellNotation(reference, K, notation, 'a', 'b', 'c', 'd')
        yield property.AtomicSubshellBindingEnergy(reference, element, K, 0.1)
        yield property.AtomicSubshellRadiativeWidth(reference, element, K, 0.01)
        yield property.AtomicSubshellNonRadiativeWidth(reference, element, K, 0.001)
        yield property.AtomicSubshellOccupancy(reference, element, K, 1)

        yield property.XrayTransitionNotation(reference, transition, notation, 'a', 'b', 'c', 'd')
        yield property.XrayTransitionNotation(reference, transition, notation_iupac, 'aa', 'bb', 'cc', 'dd')
        yield property.XrayTransitionEnergy(reference, element, transition, 0.2)
        yield property.XrayTransitionProbability(reference, element, transition, 0.02)
        yield property.XrayTransitionRelativeWeight(reference, element, transition, 0.002)

        yield property.XrayTransitionNotation(reference, transition2, notation, 'e', 'f', 'g', 'h')
        yield property.XrayTransitionEnergy(reference, element, transition2, 0.4)
        yield property.XrayTransitionProbability(reference, element, transition2, 0.04)
        yield property.XrayTransitionRelativeWeight(reference, element, transition2, 0.004)

        yield property.XrayTransitionNotation(reference, transitionset, notation, 'i', 'j', 'k', 'l')
        yield property.XrayTransitionEnergy(reference, element, transitionset, 0.6)
        yield property.XrayTransitionProbability(reference, element, transitionset, 0.06)
        yield property.XrayTransitionRelativeWeight(reference, element, transitionset, 0.006)

class MockBadParser(_Parser):

    def __iter__(self):
        raise Exception

class MockSqliteDatabaseBuilder(SqlDatabaseBuilder):

    def __init__(self, filepath=None, badparser=False):
        super().__init__(filepath)
        self.badparser = badparser

    def _find_parsers(self):
        super()._find_parsers() # Ignore output, only for coverage

        if self.badparser:
            return [('bad', MockBadParser())]
        else:
            return [('mock', MockParser())]

@pytest.fixture(scope='session')
def builder(tmp_path_factory):
    engine = sqlalchemy.create_engine('sqlite:///' + str(tmp_path_factory.mktemp('test').joinpath('pyxray.sql')))

    builder = MockSqliteDatabaseBuilder(engine)
    builder.build()

    return builder
