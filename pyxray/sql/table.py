"""
SQL table definitions.
"""

# Standard library modules.

# Third party modules.
from sqlalchemy import \
    Table, Column, Integer, Unicode, String, ForeignKey, Float, MetaData

# Local modules.

# Globals and constants variables.

metadata = MetaData()

def _append_primary_key_columns(table):
    table.append_column(Column('id', Integer, primary_key=True))

def _append_element_columns(table):
    table.append_column(Column('element_id', Integer,
                               ForeignKey('element.id'), nullable=False))

def _append_atomic_shell_columns(table):
    table.append_column(Column('atomic_shell_id', Integer,
                               ForeignKey('atomic_shell.id'), nullable=False))

def _append_atomic_subshell_columns(table):
    table.append_column(Column('atomic_subshell_id', Integer,
                               ForeignKey('atomic_subshell.id'), nullable=False))

def _append_transition_columns(table):
    table.append_column(Column('transition_id', Integer,
                               ForeignKey('transition.id'), nullable=False))

def _append_transitionset_columns(table):
    table.append_column(Column('transitionset_id', Integer,
                               ForeignKey('transitionset.id'), nullable=False))

def _append_language_columns(table):
    table.append_column(Column('language_id', Integer,
                               ForeignKey('language.id'), nullable=False))

def _append_notation_columns(table):
    table.append_column(Column('notation_id', Integer,
                               ForeignKey('notation.id'), nullable=False))

def _append_notation_property_columns(table):
    table.append_column(Column('ascii', String, nullable=False))
    table.append_column(Column('utf16', Unicode))
    table.append_column(Column('html', String))
    table.append_column(Column('latex', String))

def _append_reference_columns(table):
    table.append_column(Column('reference_id', Integer,
                               ForeignKey('ref.id'), nullable=False))

def _append_energy_property_columns(table):
    table.append_column(Column('value_eV', Float, nullable=False))

#--- Descriptors

element = \
    Table("element", metadata,
          Column('atomic_number', Integer))
_append_primary_key_columns(element)

atomic_shell = \
    Table('atomic_shell', metadata,
          Column('principal_quantum_number', Integer, nullable=False))
_append_primary_key_columns(atomic_shell)

atomic_subshell = \
    Table('atomic_subshell', metadata,
          Column('azimuthal_quantum_number', Integer, nullable=False),
          Column('total_angular_momentum_nominator', Integer, nullable=False))
_append_primary_key_columns(atomic_subshell)
_append_atomic_shell_columns(atomic_subshell)

transition = \
    Table('transition', metadata,
          Column('source_subshell_id', Integer, ForeignKey('atomic_shell.id'), nullable=False),
          Column('destination_subshell_id', Integer, ForeignKey('atomic_shell.id'), nullable=False),
          Column('secondary_destination_subshell_id', Integer, ForeignKey('atomic_shell.id')))
_append_primary_key_columns(transition)

transitionset_association = \
    Table('transitionset_association', metadata,
          Column('transitionset_id', Integer, ForeignKey('transitionset.id'), nullable=False),
          Column('transition_id', Integer, ForeignKey('transition.id'), nullable=False))
_append_primary_key_columns(transitionset_association)

transitionset = \
    Table('transitionset', metadata)
_append_primary_key_columns(transitionset)

language = \
    Table('language', metadata,
          Column('code', String(3, collation='NOCASE'), nullable=False))
_append_primary_key_columns(language)

notation = \
    Table('notation', metadata,
          Column('name', String(3, collation='NOCASE'), nullable=False))
_append_primary_key_columns(notation)

reference = \
    Table('ref', metadata,
          Column('bibtexkey', String(256), nullable=False),
          Column('author', Unicode),
          Column('year', Unicode),
          Column('title', Unicode),
          Column('type', Unicode),
          Column('booktitle', Unicode),
          Column('editor', Unicode),
          Column('pages', Unicode),
          Column('edition', Unicode),
          Column('journal', Unicode),
          Column('school', Unicode),
          Column('address', Unicode),
          Column('url', Unicode),
          Column('note', Unicode),
          Column('number', Unicode),
          Column('series', Unicode),
          Column('volume', Unicode),
          Column('publisher', Unicode),
          Column('organization', Unicode),
          Column('chapter', Unicode),
          Column('howpublished', Unicode),
          Column('doi', Unicode))
_append_primary_key_columns(reference)

#--- Properties

element_symbol = \
    Table('element_symbol', metadata,
          Column('symbol', String(3, collation='NOCASE'), nullable=False))
_append_primary_key_columns(element_symbol)
_append_reference_columns(element_symbol)
_append_element_columns(element_symbol)

element_name = \
    Table('element_name', metadata,
          Column('name', Unicode(256, collation='NOCASE'), nullable=False))
_append_primary_key_columns(element_name)
_append_reference_columns(element_name)
_append_element_columns(element_name)
_append_language_columns(element_name)

element_atomic_weight = \
    Table('element_atomic_weight', metadata,
          Column('value', Float, nullable=False))
_append_primary_key_columns(element_atomic_weight)
_append_reference_columns(element_atomic_weight)
_append_element_columns(element_atomic_weight)

element_mass_density = \
    Table('element_mass_density', metadata,
          Column('value_kg_per_m3', Float, nullable=False))
_append_primary_key_columns(element_mass_density)
_append_reference_columns(element_mass_density)
_append_element_columns(element_mass_density)

atomic_shell_notation = \
    Table('atomic_shell_notation', metadata)
_append_primary_key_columns(atomic_shell_notation)
_append_reference_columns(atomic_shell_notation)
_append_atomic_shell_columns(atomic_shell_notation)
_append_notation_columns(atomic_shell_notation)
_append_notation_property_columns(atomic_shell_notation)

atomic_subshell_notation = \
    Table('atomic_subshell_notation', metadata)
_append_primary_key_columns(atomic_subshell_notation)
_append_reference_columns(atomic_subshell_notation)
_append_atomic_subshell_columns(atomic_subshell_notation)
_append_notation_columns(atomic_subshell_notation)
_append_notation_property_columns(atomic_subshell_notation)

atomic_subshell_binding_energy = \
    Table('atomic_subshell_binding_energy', metadata)
_append_primary_key_columns(atomic_subshell_binding_energy)
_append_reference_columns(atomic_subshell_binding_energy)
_append_element_columns(atomic_subshell_binding_energy)
_append_atomic_subshell_columns(atomic_subshell_binding_energy)
_append_energy_property_columns(atomic_subshell_binding_energy)

atomic_subshell_radiative_width = \
    Table('atomic_subshell_radiative_width', metadata)
_append_primary_key_columns(atomic_subshell_radiative_width)
_append_reference_columns(atomic_subshell_radiative_width)
_append_element_columns(atomic_subshell_radiative_width)
_append_atomic_subshell_columns(atomic_subshell_radiative_width)
_append_energy_property_columns(atomic_subshell_radiative_width)

atomic_subshell_nonradiative_width = \
    Table('atomic_subshell_nonradiative_width', metadata)
_append_primary_key_columns(atomic_subshell_nonradiative_width)
_append_reference_columns(atomic_subshell_nonradiative_width)
_append_element_columns(atomic_subshell_nonradiative_width)
_append_atomic_subshell_columns(atomic_subshell_nonradiative_width)
_append_energy_property_columns(atomic_subshell_nonradiative_width)

atomic_subshell_occupancy = \
    Table('atomic_subshell_occupancy', metadata,
          Column('value', Integer, nullable=False))
_append_primary_key_columns(atomic_subshell_occupancy)
_append_reference_columns(atomic_subshell_occupancy)
_append_element_columns(atomic_subshell_occupancy)
_append_atomic_subshell_columns(atomic_subshell_occupancy)

transition_notation = \
    Table('transition_notation', metadata)
_append_primary_key_columns(transition_notation)
_append_reference_columns(transition_notation)
_append_transition_columns(transition_notation)
_append_notation_columns(transition_notation)
_append_notation_property_columns(transition_notation)

transition_energy = \
    Table('transition_energy', metadata)
_append_primary_key_columns(transition_energy)
_append_reference_columns(transition_energy)
_append_element_columns(transition_energy)
_append_transition_columns(transition_energy)
_append_energy_property_columns(transition_energy)

transition_probability = \
    Table('transition_probability', metadata,
          Column('value', Float, nullable=False))
_append_primary_key_columns(transition_probability)
_append_reference_columns(transition_probability)
_append_element_columns(transition_probability)
_append_transition_columns(transition_probability)

transition_relative_weight = \
    Table('transition_relative_weight', metadata,
          Column('value', Float, nullable=False))
_append_primary_key_columns(transition_relative_weight)
_append_reference_columns(transition_relative_weight)
_append_element_columns(transition_relative_weight)
_append_transition_columns(transition_relative_weight)

transitionset_notation = \
    Table('transitionset_notation', metadata)
_append_primary_key_columns(transitionset_notation)
_append_reference_columns(transitionset_notation)
_append_transitionset_columns(transitionset_notation)
_append_notation_columns(transitionset_notation)
_append_notation_property_columns(transitionset_notation)

transitionset_energy = \
    Table('transitionset_energy', metadata)
_append_primary_key_columns(transitionset_energy)
_append_reference_columns(transitionset_energy)
_append_element_columns(transitionset_energy)
_append_transitionset_columns(transitionset_energy)
_append_energy_property_columns(transitionset_energy)

transitionset_relative_weight = \
    Table('transitionset_relative_weight', metadata,
          Column('value', Float, nullable=False))
_append_primary_key_columns(transitionset_relative_weight)
_append_reference_columns(transitionset_relative_weight)
_append_element_columns(transitionset_relative_weight)
_append_transitionset_columns(transitionset_relative_weight)