#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.
from sqlalchemy import create_engine

# Local modules.
from pyxray.sql.data import SqlEngineDatabase
from pyxray.sql.model import \
    (Base, Reference, Element, ElementNameProperty,
     ElementAtomicWeightProperty, ElementMassDensityProperty)
from pyxray.sql.util import session_scope

# Globals and constants variables.

def create_mock_database():
    engine = create_engine('sqlite:///:memory:')

    Base.metadata.create_all(engine) #@UndefinedVariable

    elements = {}
    data = [(26, 'Fe'), (8, 'O')]
    with session_scope(engine) as session:
        for z, symbol in data:
            e = Element(z=z, symbol=symbol)
            elements[z] = e
            session.add(e)
        session.commit()

    ref1 = Reference(bibtexkey='ref1')
    ref2 = Reference(bibtexkey='ref2')
    data = [(26, 'Iron', 'Eisen', 55.845, 7874.0, ref1),
            (26, 'Iron', 'Eisen', 58.0, 9000.0, ref2),
            (8, 'Oxygen', 'Sauerstoff', 15.9994, 1.429, ref1)]

    with session_scope(engine) as session:
        for z, name_en, name_de, aw, rho, ref in data:
            e = elements[z]

            p = ElementNameProperty(element=e, language_code='en',
                                    name=name_en, reference=ref)
            session.add(p)

            p = ElementNameProperty(element=e, language_code='de',
                                    name=name_de, reference=ref)
            session.add(p)

            p = ElementAtomicWeightProperty(element=e, value=aw, reference=ref)
            session.add(p)

            p = ElementMassDensityProperty(element=e, value_kg_per_m3=rho,
                                           reference=ref)
            session.add(p)

        session.commit()

    return engine

class TestSqlEngineDatabase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        engine = create_mock_database()
        self.db = SqlEngineDatabase(engine)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testelement_symbol(self):
        self.assertEqual('Fe', self.db.element_symbol(26))

        self.assertEqual('O', self.db.element_symbol(8))

        self.assertRaises(ValueError, self.db.element_symbol, 1)

    def testelement_atomic_number(self):
        self.assertEqual(26, self.db.element_atomic_number('Fe'))
        self.assertEqual(26, self.db.element_atomic_number('fe'))

        self.assertEqual(8, self.db.element_atomic_number('O'))
        self.assertEqual(8, self.db.element_atomic_number('o'))

        self.assertRaises(ValueError, self.db.element_atomic_number, 'H')

    def testelement_name(self):
        self.assertTupleEqual(('Iron', 'ref1'), self.db.element_name(26))
        self.assertTupleEqual(('Iron', 'ref1'), self.db.element_name(26, 'en'))
        self.assertTupleEqual(('Eisen', 'ref1'), self.db.element_name(26, 'de'))
        self.assertTupleEqual(('Iron', 'ref1'), self.db.element_name('Fe'))

        self.assertTupleEqual(('Oxygen', 'ref1'), self.db.element_name(8))
        self.assertTupleEqual(('Oxygen', 'ref1'), self.db.element_name(8, 'en'))
        self.assertTupleEqual(('Sauerstoff', 'ref1'), self.db.element_name(8, 'de'))
        self.assertTupleEqual(('Oxygen', 'ref1'), self.db.element_name('O'))

        self.assertRaises(ValueError, self.db.element_name, 'H')
        self.assertRaises(ValueError, self.db.element_name, 26, 'fr')

    def testelement_atomic_weight(self):
        self.assertAlmostEqual(55.845, self.db.element_atomic_weight(26)[0], 3)
        self.assertEqual('ref1', self.db.element_atomic_weight(26)[1])
        self.assertAlmostEqual(55.845, self.db.element_atomic_weight('Fe')[0], 3)
        self.assertEqual('ref1', self.db.element_atomic_weight('Fe')[1])
        self.assertAlmostEqual(55.845, self.db.element_atomic_weight(26, reference='ref1')[0], 3)
        self.assertAlmostEqual(58.0, self.db.element_atomic_weight(26, reference='ref2')[0], 3)
        self.assertEqual('ref2', self.db.element_atomic_weight(26, reference='ref2')[1])

        self.assertAlmostEqual(15.9994, self.db.element_atomic_weight(8)[0], 3)
        self.assertEqual('ref1', self.db.element_atomic_weight(8)[1])
        self.assertAlmostEqual(15.9994, self.db.element_atomic_weight('O')[0], 3)
        self.assertEqual('ref1', self.db.element_atomic_weight('O')[1])
        self.assertAlmostEqual(15.9994, self.db.element_atomic_weight(8, reference='ref1')[0], 3)

        self.db.reference_priority = ['ref2']
        self.assertAlmostEqual(58.0, self.db.element_atomic_weight(26)[0], 3)
        self.assertEqual('ref2', self.db.element_atomic_weight(26)[1])
        self.assertAlmostEqual(55.845, self.db.element_atomic_weight(26, reference='ref1')[0], 3)
        self.assertEqual('ref1', self.db.element_atomic_weight(26, reference='ref1')[1])
        self.assertAlmostEqual(58.0, self.db.element_atomic_weight(26, reference='ref2')[0], 3)
        self.assertEqual('ref2', self.db.element_atomic_weight(26, reference='ref2')[1])
        self.assertAlmostEqual(15.9994, self.db.element_atomic_weight(8)[0], 3)
        self.assertEqual('ref1', self.db.element_atomic_weight(8)[1])

    def testelement_mass_density_kg_per_m3(self):
        self.assertAlmostEqual(7874.0, self.db.element_mass_density_kg_per_m3(26)[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3(26)[1], 3)
        self.assertAlmostEqual(7874.0, self.db.element_mass_density_kg_per_m3('Fe')[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3('Fe')[1], 3)
        self.assertAlmostEqual(7874.0, self.db.element_mass_density_kg_per_m3(26, reference='ref1')[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3(26, reference='ref1')[1], 3)
        self.assertAlmostEqual(9000.0, self.db.element_mass_density_kg_per_m3(26, reference='ref2')[0], 3)
        self.assertEqual('ref2', self.db.element_mass_density_kg_per_m3(26, reference='ref2')[1], 3)

        self.assertAlmostEqual(1.429, self.db.element_mass_density_kg_per_m3(8)[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3(8)[1], 3)
        self.assertAlmostEqual(1.429, self.db.element_mass_density_kg_per_m3('O')[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3('O')[1], 3)
        self.assertAlmostEqual(1.429, self.db.element_mass_density_kg_per_m3(8, reference='ref1')[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3(8, reference='ref1')[1], 3)

        self.db.reference_priority = ['ref2']
        self.assertAlmostEqual(9000.0, self.db.element_mass_density_kg_per_m3(26)[0], 3)
        self.assertEqual('ref2', self.db.element_mass_density_kg_per_m3(26)[1], 3)
        self.assertAlmostEqual(7874.0, self.db.element_mass_density_kg_per_m3(26, reference='ref1')[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3(26, reference='ref1')[1], 3)
        self.assertAlmostEqual(9000.0, self.db.element_mass_density_kg_per_m3(26, reference='ref2')[0], 3)
        self.assertEqual('ref2', self.db.element_mass_density_kg_per_m3(26, reference='ref2')[1], 3)
        self.assertAlmostEqual(1.429, self.db.element_mass_density_kg_per_m3(8)[0], 3)
        self.assertEqual('ref1', self.db.element_mass_density_kg_per_m3(8)[1], 3)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
