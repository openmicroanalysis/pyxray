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
from pyxray.property import AtomicSubshellBindingEnergy, XrayTransitionEnergy, XrayTransitionRelativeWeight
from pyxray import xray_transition
from pyxray.base import NotFound

# Globals and constants variables.
logger = logging.getLogger(__name__)

# noinspection PyArgumentList
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


# noinspection PyArgumentList
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


def line_label_lookup(line_label):
    if line_label == 'Kb2':
        line_label = 'Kb2I'
    elif line_label == 'Kb4':
        line_label = 'Kb4I'
    elif line_label == 'Kb5':
        line_label = 'Kb5I'
    elif line_label == 'Leta':
        line_label = 'Ln'
    elif line_label == 'Lb5':
        line_label = 'L3-O5'
    elif line_label == 'Lg11':
        line_label = 'L1-N5'
    elif line_label == 'Lu':
        line_label = 'L3-N7'
    elif line_label == 'L1M1':
        line_label = 'L1-M1'
    elif line_label == 'L1N1':
        line_label = 'L1-N1'
    elif line_label == 'L1N4':
        line_label = 'L1-N4'
    elif line_label == 'L1O1':
        line_label = 'L1-O1'
    elif line_label == 'L1O4':
        line_label = 'L1-O4'
    elif line_label == 'L2M2':
        line_label = 'L2-M2'
    elif line_label == 'L2M5':
        line_label = 'L2-M5'
    elif line_label == 'L2N2':
        line_label = 'L2-N2'
    elif line_label == 'L2N3':
        line_label = 'L2-N3'
    elif line_label == 'L2N5':
        line_label = 'L2-N5'
    elif line_label == 'L2O2':
        line_label = 'L2-O2'
    elif line_label == 'L2O3':
        line_label = 'L2-O3'
    elif line_label == 'L2P2':
        line_label = 'L2-P2'
    elif line_label == 'L2P3':
        line_label = 'L2-P3'
    elif line_label == 'L3N2':
        line_label = 'L3-N2'
    elif line_label == 'L3N3':
        line_label = 'L3-N3'
    elif line_label == 'L3O2':
        line_label = 'L3-O2'
    elif line_label == 'L3O3':
        line_label = 'L3-O3'
    elif line_label == 'L3P1':
        line_label = 'L3-P1'
    elif line_label == 'M2O4':
        line_label = 'M2-O4'
    elif line_label == 'M1N2':
        line_label = 'M1-N2'
    elif line_label == 'M1N3':
        line_label = 'M1-N3'
    elif line_label == 'M2M4':
        line_label = 'M2-M4'
    elif line_label == 'M2N1':
        line_label = 'M2-N1'
    elif line_label == 'M2N4':
        line_label = 'M2-N4'
    elif line_label == 'M3M4':
        line_label = 'M3-M4'
    elif line_label == 'M3M5':
        line_label = 'M3-M5'
    elif line_label == 'M3N1':
        line_label = 'M3-N1'
    elif line_label == 'M3N4':
        line_label = 'M3-N4'
    elif line_label == 'M3O1':
        line_label = 'M3-O1'
    elif line_label == 'M3O4':
        line_label = 'M3-O4'
    elif line_label == 'M3O5':
        line_label = 'M3-O5'
    elif line_label == 'M4N3':
        line_label = 'M4-N3'
    elif line_label == 'M4O2':
        line_label = 'M4-O2'
    elif line_label == 'M5O3':
        line_label = 'M5-O3'
    elif line_label == 'Mz1':
        line_label = 'M5-N3'
    elif line_label == 'Mz2':
        line_label = 'M4-N2'

    return line_label


# noinspection PyArgumentList
class DtsaLineParser(_Parser):

    def __iter__(self):
        relative_path = os.path.join('..', 'data', 'dtsa_line.csv')
        filepath = pkg_resources.resource_filename(__name__, relative_path)

        with open(filepath, 'r') as csv_file:
            reader = csv.reader(csv_file)

            # skip first line
            next(reader)

            line_data = []
            for row in reader:
                try:
                    atomic_number = int(row[0])
                    # noinspection PyPep8Naming
                    energy_eV = float(row[1])
                    fraction = float(row[2])
                    line_label = str(row[3])

                    line_data.append([atomic_number, energy_eV, fraction, line_label])
                except ValueError:
                    pass

        unparse_lines = set()
        length = 2 * len(line_data)
        for atomic_number, energy_eV, fraction, line_label in line_data:
            line_label = line_label_lookup(line_label)

            try:
                transition = xray_transition(line_label)
                element = Element(atomic_number)

                prop = XrayTransitionEnergy(DTSA1992, element, transition, energy_eV)
                # logger.debug('Parsed: {0}'.format(prop))
                self.update(int((atomic_number - 1) / length * 100.0))
                yield prop

                prop = XrayTransitionRelativeWeight(DTSA1992, element, transition, fraction)
                # logger.debug('Parsed: {0}'.format(prop))
                self.update(int((atomic_number - 1) / length * 100.0))
                yield prop

            except NotFound:
                logger.debug('Line not found: {} for {}'.format(line_label, atomic_number))
                unparse_lines.add(line_label)

        logger.debug('Lines not found: {}'.format(sorted(unparse_lines)))
