"""
Parsers for DTSA data.
"""

# Standard library modules.
import os
import csv
import logging

# Third party modules.
import pkg_resources

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Element, AtomicSubshell
from pyxray.property import AtomicSubshellBindingEnergy

# Globals and constants variables.
logger = logging.getLogger(__name__)


DTSA1992 = Reference('dtsa1992',
                     author='C.E. Fiori and C.R. Swyt and R.L. Myklebust',
                     year=1992,
                     title='NIST/NIH Desk Top Spectrum Analyzer',
                     url='https://www.cstl.nist.gov/div837/Division/outputs/DTSA/oldDTSA.htm')

# noinspection SpellCheckingInspection
_SUBSHELL_LOOKUP = {
    'Kedge': (1, 0, 1),

    'LIedge': (2, 0, 1), 'LIIedge': (2, 1, 1), 'LIIIedge': (2, 1, 3),

    'MIedge': (3, 0, 1), 'MIIedge': (3, 1, 1), 'MIIIedge': (3, 1, 3), 'MIVedge': (3, 2, 3),
    'MVedge': (3, 2, 5),

    'NIedge': (4, 0, 1), 'NIIedge': (4, 1, 1), 'NIIIedge': (4, 1, 3), 'NIVedge': (4, 2, 3),
    'NVedge': (4, 2, 5), 'NVIedge': (4, 3, 5), 'NVIIedge': (4, 3, 7),

    'OIedge': (5, 0, 1)
}


class DtsaSubshellParser(_Parser):

    def __iter__(self):
        relative_path = os.path.join('..', 'data', 'dtsa_subshell.csv')
        filepath = pkg_resources.resource_filename(__name__, relative_path)

        with open(filepath, 'r') as csv_file:
            reader = csv.reader(csv_file)

            # skip first line
            next(reader)

            subshell_data = []
            for row in reader:
                atomic_number = int(row[0])
                # noinspection PyPep8Naming
                energy_eV = float(row[1])
                subshell = str(row[2])

                subshell_data.append([atomic_number, energy_eV, subshell])

        length = len(subshell_data)
        for atomic_number, energy_eV, subshell_dtsa in subshell_data:

            subshell = AtomicSubshell(*_SUBSHELL_LOOKUP[subshell_dtsa])
            element = Element(atomic_number)
            prop = AtomicSubshellBindingEnergy(DTSA1992, element, subshell, energy_eV)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((atomic_number - 1) / length * 100.0))
            yield prop
