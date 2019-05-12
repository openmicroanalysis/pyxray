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
import pyxray.parser.base as base
from pyxray.descriptor import Reference, Element
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
    'K': base.K,
    'L1': base.L1, 'L2': base.L2, 'L3': base.L3,
    'M1': base.M1, 'M2': base.M2, 'M3': base.M3, 'M4': base.M4, 'M5': base.M5,
    'N1': base.N1, 'N2': base.N2, 'N3': base.N3, 'N4': base.N4, 'N5': base.N5, 'N6': base.N6, 'N7': base.N7
}

subshell_order = ['K', 'L1', 'L2', 'L3', 'M1', 'M2', 'M3', 'M4', 'M5', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7']

class CampbellAtomicSubshellRadiativeWidthParser(base._Parser):

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
            subshell = _SUBSHELL_LOOKUP[subshell]
            element = Element(z)
            prop = AtomicSubshellRadiativeWidth(CAMPBELL2001, element, subshell, width)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop
