""""""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)

# Third party modules.
from sqlalchemy.orm.exc import NoResultFound

# Local modules.
from pyxray.sql.util import session_scope
from pyxray.sql.model import Reference

# Globals and constants variables.

class SqlMapper(object):
    """
    Maps a SQL model to a parser in order to populate a SQL database.
    """

    def __init__(self, model, parser, mappings, dependencies=None):
        """
        :arg model: SQL model
        :type model: 
        
        :arg parser: parser
        :type parser: :class:`_Parser <pyxray.meta.parser._Parser`
        
        :arg mappings: :class:`dict` mapping each column of a SQL model to a 
            parsed entry. The keys of the :class:`dict` are the model columns,
            and the values a callable function taking two arguments: (1) the
            SQL session and (2) a parsed entry.
        :type mappings: :class:`dict`
        
        :arg dependencies: :class:`set` of :class:`.SqlMapper` on which this
            mapper depends on. If ``None``, there is no dependency (default).
        :type dependencies: :class:`set`
        """
        self._model = model
        self._parser = parser

        for column, funckey in mappings.items():
            if not hasattr(model, column.key):
                raise ValueError('Model has no "{0}" column'
                                 .format(column.key))
            if not callable(funckey):
                raise ValueError('Value should be callable')
        self._mappings = mappings.copy()

        if dependencies is None:
            dependencies = []
        self._dependencies = frozenset(dependencies)

    def _create_table(self, engine, model):
        table = model.__table__
        if table.exists(engine):
            return
        table.create(engine)

    def _add_reference(self, session, reference):
        query = session.query(Reference)
        query = query.filter(Reference.bibtexkey == reference.bibtexkey)

        try:
            return query.one()
        except NoResultFound:
            ref = Reference(**reference.todict())
            session.add(ref)
            session.commit()
            return ref

    def _add_entry(self, session, entry, reference):
        kwargs = {}
        query = session.query(self.model)

        for column, funckey in self.mappings.items():
            value = funckey(session, entry)
            kwargs[column.key] = value
            query = query.filter(column == value)

        if hasattr(self.model, 'reference') and 'reference' not in kwargs:
            kwargs['reference'] = reference
            query = query.filter(self.model.reference == reference)

        obj = self.model(**kwargs)

        if query.count() == 0:
            session.add(obj)
            logger.debug('Added entry: ' +
                         ', '.join('{0}={1}'.format(k, v)
                                   for k, v in sorted(kwargs.items())))

    def _populate_dependencies(self, engine):
        for dependency in self.dependencies:
            dependency.populate(engine)

    def populate(self, engine):
        self._populate_dependencies(engine)

        entries = self.parser.parse()

        self._create_table(engine, self.model)
        self._create_table(engine, Reference)

        with session_scope(engine) as session:
            reference = self._add_reference(session, self.parser.reference)
            for entry in entries:
                self._add_entry(session, entry, reference)

    @property
    def model(self):
        return self._model

    @property
    def parser(self):
        return self._parser

    @property
    def mappings(self):
        return self._mappings.copy()

    @property
    def dependencies(self):
        return self._dependencies


