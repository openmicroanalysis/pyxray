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
import pyxray.descriptor as descriptor
from pyxray.sql.data import SqlEngineDatabase
from pyxray.sql.test_build import MockSqliteDatabaseBuilder

# Globals and constants variables.

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

        engine = create_engine('sqlite:///' + self.filepath)
        self.db = SqlEngineDatabase(engine)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testelement_atomic_number(self):
        self.assertEqual(118, self.db.element_atomic_number('Vi'))

    def testelement_symbol(self):
        self.assertEqual('Vi', self.db.element_symbol(118))

    def testelement_name(self):
        self.assertEqual('Vibranium', self.db.element_name(118, 'en'))

    def testelement_atomic_weight(self):
        self.assertAlmostEqual(999.1, self.db.element_atomic_weight(118), 2)
        self.assertAlmostEqual(999.1, self.db.element_atomic_weight(118, 'lee1966'), 2)
        self.assertAlmostEqual(111.1, self.db.element_atomic_weight(118, 'doe2016'), 2)

        self.db.set_default_reference('element_atomic_weight', 'doe2016')
        self.assertAlmostEqual(111.1, self.db.element_atomic_weight(118), 2)

    def testelement_mass_density_kg_per_m3(self):
        self.assertAlmostEqual(999.2, self.db.element_mass_density_kg_per_m3(118), 2)

    def testelement_mass_density_g_per_cm3(self):
        self.assertAlmostEqual(0.9992, self.db.element_mass_density_g_per_cm3(118), 4)

    def testatomic_shell_notation(self):
        self.assertEqual('a', self.db.atomic_shell_notation(1, 'mock', 'ascii'))
        self.assertEqual('b', self.db.atomic_shell_notation(1, 'mock', 'utf16'))
        self.assertEqual('c', self.db.atomic_shell_notation(1, 'mock', 'html'))
        self.assertEqual('d', self.db.atomic_shell_notation(1, 'mock', 'latex'))

    def testatomic_subshell_notation(self):
        ashell = descriptor.AtomicSubshell(1, 0, 1)
        self.assertEqual('a', self.db.atomic_subshell_notation(ashell, 'mock', 'ascii'))
        self.assertEqual('b', self.db.atomic_subshell_notation(ashell, 'mock', 'utf16'))
        self.assertEqual('c', self.db.atomic_subshell_notation(ashell, 'mock', 'html'))
        self.assertEqual('d', self.db.atomic_subshell_notation(ashell, 'mock', 'latex'))

    def testatomic_subshell_binding_energy_eV(self):
        ashell = descriptor.AtomicSubshell(1, 0, 1)
        self.assertAlmostEqual(0.1, self.db.atomic_subshell_binding_energy_eV(118, ashell), 4)

    def testatomic_subshell_radiative_width_eV(self):
        ashell = descriptor.AtomicSubshell(1, 0, 1)
        self.assertAlmostEqual(0.01, self.db.atomic_subshell_radiative_width_eV(118, ashell), 4)

    def testatomic_subshell_nonradiative_width_eV(self):
        ashell = descriptor.AtomicSubshell(1, 0, 1)
        self.assertAlmostEqual(0.001, self.db.atomic_subshell_nonradiative_width_eV(118, ashell), 4)

    def testatomic_subshell_occupancy(self):
        ashell = descriptor.AtomicSubshell(1, 0, 1)
        self.assertEqual(1, self.db.atomic_subshell_occupancy(118, ashell))

    def testtransition_notation(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.Transition(L3, K)
        self.assertEqual('a', self.db.transition_notation(transition, 'mock', 'ascii'))
        self.assertEqual('b', self.db.transition_notation(transition, 'mock', 'utf16'))
        self.assertEqual('c', self.db.transition_notation(transition, 'mock', 'html'))
        self.assertEqual('d', self.db.transition_notation(transition, 'mock', 'latex'))

    def testtransition_energy_eV(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.Transition(L3, K)
        self.assertAlmostEqual(0.2, self.db.transition_energy_eV(118, transition), 4)

    def testtransition_probability(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.Transition(L3, K)
        self.assertAlmostEqual(0.02, self.db.transition_probability(118, transition), 4)

    def testtransition_relative_weight(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.Transition(L3, K)
        self.assertAlmostEqual(0.002, self.db.transition_relative_weight(118, transition), 4)

    def testtransitionset_notation(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.Transition(L3, K)
        transition2 = descriptor.Transition(L2, K, L3)
        transitionset = descriptor.TransitionSet([transition, transition2])
        self.assertEqual('a', self.db.transitionset_notation(transitionset, 'mock', 'ascii'))
        self.assertEqual('b', self.db.transitionset_notation(transitionset, 'mock', 'utf16'))
        self.assertEqual('c', self.db.transitionset_notation(transitionset, 'mock', 'html'))
        self.assertEqual('d', self.db.transitionset_notation(transitionset, 'mock', 'latex'))

    def testtransitionset_energy_eV(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.Transition(L3, K)
        transition2 = descriptor.Transition(L2, K, L3)
        transitionset = descriptor.TransitionSet([transition, transition2])
        self.assertAlmostEqual(0.3, self.db.transitionset_energy_eV(118, transitionset), 4)

    def testtransitionset_relative_weight(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.Transition(L3, K)
        transition2 = descriptor.Transition(L2, K, L3)
        transitionset = descriptor.TransitionSet([transition, transition2])
        self.assertAlmostEqual(0.003, self.db.transitionset_relative_weight(118, transitionset), 4)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
