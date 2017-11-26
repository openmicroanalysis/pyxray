#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil
import sqlite3

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
import pyxray.property as property
import pyxray.descriptor as descriptor
from pyxray.sql.build import SqliteDatabaseBuilder

# Globals and constants variables.

class MockParser(_Parser):

    def __iter__(self):
        reference = descriptor.Reference('lee1966')
        reference2 = descriptor.Reference('doe2016')
        element = descriptor.Element(118)
        atomic_shell = descriptor.AtomicShell(1)
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
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

        yield property.AtomicSubshellNotation(reference, K, notation,
                                              'a', 'b', 'c', 'd')
        yield property.AtomicSubshellBindingEnergy(reference, element, K, 0.1)
        yield property.AtomicSubshellRadiativeWidth(reference, element, K, 0.01)
        yield property.AtomicSubshellNonRadiativeWidth(reference, element, K, 0.001)
        yield property.AtomicSubshellOccupancy(reference, element, K, 1)

        yield property.XrayTransitionNotation(reference, transition, notation,
                                              'a', 'b', 'c', 'd')
        yield property.XrayTransitionNotation(reference, transition, notation_iupac,
                                              'aa', 'bb', 'cc', 'dd')
        yield property.XrayTransitionEnergy(reference, element, transition, 0.2)
        yield property.XrayTransitionProbability(reference, element, transition, 0.02)
        yield property.XrayTransitionRelativeWeight(reference, element, transition, 0.002)

        yield property.XrayTransitionSetNotation(reference, transitionset, notation,
                                                 'a', 'b', 'c', 'd')
        yield property.XrayTransitionSetEnergy(reference, element, transitionset, 0.3)
        yield property.XrayTransitionSetRelativeWeight(reference, element, transitionset, 0.003)

class MockBadParser(_Parser):

    def __iter__(self):
        raise Exception

class MockSqliteDatabaseBuilder(SqliteDatabaseBuilder):

    def __init__(self, filepath=None, badparser=False):
        super().__init__(filepath)
        self.badparser = badparser

    def _find_parsers(self):
        super()._find_parsers() # Ignore output, only for coverage

        if self.badparser:
            return [('bad', MockBadParser())]
        else:
            return [('mock', MockParser())]

class Test_DatabaseBuilder(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.tmpdir = tempfile.mkdtemp()

        filepath = os.path.join(self.tmpdir, 'pyxray.sql')
        self.builder = MockSqliteDatabaseBuilder(filepath)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testbuild(self):
        self.builder.build()

        filepath = os.path.join(self.tmpdir, 'pyxray.sql')
        self.assertTrue(os.path.exists(filepath))

        conn = sqlite3.connect(filepath)
        command = "SELECT count(*) FROM sqlite_master WHERE type = 'table'"
        ntable, = conn.execute(command).fetchone()
        self.assertEqual(26, ntable)

    def testbackup(self):
        self.builder.build()
        self.builder.build()

        filepath = os.path.join(self.tmpdir, 'pyxray.sql')
        self.assertTrue(os.path.exists(filepath))

        filepath = os.path.join(self.tmpdir, 'pyxray.sql.old')
        self.assertTrue(os.path.exists(filepath))

    def testexception(self):
        filepath = os.path.join(self.tmpdir, 'pyxray.sql')
        builder = MockSqliteDatabaseBuilder(filepath, badparser=True)
        self.assertRaises(Exception, builder.build)

    def testexception_revert(self):
        self.builder.build()

        filepath = os.path.join(self.tmpdir, 'pyxray.sql')
        builder = MockSqliteDatabaseBuilder(filepath, badparser=True)
        self.assertRaises(Exception, builder.build)

    def testdefault_database_filepath(self):
        builder = MockSqliteDatabaseBuilder()

        filename = os.path.basename(builder._filepath)
        self.assertEqual('pyxray.sql', filename)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
