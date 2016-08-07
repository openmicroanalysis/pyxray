""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.sql.mapping.mapper import SqlMapper
from pyxray.sql.mapping.base import mapper_element
from pyxray.sql.mapping.util import get_key, get_element
from pyxray.sql.model import ElementNameProperty
from pyxray.parser.wikipedia import WikipediaElementNameParser

# Globals and constants variables.

model = ElementNameProperty
parser = WikipediaElementNameParser()
bindings = {ElementNameProperty.element: get_element(parser.KEY_Z),
            ElementNameProperty.language_code: get_key(parser.KEY_LANGUAGE_CODE),
            ElementNameProperty.name: get_key(parser.KEY_NAME)}
mapper_name = SqlMapper(model, parser, bindings, [mapper_element])

