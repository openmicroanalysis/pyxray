"""
Base SQL database.
"""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
from pyxray.sql.model import Reference
from pyxray.sql.util import session_scope

# Local modules.
from pyxray.meta.data import _Database

# Globals and constants variables.

class _SqlEngineDatabase(_Database):

    def __init__(self, engine):
        self.engine = engine

    def _get(self, queried_columns, filters, exception, reference=None):
        queried_columns.append(Reference.bibtexkey)

        with session_scope(self.engine) as session:
            q = session.query(*queried_columns)
            q = q.join(Reference)
            for f in filters:
                q = q.filter(f)
            q = q.order_by(Reference.id)

            results = OrderedDict((k, v) for * v, k in q.all())
            if not results:
                raise exception

            if reference is not None:
                if reference in results:
                    return results[reference]
                else:
                    raise exception

            for reference in self.reference_priority:
                if reference in results:
                    return results[reference]

            return results.popitem(last=False)[1]
