""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.bearden1967 import Bearden1967XrayTransitionNotationParser

# Globals and constants variables.

def test_bearden1967():
    parser = Bearden1967XrayTransitionNotationParser()
    assert len(list(parser)) == 5