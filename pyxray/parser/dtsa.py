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
from pyxray.descriptor import Reference, Element, AtomicSubshell, XrayTransition
from pyxray.property import AtomicSubshellBindingEnergy, XrayTransitionEnergy, XrayTransitionRelativeWeight

# Globals and constants variables.
logger = logging.getLogger(__name__)

# noinspection PyArgumentList
DTSA1992 = Reference('dtsa1992',
                     author='C.E. Fiori and C.R. Swyt and R.L. Myklebust',
                     year=1992,
                     title='NIST/NIH Desk Top Spectrum Analyzer',
                     url='https://www.cstl.nist.gov/div837/Division/outputs/DTSA/oldDTSA.htm')

K = AtomicSubshell(1, 0, 1)
L1 = AtomicSubshell(2, 0, 1)
L2 = AtomicSubshell(2, 1, 1)
L3 = AtomicSubshell(2, 1, 3)
M1 = AtomicSubshell(3, 0, 1)
M2 = AtomicSubshell(3, 1, 1)
M3 = AtomicSubshell(3, 1, 3)
M4 = AtomicSubshell(3, 2, 3)
M5 = AtomicSubshell(3, 2, 5)
N1 = AtomicSubshell(4, 0, 1)
N2 = AtomicSubshell(4, 1, 1)
N3 = AtomicSubshell(4, 1, 3)
N4 = AtomicSubshell(4, 2, 3)
N5 = AtomicSubshell(4, 2, 5)
N6 = AtomicSubshell(4, 3, 5)
N7 = AtomicSubshell(4, 3, 7)
O1 = AtomicSubshell(5, 0, 1)
O2 = AtomicSubshell(5, 1, 1)
O3 = AtomicSubshell(5, 1, 3)
O4 = AtomicSubshell(5, 2, 3)
O5 = AtomicSubshell(5, 2, 5)
O6 = AtomicSubshell(5, 3, 5)
O7 = AtomicSubshell(5, 3, 7)
O8 = AtomicSubshell(5, 4, 7)
O9 = AtomicSubshell(5, 4, 9)
P1 = AtomicSubshell(6, 0, 1)
P2 = AtomicSubshell(6, 1, 1)
P3 = AtomicSubshell(6, 1, 3)

# noinspection SpellCheckingInspection
_SUBSHELL_LOOKUP = {
    'Kedge': K,

    'LIedge': L1, 'LIIedge': L2, 'LIIIedge': L3,

    'MIedge': M1, 'MIIedge': M2, 'MIIIedge': M3, 'MIVedge': M4, 'MVedge': M5,

    'NIedge': N1, 'NIIedge': N2, 'NIIIedge': N3, 'NIVedge': N4,
    'NVedge': N5, 'NVIedge': N6, 'NVIIedge': N7,

    'OIedge': O1
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

            subshell = _SUBSHELL_LOOKUP[subshell_dtsa]
            element = Element(atomic_number)
            prop = AtomicSubshellBindingEnergy(DTSA1992, element, subshell, energy_eV)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((atomic_number - 1) / length * 100.0))
            yield prop

_TRANSITION_LOOKUP = {
'Ka1': (L3, K), 'Ka2': (L2, K),
'Kb1': (M3, K), 'Kb2': (N3, K), 'Kb3': (M2, K), 'Kb4': (N5, K), 'Kb5': (M5, K),

'La1': (M5, L3), 'La2': (M4, L3),
'Lb1': (M4, L2), 'Lb2': (N5, L3), 'Lb3': (M3, L1), 'Lb4': (M2, L1), 'Lb5': (O5, L3),
'Lb6': (N1, L3), 'Lb7': (O1, L3), 'Lb9': (M5, L1), 'Lb10': (M4, L1),
'Lb15': (N4, L3), 'Lb17': (M3, L2),
'Leta': (M1, L2),
'Lg1': (N4, L2), 'Lg2': (N2, L1), 'Lg3': (N3, L1), 'Lg4': (O3, L1),
'Lg5': (N1, L2), 'Lg6': (O4, L2), 'Lg8': (O1, L2),
'Lg11':  (N5, L1),
'Ll': (M1, L3), 'Ls': (M3, L3), 'Lt': (M2, L3), 'Lv': (N6, L2), 'Lu': (N7, L3),

'Ma1': (N7, M5), 'Ma2': (N6, M5),
'Mb': (N6, M4),
'Mg': (N5, M3),
'Mz1': (M5, N3),
'Mz2':(M4, N2),

'N4-N6': (N6, N4),
'N5-N6': (N6, N5),

#'Kb2': 'Kb2I',
#'Kb4': 'Kb4I',
#'Kb5': 'Kb5I',
#SKa,SKa',SKa'',SKa3,SKa3',SKa3'',SKa4,SKa5,SKa6,SKa7,SKa8,SKa9,SKb',SKb'',SKb+4,SKb+5,SKb7,SKb8,SKb9,SKbN,SKbX,SLa',SLa+IX,SLa+X,SLa+Y,SLa1+Z,SLa2',SLa3,SLa3+Z,SLa4,SLa5,SLa6,SLa7,SLa8,SLa9,SLaa,SLas,SLb'',SLb1+4,SLb14,SLb2+1,SLb2+2,SLb2+3,SLb2+4,SLb2+5,SLb2+7,SLb2+A,SLb2+B,SLb2+C,SLb5+1,SLb5+2,SLg1',SLg10,SLg2',SLg2'',SLg9,SMa+1,SMa+2,SMa+3,SMa+4,SMb1,SMb2,SMb3,SMg',Skb,Skb10,Skb6

'L1M1': (L1, M1),
'L1N1': (N1, L1),
'L1N4': (N4, L1),
'L1O1': (O1, L1),
'L1O4': (O4, L1),
'L2M2': (L2, M2),
'L2M5': (M5, L2),
'L2N2': (N2, L2),
'L2N3': (N3, L2),
'L2N5': (N5, L2),
'L2O2': (O2, L2),
'L2O3': (O3, L2),
'L2P2': (P2, L2),
'L2P3': (P3, L2),
'L3N2': (N2, L3),
'L3N3': (N3, L3),
'L3O2': (O2, L3),
'L3O3': (O3, L3),
'L3P1': (P1, L3),
'M2O4': (O4, M2),
'M1N2': (N2, M1),
'M1N3': (N3, M1),
'M2M4': (M4, M2),
'M2N1': (N1, M2),
'M2N4': (N4, M2),
'M3M4': (M4, M3),
'M3M5': (M5, M3),
'M3N1': (N1, M3),
'M3N4': (N4, M3),
'M3O1': (O1, M3),
'M3O4': (O4, M3),
'M3O5': (O5, M3),
'M4N3': (N3, M4),
'M4O2': (O2, M4),
'M5O3': (O3, M5),

}

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
            try:
                transition = XrayTransition(*_TRANSITION_LOOKUP[line_label])
            except KeyError:
#                logger.debug('Line not found: {} for {}'.format(line_label, atomic_number))
                unparse_lines.add(line_label)
                continue

            element = Element(atomic_number)

            prop = XrayTransitionEnergy(DTSA1992, element, transition, energy_eV)
#                logger.debug('Parsed: {0}'.format(prop))
            self.update(int((atomic_number - 1) / length * 100.0))
            yield prop

            prop = XrayTransitionRelativeWeight(DTSA1992, element, transition, fraction)
#                logger.debug('Parsed: {0}'.format(prop))
            self.update(int((atomic_number - 1) / length * 100.0))
            yield prop

        logger.debug('Lines not found: {}'.format(sorted(unparse_lines)))
