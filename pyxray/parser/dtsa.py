"""
Parsers for DTSA data.
"""

# Standard library modules.
import os
import csv
import logging
import pkgutil

# Third party modules.

# Local modules.
from pyxray.descriptor import Reference, Element, XrayTransition
from pyxray.property import AtomicSubshellBindingEnergy, XrayTransitionEnergy, XrayTransitionRelativeWeight
import pyxray.parser.base as base

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
    'Kedge': base.K,
    'LIedge': base.L1, 'LIIedge': base.L2, 'LIIIedge': base.L3,
    'MIedge': base.M1, 'MIIedge': base.M2, 'MIIIedge': base.M3, 'MIVedge': base.M4, 'MVedge': base.M5,
    'NIedge': base.N1, 'NIIedge': base.N2, 'NIIIedge': base.N3, 'NIVedge': base.N4,
    'NVedge': base.N5, 'NVIedge': base.N6, 'NVIIedge': base.N7,
    'OIedge': base.O1
}

# noinspection PyArgumentList
class DtsaSubshellParser(base._Parser):

    def __iter__(self):
        relative_path = os.path.join('..', 'data', 'dtsa_subshell.csv')
        content = pkgutil.get_data(__name__, relative_path).decode('utf8')
        reader = csv.reader(content.splitlines())

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
'Ka1': base.Ka1, 'Ka2': base.Ka2,
'Kb1': base.Kb1, 'Kb2': base.Kb2, 'Kb3': base.Kb3, 'Kb4': base.Kb4, 'Kb5': base.Kb5,

'La1': base.La1, 'La2': base.La2,
'Lb1': base.Lb1, 'Lb2': base.Lb2, 'Lb3': base.Lb3, 'Lb4': base.Lb4, 'Lb5': base.Lb5,
'Lb6': base.Lb6, 'Lb7': base.Lb7, 'Lb9': base.Lb9, 'Lb10': base.Lb10,
'Lb15': base.Lb15, 'Lb17': base.Lb17,
'Leta': base.Leta,
'Lg1': base.Lg1, 'Lg2': base.Lg2, 'Lg3': base.Lg3, 'Lg4': base.Lg4,
'Lg5': base.Lg5, 'Lg6': base.Lg6, 'Lg8': base.Lg8,
'Lg11': base.Lg11,
'Ll': base.Ll, 'Ls': base.Ls, 'Lt': base.Lt, 'Lv': base.Lv, 'Lu': base.Lu,

'Ma1': base.Ma1, 'Ma2': base.Ma2,
'Mb': base.Mb,
'Mg': base.Mg,
'Mz1': base.Mz1,
'Mz2': base.Mz2,

'N4-N6': XrayTransition(base.N6, base.N4),
'N5-N6': XrayTransition(base.N6, base.N5),

#'Kb2': 'Kb2I',
#'Kb4': 'Kb4I',
#'Kb5': 'Kb5I',
#SKa,SKa',SKa'',SKa3,SKa3',SKa3'',SKa4,SKa5,SKa6,SKa7,SKa8,SKa9,SKb',SKb'',SKb+4,SKb+5,SKb7,SKb8,SKb9,SKbN,SKbX,SLa',SLa+IX,SLa+X,SLa+Y,SLa1+Z,SLa2',SLa3,SLa3+Z,SLa4,SLa5,SLa6,SLa7,SLa8,SLa9,SLaa,SLas,SLb'',SLb1+4,SLb14,SLb2+1,SLb2+2,SLb2+3,SLb2+4,SLb2+5,SLb2+7,SLb2+A,SLb2+B,SLb2+C,SLb5+1,SLb5+2,SLg1',SLg10,SLg2',SLg2'',SLg9,SMa+1,SMa+2,SMa+3,SMa+4,SMb1,SMb2,SMb3,SMg',Skb,Skb10,Skb6

'L1M1': XrayTransition(base.L1, base.M1),
'L1N1': XrayTransition(base.N1, base.L1),
'L1N4': XrayTransition(base.N4, base.L1),
'L1O1': XrayTransition(base.O1, base.L1),
'L1O4': XrayTransition(base.O4, base.L1),
'L2M2': XrayTransition(base.L2, base.M2),
'L2M5': XrayTransition(base.M5, base.L2),
'L2N2': XrayTransition(base.N2, base.L2),
'L2N3': XrayTransition(base.N3, base.L2),
'L2N5': XrayTransition(base.N5, base.L2),
'L2O2': XrayTransition(base.O2, base.L2),
'L2O3': XrayTransition(base.O3, base.L2),
'L2P2': XrayTransition(base.P2, base.L2),
'L2P3': XrayTransition(base.P3, base.L2),
'L3N2': XrayTransition(base.N2, base.L3),
'L3N3': XrayTransition(base.N3, base.L3),
'L3O2': XrayTransition(base.O2, base.L3),
'L3O3': XrayTransition(base.O3, base.L3),
'L3P1': XrayTransition(base.P1, base.L3),
'M2O4': XrayTransition(base.O4, base.M2),
'M1N2': XrayTransition(base.N2, base.M1),
'M1N3': XrayTransition(base.N3, base.M1),
'M2M4': XrayTransition(base.M4, base.M2),
'M2N1': XrayTransition(base.N1, base.M2),
'M2N4': XrayTransition(base.N4, base.M2),
'M3M4': XrayTransition(base.M4, base.M3),
'M3M5': XrayTransition(base.M5, base.M3),
'M3N1': XrayTransition(base.N1, base.M3),
'M3N4': XrayTransition(base.N4, base.M3),
'M3O1': XrayTransition(base.O1, base.M3),
'M3O4': XrayTransition(base.O4, base.M3),
'M3O5': XrayTransition(base.O5, base.M3),
'M4N3': XrayTransition(base.N3, base.M4),
'M4O2': XrayTransition(base.O2, base.M4),
'M5O3': XrayTransition(base.O3, base.M5),

}

# noinspection PyArgumentList
class DtsaLineParser(base._Parser):

    def __iter__(self):
        relative_path = os.path.join('..', 'data', 'dtsa_line.csv')
        content = pkgutil.get_data(__name__, relative_path).decode('utf8')
        reader = csv.reader(content.splitlines())

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
                transition = _TRANSITION_LOOKUP[line_label]
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
