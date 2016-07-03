""""""

# Standard library modules.

# Third party modules.
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, Unicode, String, ForeignKey, Float
from sqlalchemy.orm import relationship

# Local modules.

# Globals and constants variables.

Base = declarative_base()

class Reference(Base):

    __tablename__ = 'refs'

    id = Column(Integer, primary_key=True)
    bibtexkey = Column(String(256), nullable=False)
    author = Column(Unicode)
    year = Column(Unicode)
    title = Column(Unicode)
    type = Column(Unicode)
    booktitle = Column(Unicode)
    editor = Column(Unicode)
    pages = Column(Unicode)
    edition = Column(Unicode)
    journal = Column(Unicode)
    school = Column(Unicode)
    address = Column(Unicode)
    url = Column(Unicode)
    note = Column(Unicode)
    number = Column(Unicode)
    series = Column(Unicode)
    volume = Column(Unicode)
    publisher = Column(Unicode)
    organization = Column(Unicode)
    chapter = Column(Unicode)
    howpublished = Column(Unicode)

    def __repr__(self):
        return '<Reference(%s)>' % self.bibtexkey

class ReferenceMixin(object):

    @declared_attr
    def reference_id(cls): #@NoSelf
        return Column(Integer, ForeignKey('refs.id'), nullable=False)

    @declared_attr
    def reference(cls): #@NoSelf
        return relationship('Reference')

class ElementPropertyMixin(object):

    id = Column(Integer, primary_key=True)
    z = Column(Integer, nullable=False)

class ElementSymbolProperty(ElementPropertyMixin, ReferenceMixin, Base):

    __tablename__ = 'element_symbol'

    symbol = Column(String(3, collation='NOCASE'), nullable=False)

class ElementNameProperty(ElementPropertyMixin, ReferenceMixin, Base):

    __tablename__ = 'element_name'

    name = Column(Unicode(256, collation='NOCASE'), nullable=False)
    language_code = Column(String(2, collation='NOCASE'), nullable=False)

class ElementAtomicWeightProperty(ElementPropertyMixin, ReferenceMixin, Base):

    __tablename__ = 'element_atomic_weight'

    value = Column(Float, nullable=False)

class ElementMassDensityProperty(ElementPropertyMixin, ReferenceMixin, Base):

    __tablename__ = 'element_mass_density'

    value = Column(Float, nullable=False)
