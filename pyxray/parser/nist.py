"""
Parsers from NIST.
"""

# Standard library modules.
import logging
import re
import os
import pkgutil

# Third party modules.

# Local modules.
import pyxray.parser.base as base
from pyxray.descriptor import Reference, Element
from pyxray.property import ElementAtomicWeight

# Globals and constants variables.
logger = logging.getLogger(__name__)

NIST = Reference('coursey2015',
                 author='J. S. Coursey, D. J. Schwab, J. J. Tsai, R. A. Dragoset',
                 title='Atomic Weights and Isotopic Compositions',
                 organization='NIST Physical Measurement Laboratory',
                 year=2015)

class NISTElementAtomicWeightParser(base._Parser):

    def __iter__(self):
        relpath = os.path.join('..', 'data', 'nist_element_atomic_weight.html')
        content = pkgutil.get_data(__name__, relpath).decode('utf8')

        current_z = "1"
        value = 0

        atomic_weights = []
        for line in content.splitlines():
            z = re.search(r"Atomic\sNumber\s=\s([0-9]*)", line)
            relative_mass = re.search(r"Relative\sAtomic\sMass\s=\s([0-9]*.{0,1}[0-9]*)", line)
            composition = re.search(r"Isotopic\sComposition\s=\s([0-9]*.{0,1}[0-9]*)", line)
            if z != None:
                if current_z != z.group(1):
                    current_z = z.group(1)
                    if value == 0:
                        value = None
                    atomic_weights.append(value)
                    value = 0
            elif relative_mass != None:
                if relative_mass.group(1) == '':
                    r_m = 0.0
                else:
                    r_m = float(relative_mass.group(1))
            elif composition != None:
                if composition.group(1) == '':
                    c = 0.0
                else:
                    c = float(composition.group(1))
                value = value + r_m * c

        length = len(atomic_weights)
        for z, aw in enumerate(atomic_weights, 1):
            if aw is None:
                continue
            element = Element(z)
            prop = ElementAtomicWeight(NIST, element, aw)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop
