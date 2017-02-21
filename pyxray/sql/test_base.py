#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil

# Third party modules.
from sqlalchemy import create_engine

# Local modules.
from pyxray.base import NotFound
import pyxray.descriptor as descriptor
from pyxray.sql.base import SqlEngineDatabaseMixin
from pyxray.sql.test_build import MockSqliteDatabaseBuilder

# Globals and constants variables.

class MockSqliteEngineDatabase(SqlEngineDatabaseMixin):
    pass

class TestSqlEngineDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.tmpdir = tempfile.mkdtemp()
        cls.filepath = os.path.join(cls.tmpdir, 'pyxray.sql')
        builder = MockSqliteDatabaseBuilder(cls.filepath)
        builder.build()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.engine = create_engine('sqlite:///' + self.filepath)
        self.mock = MockSqliteEngineDatabase()

    def test_get_element_id(self):
        self.assertEqual(1, self.mock._get_element_id(self.engine, 'VI'))
        self.assertEqual(1, self.mock._get_element_id(self.engine, 'vi'))
        self.assertEqual(1, self.mock._get_element_id(self.engine, 'Vi'))

        self.assertEqual(1, self.mock._get_element_id(self.engine, 'Vibranium'))
        self.assertEqual(1, self.mock._get_element_id(self.engine, 'VIBRANIUM'))
        self.assertEqual(1, self.mock._get_element_id(self.engine, 'vibranium'))

        self.assertEqual(1, self.mock._get_element_id(self.engine, 118))

        class MockAtomicNumber:
            def __init__(self):
                self.atomic_number = 118
        obj = MockAtomicNumber()
        self.assertEqual(1, self.mock._get_element_id(self.engine, obj))

        class MockZ:
            def __init__(self):
                self.z = 118
        obj = MockZ()
        self.assertEqual(1, self.mock._get_element_id(self.engine, obj))

        self.assertRaises(NotFound, self.mock._get_element_id, self.engine, 'foo')

    def test_get_atomic_shell_id(self):
        self.assertEqual(1, self.mock._get_atomic_shell_id(self.engine, 1))

        self.assertEqual(1, self.mock._get_atomic_shell_id(self.engine, 'a'))
        self.assertEqual(1, self.mock._get_atomic_shell_id(self.engine, 'b'))

        atomic_shell = descriptor.AtomicShell(1)
        self.assertEqual(1, self.mock._get_atomic_shell_id(self.engine, atomic_shell))

        self.assertRaises(NotFound, self.mock._get_atomic_shell_id, self.engine, 7)

    def test_get_atomic_subshell_id(self):
        self.assertEqual(1, self.mock._get_atomic_subshell_id(self.engine, (1, 0, 1)))

        self.assertEqual(1, self.mock._get_atomic_subshell_id(self.engine, 'a'))
        self.assertEqual(1, self.mock._get_atomic_subshell_id(self.engine, 'b'))

        atomic_shell = descriptor.AtomicSubshell(1, 0, 1)
        self.assertEqual(1, self.mock._get_atomic_subshell_id(self.engine, atomic_shell))

        self.assertRaises(NotFound, self.mock._get_atomic_subshell_id, self.engine, (7, 0, 1))

    def test_get_xray_transition_id(self):
        self.assertEqual(1, self.mock._get_xray_transition_id(self.engine, 'a'))
        self.assertEqual(1, self.mock._get_xray_transition_id(self.engine, 'b'))

        K = descriptor.AtomicSubshell(1, 0, 1)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        self.assertEqual(1, self.mock._get_xray_transition_id(self.engine, (L3, K)))
        self.assertEqual(2, self.mock._get_xray_transition_id(self.engine, (L2, K)))

        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        self.assertEqual(1, self.mock._get_xray_transition_id(self.engine, transition))
        self.assertEqual(2, self.mock._get_xray_transition_id(self.engine, transition2))

    def test_get_xray_transitionset_id(self):
        self.assertEqual(1, self.mock._get_xray_transitionset_id(self.engine, 'a'))
        self.assertEqual(1, self.mock._get_xray_transitionset_id(self.engine, 'b'))

        K = descriptor.AtomicSubshell(1, 0, 1)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        transitionset = descriptor.XrayTransitionSet([transition, transition2])

        self.assertEqual(1, self.mock._get_xray_transitionset_id(self.engine, [(L3, K), (L2, K)]))
        self.assertEqual(1, self.mock._get_xray_transitionset_id(self.engine, transitionset))

    def test_get_xray_transitionset_id_exception(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.XrayTransition(L3, K)
        transitionset = descriptor.XrayTransitionSet([transition])

        self.assertRaises(NotFound, self.mock._get_xray_transitionset_id, self.engine, transitionset)

    def test_get_notation_id(self):
        self.assertEqual(1, self.mock._get_notation_id(self.engine, 'mock'))

        notation = descriptor.Notation('mock')
        self.assertEqual(1, self.mock._get_notation_id(self.engine, notation))

    def test_get_language_id(self):
        self.assertEqual(1, self.mock._get_language_id(self.engine, 'en'))

        notation = descriptor.Language('en')
        self.assertEqual(1, self.mock._get_language_id(self.engine, notation))

    def test_get_reference_id(self):
        self.assertEqual(1, self.mock._get_reference_id(self.engine, 'lee1966'))

        notation = descriptor.Reference('lee1966')
        self.assertEqual(1, self.mock._get_reference_id(self.engine, notation))





if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
