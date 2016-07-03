"""
Base SQL database.
"""

# Standard library modules.
from collections import OrderedDict

# Third party modules.
from sqlalchemy.orm.exc import NoResultFound

# Local modules.
from pyxray.sql.model import Reference
from pyxray.sql.util import session_scope

# Globals and constants variables.

class _SqlEngineDatabaseMixin(object):

    def _get_noref(self, queried_columns, filters, exception):
        with session_scope(self.engine) as session:
            q = session.query(*queried_columns)
            for f in filters:
                q = q.filter(f)

            try:
                return q.one()
            except NoResultFound:
                raise exception

    def _get(self, queried_columns, filters, exception, reference=None):
        """
        Returns values from the database based on the specified columns, 
        filters and reference.
        If no result is found, the exception is raised.
        This method respects the reference priority defined in the database
        if no reference is specified.
        
        :return: :class:`list` of length equal to the number of *queried_columns*
        """
        queried_columns.append(Reference.bibtexkey)

        with session_scope(self.engine) as session:
            q = session.query(*queried_columns)
            q = q.join(Reference)
            for f in filters:
                q = q.filter(f)
            q = q.order_by(Reference.id)

            results = OrderedDict((k, v) for * v, k in q.all())

            # No results from query
            if not results:
                raise exception

            # Check result from specified reference
            if reference is not None:
                if reference in results:
                    return results[reference]
                else:
                    raise exception

            # Check result from preferred references
            for reference in self.reference_priority:
                if reference in results:
                    return results[reference]

            # Return first result
            return results.popitem(last=False)[1]
