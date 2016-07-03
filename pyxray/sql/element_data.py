""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.meta.element_data import _ElementDatabase
from pyxray.sql.data import _SqlEngineDatabaseMixin
from pyxray.sql.model import \
    (Element, ElementNameProperty, ElementAtomicWeightProperty,
     ElementMassDensityProperty)
from pyxray.sql.util import session_scope

# Globals and constants variables.

class SqlEngineElementDatabase(_SqlEngineDatabaseMixin, _ElementDatabase):

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def _get_element_id(self, z):
        with session_scope(self.engine) as session:
            return session.query(Element.id).filter(Element.z == z).one()[0]

    def symbol(self, z):
        queried_columns = [Element.symbol]
        filters = [Element.z == z]
        exception = ValueError('Unknown symbol for z={0}'.format(z))
        return self._get_noref(queried_columns, filters, exception)[0]

    def atomic_number(self, symbol):
        queried_columns = [Element.z]
        filters = [Element.symbol == symbol]
        exception = ValueError('Unknown atomic number for symbol="{0}"'.format(symbol))
        return self._get_noref(queried_columns, filters, exception)[0]

    def name(self, zeq, language='en', reference=None):
        z = self._get_z(zeq)
        element_id = self._get_element_id(z)
        queried_columns = [ElementNameProperty.name]
        filters = [ElementNameProperty.element_id == element_id,
                   ElementNameProperty.language_code == language]
        exception = ValueError('Unknown name for z="{0}", '
                               'language="{1}" and '
                                'reference="{2}"'
                                .format(z, language, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

    def atomic_weight(self, zeq, reference=None):
        z = self._get_z(zeq)
        element_id = self._get_element_id(z)
        queried_columns = [ElementAtomicWeightProperty.value]
        filters = [ElementAtomicWeightProperty.element_id == element_id]
        exception = ValueError('Unknown atomic weight for z="{0}" and '
                                'reference="{1}"'.format(z, reference))
        return self._get(queried_columns, filters, exception, reference)[0]

    def mass_density_kg_per_m3(self, zeq, reference=None):
        z = self._get_z(zeq)
        element_id = self._get_element_id(z)
        queried_columns = [ElementMassDensityProperty.value_kg_per_m3]
        filters = [ElementMassDensityProperty.element_id == element_id]
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
    print(db.symbol(92))
    print(db.atomic_number('al'))
#    print(db.name('o', language='en', reference='wikipedia2016'))
#    print(db.name('o', language='de'))
#    print(db.name('na', language='en', reference='unattributed'))
