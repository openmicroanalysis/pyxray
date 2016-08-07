""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.sql.mapping.mapper import SqlMapper
from pyxray.sql.mapping.base import mapper_element
from pyxray.sql.mapping.util import get_key, get_element
from pyxray.sql.model import \
    ElementAtomicWeightProperty, ElementMassDensityProperty
from pyxray.parser.sargent_welch import \
    SargentWelchElementAtomicWeightParser, SargentWelchElementMassDensityParser

# Globals and constants variables.

model = ElementAtomicWeightProperty
parser = SargentWelchElementAtomicWeightParser()
bindings = {ElementAtomicWeightProperty.element: get_element(parser.KEY_Z),
            ElementAtomicWeightProperty.value: get_key(parser.KEY_ATOMIC_WEIGHT)}
mapper_atomic_weight = SqlMapper(model, parser, bindings, [mapper_element])

model = ElementMassDensityProperty
parser = SargentWelchElementMassDensityParser()
bindings = {ElementMassDensityProperty.element: get_element(parser.KEY_Z),
            ElementMassDensityProperty.value_kg_per_m3: get_key(parser.KEY_DENSITY)}
mapper_mass_density = SqlMapper(model, parser, bindings, [mapper_element])