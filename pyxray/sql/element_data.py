""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.meta.element_data import _ElementDatabase
from pyxray.sql.model import Reference, ElementSymbolProperty
from pyxray.sql.util import session_scope

# Globals and constants variables.

class SqlEngineElementDatabase(_ElementDatabase):

    def __init__(self, engine):
        self.engine = engine

    def _get_property(self, zeq, reference, clasz, attr, name):
        z = self._get_z(zeq)

        with session_scope(self.engine) as session:
            q = session.query(getattr(clasz, attr))\
                       .filter(getattr(clasz, 'z') == z)\
                       .join(Reference)\
                       .filter(Reference.bibtexkey == reference)

            result = q.first()
            if not result:
                raise ValueError('Unknown {0} for z={1} and reference "{2}"'
                                 .format(name, z, reference))

            return result[0]

    def symbol(self, z, reference='unattributed'):
        return self._get_property(z, reference,
                                  ElementSymbolProperty, 'symbol', 'symbol')

    def atomic_number(self, symbol, reference='unattributed'):
        with session_scope(self.engine) as session:
            q = session.query(ElementSymbolProperty.z)\
                       .filter(ElementSymbolProperty.symbol == symbol)\
                       .join(Reference)\
                       .filter(Reference.bibtexkey == reference)

            result = q.first()
            if not result:
                raise ValueError('Unknown atomic number for symbol "{0}" and'
                                 ' reference "{1}"'.format(symbol, reference))

            return result[0]

    def name(self, zeq, language='en', reference='unattributed'):
        raise NotImplementedError

    def atomic_weight(self, zeq, ref='unattributed'):
        raise NotImplementedError

    def mass_density_kg_per_m3(self, zeq, ref='unattributed'):
        raise NotImplementedError

if __name__ == '__main__':
    import os
    from sqlalchemy import create_engine

    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'pyxray.sql')
    engine = create_engine('sqlite:///' + os.path.abspath(filepath))
    db = SqlEngineElementDatabase(engine)
    print(db.symbol(92, reference='unattributed'))
    print(db.symbol(95))
    print(db.atomic_number('Al'))
