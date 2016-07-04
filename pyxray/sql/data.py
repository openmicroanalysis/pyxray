""""""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.exc import NoResultFound

# Local modules.
from pyxray.meta.data import _Database
from pyxray.sql.model import \
    (Reference,
     Element, ElementNameProperty, ElementAtomicWeightProperty,
     ElementMassDensityProperty)
from pyxray.sql.util import session_scope, one_or_list

# Globals and constants variables.

class SqlEngineDatabase(_Database):

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    def _query_one(self, q, exception):
        with session_scope(self.engine) as session:
            q = q.with_session(session)
            try:
                return one_or_list(q.one())
            except NoResultFound:
                raise exception

    def _query_with_references(self, q, exception, reference=None):
        q = q.add_columns(Reference.bibtexkey)
        q = q.join(Reference)
        q = q.order_by(Reference.id)

        with session_scope(self.engine) as session:
            q = q.with_session(session)

            results = OrderedDict((k, v) for * v, k in q.all())

            # No results from query
            if not results:
                raise exception

            # Check result from specified reference
            if reference is not None:
                if reference in results:
                    return one_or_list(results[reference]), reference
                else:
                    raise exception

            # Check result from preferred references
            for reference in self.reference_priority:
                if reference in results:
                    return one_or_list(results[reference]), reference

            # Return first result
            reference, value = results.popitem(last=False)
            return one_or_list(value), reference

    def element_symbol(self, z):
        q = Query(Element.symbol)
        q = q.filter(Element.z == z)
        exception = ValueError('Unknown symbol for z={0}'.format(z))
        return self._query_one(q, exception)

    def element_atomic_number(self, symbol):
        q = Query(Element.z)
        q = q.filter(Element.symbol == symbol)
        exception = \
            ValueError('Unknown atomic number for symbol="{0}"'.format(symbol))
        return self._query_one(q, exception)

    def element_name(self, zeq, language='en', reference=None):
        z = self._get_z(zeq)
        q = Query(ElementNameProperty.name)
        q = q.filter(ElementNameProperty.language_code == language)
        q = q.join(Element)
        q = q.filter(Element.z == z)
        exception = ValueError('Unknown name for z="{0}", '
                               'language="{1}" and '
                                'reference="{2}"'
                                .format(z, language, reference))
        return self._query_with_references(q, exception, reference)

    def element_atomic_weight(self, zeq, reference=None):
        z = self._get_z(zeq)
        q = Query(ElementAtomicWeightProperty.value)
        q = q.join(Element)
        q = q.filter(Element.z == z)
        exception = ValueError('Unknown atomic weight for z="{0}" and '
                                'reference="{1}"'.format(z, reference))
        return self._query_with_references(q, exception, reference)

    def element_mass_density_kg_per_m3(self, zeq, reference=None):
        z = self._get_z(zeq)
        q = Query(ElementMassDensityProperty.value_kg_per_m3)
        q = q.join(Element)
        q = q.filter(Element.z == z)
        exception = ValueError('Unknown mass density for z="{0}" and '
                                'reference="{1}"'.format(z, reference))
        return self._query_with_references(q, exception, reference)

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

    db = SqlEngineDatabase(engine)
    print(db.element_symbol(92))
    print(db.element_atomic_number('al'))
#    print(db.name('o', language='en', reference='wikipedia2016'))
#    print(db.name('o', language='de'))
#    print(db.name('na', language='en', reference='unattributed'))
