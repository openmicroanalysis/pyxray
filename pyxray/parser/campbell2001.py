"""
Parsers from Campbell.
"""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)
import os

# Third party modules.
import pkg_resources

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Element, AtomicSubshell
from pyxray.property import AtomicSubshellRadiativeWidth

# Globals and constants variables.

CAMPBELL2001 = Reference('campbell2001',
                         author='Campbell, J.L. and Papp, T.',
                         year=2001,
                         title='Widths of the atomic K-N7 levels',
                         booktitle='Atomic Data and Nuclear Data Tables',
                         pages='1-56',
                         volume=77)

_SUBSHELL_LOOKUP = {
    'K': (1, 0, 1),

    'L1': (2, 0, 1), 'L2': (2, 1, 1), 'L3': (2, 1, 3),

    'M1': (3, 0, 1), 'M2': (3, 1, 1), 'M3': (3, 1, 3), 'M4': (3, 2, 3),
    'M5': (3, 2, 5),

    'N1': (4, 0, 1), 'N2': (4, 1, 1), 'N3': (4, 1, 3), 'N4': (4, 2, 3),
    'N5': (4, 2, 5), 'N6': (4, 3, 5), 'N7': (4, 3, 7)
}

subshell_order = ['K', 'L1', 'L2', 'L3', 'M1', 'M2', 'M3', 'M4', 'M5', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7']

class CampbellAtomicSubshellRadiativeWidthParser(_Parser):

    def __iter__(self):
        relpath = os.path.join('..', 'data', 'campbell.asc')
        filepath = pkg_resources.resource_filename(__name__, relpath)

        with open(filepath, 'r') as infile:
            shell_width = []
            for line in infile:
                line = line.strip()
                if not line: continue

                z = int(line[0:2])

                for s in range(1, 17):
                    s_w = line[6 * s:6 * s + 6].strip()
                    if s_w == '': continue
                    shell_width.append([z, subshell_order[s - 1], float(s_w)])

        length = len(shell_width)
        for z, subshell, width in shell_width:
            if width is None:
                continue
            subshell = AtomicSubshell(*_SUBSHELL_LOOKUP[subshell])
            element = Element(z)
            prop = AtomicSubshellRadiativeWidth(CAMPBELL2001, element, subshell, width)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop
