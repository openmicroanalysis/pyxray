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
import pyxray.descriptor as descriptor
from pyxray.sql.data import SqlDatabase, NotFound
from pyxray.sql.test_build import MockSqliteDatabaseBuilder

# Globals and constants variables.

class TestSqlDatabase(unittest.TestCase):

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
        super().setUp()

        self.connection = sqlite3.connect(self.filepath)
        self.db = SqlDatabase(self.connection)

    def tearDown(self):
        super().tearDown()
        self.connection.close()

    def testelement(self):
        self.assertEqual(descriptor.Element(118), self.db.element('Vi'))
        self.assertEqual(descriptor.Element(118), self.db.element(118))
        self.assertEqual(descriptor.Element(118), self.db.element('Vibranium'))
        self.assertRaises(NotFound, self.db.element, 'Al')
        self.assertRaises(NotFound, self.db.element, 13)
        self.assertRaises(NotFound, self.db.element, 'Aluminium')

    def testelement_atomic_number(self):
        self.assertEqual(118, self.db.element_atomic_number('Vi'))
        self.assertEqual(118, self.db.element_atomic_number(118))
        self.assertEqual(118, self.db.element_atomic_number('Vibranium'))
        self.assertRaises(NotFound, self.db.element_atomic_number, 'Al')
        self.assertRaises(NotFound, self.db.element_atomic_number, 13)
        self.assertRaises(NotFound, self.db.element_atomic_number, 'Aluminium')

    def testelement_symbol(self):
        self.assertEqual('Vi', self.db.element_symbol('Vi'))
        self.assertEqual('Vi', self.db.element_symbol(118))
        self.assertEqual('Vi', self.db.element_symbol('Vibranium'))
        self.assertRaises(NotFound, self.db.element_symbol, 'Al')
        self.assertRaises(NotFound, self.db.element_symbol, 13)
        self.assertRaises(NotFound, self.db.element_symbol, 'Aluminium')

    def testelement_name(self):
        self.assertEqual('Vibranium', self.db.element_name('Vi', 'en'))
        self.assertEqual('Vibranium', self.db.element_name(118, 'en'))
        self.assertEqual('Vibranium', self.db.element_name('Vibranium', 'en'))
        self.assertEqual('Vibranium', self.db.element_name(118, 'en', 'lee1966'))
        self.assertRaises(NotFound, self.db.element_name, 'Al', 'en')
        self.assertRaises(NotFound, self.db.element_name, 13, 'en')
        self.assertRaises(NotFound, self.db.element_name, 'Aluminium', 'en')
        self.assertRaises(NotFound, self.db.element_name, 118, 'en', 'doe2016')

    def testelement_atomic_weight(self):
        self.assertAlmostEqual(999.1, self.db.element_atomic_weight(118), 2)
        self.assertAlmostEqual(999.1, self.db.element_atomic_weight(118, 'lee1966'), 2)
        self.assertAlmostEqual(111.1, self.db.element_atomic_weight(118, 'doe2016'), 2)

        self.db.set_default_reference('element_atomic_weight', 'doe2016')
        self.assertAlmostEqual(111.1, self.db.element_atomic_weight(118), 2)

    def testelement_mass_density_kg_per_m3(self):
        self.assertAlmostEqual(999.2, self.db.element_mass_density_kg_per_m3('Vi'), 2)
        self.assertAlmostEqual(999.2, self.db.element_mass_density_kg_per_m3(118), 2)
        self.assertAlmostEqual(999.2, self.db.element_mass_density_kg_per_m3('Vibranium'), 2)

    def testelement_mass_density_g_per_cm3(self):
        self.assertAlmostEqual(0.9992, self.db.element_mass_density_g_per_cm3('Vi'), 4)
        self.assertAlmostEqual(0.9992, self.db.element_mass_density_g_per_cm3(118), 4)
        self.assertAlmostEqual(0.9992, self.db.element_mass_density_g_per_cm3('Vibranium'), 4)

    def testelement_xray_transitions(self):
        transitions = self.db.element_xray_transitions(118)
        self.assertEqual(1, len(transitions))

        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        expected = descriptor.XrayTransition(L3, K)
        self.assertEqual(expected, transitions[0])

    def testelement_xray_transitions2(self):
        transitions = self.db.element_xray_transitions(118, 'a')
        self.assertEqual(1, len(transitions))

        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        expected = descriptor.XrayTransition(L3, K)
        self.assertEqual(expected, transitions[0])

    def testelement_xray_transition(self):
        transition = self.db.element_xray_transition(118, 'a')

        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        expected = descriptor.XrayTransition(L3, K)
        self.assertEqual(expected, transition)

        self.assertRaises(NotFound, self.db.element_xray_transition, 1, 'a')
        self.assertRaises(NotFound, self.db.element_xray_transition, 118, 'g')

    def testatomic_shell(self):
        expected = descriptor.AtomicShell(1)
        self.assertEqual(expected, self.db.atomic_shell('a'))
        self.assertEqual(expected, self.db.atomic_shell('b'))
        self.assertEqual(expected, self.db.atomic_shell(1))
        self.assertRaises(NotFound, self.db.atomic_shell, 'c')
        self.assertRaises(NotFound, self.db.atomic_shell, 3)

    def testatomic_shell_notation(self):
        self.assertEqual('a', self.db.atomic_shell_notation(1, 'mock', 'ascii'))
        self.assertEqual('b', self.db.atomic_shell_notation(1, 'mock', 'utf16'))
        self.assertEqual('c', self.db.atomic_shell_notation(1, 'mock', 'html'))
        self.assertEqual('d', self.db.atomic_shell_notation(1, 'mock', 'latex'))
        self.assertEqual('c', self.db.atomic_shell_notation('a', 'mock', 'html'))
        self.assertEqual('c', self.db.atomic_shell_notation('b', 'mock', 'html'))

    def testatomic_subshell(self):
        expected = descriptor.AtomicSubshell(1, 0, 1)
        self.assertEqual(expected, self.db.atomic_subshell('a'))
        self.assertEqual(expected, self.db.atomic_subshell('b'))
        self.assertEqual(expected, self.db.atomic_subshell((1, 0, 1)))
        self.assertEqual(expected, self.db.atomic_subshell(descriptor.AtomicSubshell(1, 0, 1)))
        self.assertRaises(NotFound, self.db.atomic_subshell, 'c')
        self.assertRaises(NotFound, self.db.atomic_subshell, (3, 3, 3))

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

    def testxray_transition(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        expected = descriptor.XrayTransition(L3, K)
        self.assertEqual(expected, self.db.xray_transition('a'))
        self.assertEqual(expected, self.db.xray_transition((L3, K)))
        self.assertEqual(expected, self.db.xray_transition(descriptor.XrayTransition(L3, K)))

    def testxray_transition_notation(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.XrayTransition(L3, K)
        self.assertEqual('a', self.db.xray_transition_notation(transition, 'mock', 'ascii'))
        self.assertEqual('b', self.db.xray_transition_notation(transition, 'mock', 'utf16'))
        self.assertEqual('c', self.db.xray_transition_notation(transition, 'mock', 'html'))
        self.assertEqual('d', self.db.xray_transition_notation(transition, 'mock', 'latex'))

    def testxray_transition_energy_eV(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.XrayTransition(L3, K)
        self.assertAlmostEqual(0.2, self.db.xray_transition_energy_eV(118, transition), 4)

    def testxray_transition_probability(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.XrayTransition(L3, K)
        self.assertAlmostEqual(0.02, self.db.xray_transition_probability(118, transition), 4)

    def testxray_transition_relative_weight(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        transition = descriptor.XrayTransition(L3, K)
        self.assertAlmostEqual(0.002, self.db.xray_transition_relative_weight(118, transition), 4)

    def testxray_transitionset(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        L1 = descriptor.AtomicSubshell(2, 0, 1)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        expected = descriptor.XrayTransitionSet([transition, transition2])
        self.assertEqual(expected, self.db.xray_transitionset('a'))
        self.assertEqual(expected, self.db.xray_transitionset('b'))

        transitionset = descriptor.XrayTransitionSet([transition, transition2])
        self.assertEqual(expected, self.db.xray_transitionset(transitionset))

        transitionset = descriptor.XrayTransitionSet([transition])
        self.assertRaises(NotFound, self.db.xray_transitionset, transitionset)

        transition3 = descriptor.XrayTransition(L1, K)
        transitionset = descriptor.XrayTransitionSet([transition, transition3])
        self.assertRaises(NotFound, self.db.xray_transitionset, transitionset)

    def testxray_transitionset_notation(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        transitionset = descriptor.XrayTransitionSet([transition, transition2])
        self.assertEqual('a', self.db.xray_transitionset_notation(transitionset, 'mock', 'ascii'))
        self.assertEqual('b', self.db.xray_transitionset_notation(transitionset, 'mock', 'utf16'))
        self.assertEqual('c', self.db.xray_transitionset_notation(transitionset, 'mock', 'html'))
        self.assertEqual('d', self.db.xray_transitionset_notation(transitionset, 'mock', 'latex'))

    def testxray_transitionset_energy_eV(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        transitionset = descriptor.XrayTransitionSet([transition, transition2])
        self.assertAlmostEqual(0.3, self.db.xray_transitionset_energy_eV(118, transitionset), 4)

    def testxray_transitionset_relative_weight(self):
        K = descriptor.AtomicSubshell(1, 0, 1)
        L3 = descriptor.AtomicSubshell(2, 1, 3)
        L2 = descriptor.AtomicSubshell(2, 1, 1)
        transition = descriptor.XrayTransition(L3, K)
        transition2 = descriptor.XrayTransition(L2, K)
        transitionset = descriptor.XrayTransitionSet([transition, transition2])
        self.assertAlmostEqual(0.003, self.db.xray_transitionset_relative_weight(118, transitionset), 4)

    def testxray_line(self):
        xrayline = self.db.xray_line(118, 'aa')

        self.assertEqual(xrayline.element.atomic_number, 118)
        self.assertEqual(1, len(xrayline.transitions))
        self.assertEqual('Vi bb', xrayline.iupac)
        self.assertEqual('Vi bb', xrayline.siegbahn)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
