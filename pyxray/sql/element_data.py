""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.meta.element_data import _ElementDatabase
from pyxray.sql.data import _SqlEngineDatabase
from pyxray.sql.model import \
    (ElementSymbolProperty, ElementNameProperty, ElementAtomicWeightProperty,
     ElementMassDensityProperty)

# Globals and constants variables.

class SqlEngineElementDatabase(_ElementDatabase, _SqlEngineDatabase):

    def __init__(self, engine):
        super().__init__(engine)

    def symbol(self, z, reference=None):
        queried_columns = [ElementSymbolProperty.symbol]
        filters = [ElementSymbolProperty.z == z]
        exception = ValueError('Unknown symbol for z={0} and '
                               'reference="{1}"'.format(z, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

    def atomic_number(self, symbol, reference=None):
        queried_columns = [ElementSymbolProperty.z]
        filters = [ElementSymbolProperty.symbol == symbol]
        exception = ValueError('Unknown atomic number for symbol="{0}" and '
                               'reference="{1}"'.format(symbol, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

    def name(self, zeq, language='en', reference=None):
        z = self._get_z(zeq)
        queried_columns = [ElementNameProperty.name]
        filters = [ElementNameProperty.z == z,
                   ElementNameProperty.language_code == language]
        exception = ValueError('Unknown name for z="{0}", '
                               'language="{1}" and '
                                'reference="{2}"'.format(z, language, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

    def atomic_weight(self, zeq, reference=None):
        z = self._get_z(zeq)
        queried_columns = [ElementAtomicWeightProperty.value]
        filters = [ElementAtomicWeightProperty.z == z]
        exception = ValueError('Unknown atomic weight for z="{0}" and '
                                'reference="{1}"'.format(z, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

    def mass_density_kg_per_m3(self, zeq, reference=None):
        z = self._get_z(zeq)
        queried_columns = [ElementMassDensityProperty.value]
        filters = [ElementMassDensityProperty.z == z]
        exception = ValueError('Unknown mass density for z="{0}" and '
                                'reference="{1}"'.format(z, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

if __name__ == '__main__':
    import os
    from sqlalchemy import create_engine

    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'pyxray.sql')
    engine = create_engine('sqlite:///' + os.path.abspath(filepath))

#    with session_scope(engine) as session:
#        ref = Reference(bibtexkey='test')
#        p = ElementSymbolProperty(z=92, symbol='U2', reference=ref)
#        session.add(p)
#        session.commit()

    db = SqlEngineElementDatabase(engine)
    db.reference_priority = ['test2']
    print(db.symbol(92, reference='unattributed'))
    print(db.symbol(92))
    print(db.atomic_number('al'))
    print(db.name('na', language='en', reference='wikipedia2016'))
    print(db.name('na', language='en'))
#    print(db.name('na', language='en', reference='unattributed'))
