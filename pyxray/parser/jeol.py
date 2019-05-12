"""
Parsers from JEOL.
"""

# Standard library modules.
import logging
import os
import pkgutil

# Third party modules.

# Local modules.
from pyxray.descriptor import Reference, Element, XrayTransition
from pyxray.property import XrayTransitionEnergy, XrayTransitionRelativeWeight
from pyxray.util import wavelength_to_energy_eV
import pyxray.parser.base as base

# Globals and constants variables.
logger = logging.getLogger(__name__)

JEOL = Reference('JEOL'
                 )

_TRANSITION_LOOKUP = {
# Siegbahn
'KA1': base.Ka1, 'KA2': base.Ka2,
'KB1': base.Kb1,
'KB2': base.Kb2, 'KB2_1': base.Kb2_1, 'KB2+2': base.Kb2_2, 'KB2_2': base.Kb2_2,
'KB3': base.Kb3,
'KB4': base.Kb4, 'KB4_1': base.Kb4_1, 'KB4_2': base.Kb4_2, 'KB4x': base.Kb4_2,
'KB5': base.Kb5, 'KB5_1': base.Kb5_1, 'KB5+2': base.Kb5_2, 'KB5_2': base.Kb5_2,

'LA1': base.La1, 'LA2':  base.La2,
'LN': base.Ln, 'LL': base.Ll, 'LS': base.Ls, 'LT': base.Lt, 'LV': base.Lv,
'LB1': base.Lb1, 'LB2': base.Lb2, 'LB3': base.Lb3, 'LB4': base.Lb4,
'LB6': base.Lb6, 'LB7': base.Lb7, 'LB9': base.Lb9, 'LB10': base.Lb10,
'LB15': base.Lb15, 'LB17': base.Lb17,
'LG1': base.Lg1, 'LG2': base.Lg2, 'LG3': base.Lg3, 'LG4': base.Lg4,
'LG4_p': base.Lg4p, 'LG5': base.Lg5, 'LG6': base.Lg6, 'LG8': base.Lg8,

'MA1': base.Ma1, 'MA2': base.Ma2,
'MB': base.Mb,
'MG': base.Mg,
'MZ1': base.Mz1, 'MZ2': base.Mz2,

# IUPAC
'M1-N2': XrayTransition(base.N2, base.M1),
'M1-N3': XrayTransition(base.N3, base.M1),
'M2-M4': XrayTransition(base.M4, base.M2),
'M2-N1': XrayTransition(base.N1, base.M2),
'M2-N4': XrayTransition(base.N4, base.M2),
'M2-O4': XrayTransition(base.O4, base.M2),
'M3-M5': XrayTransition(base.M5, base.M3),
'M3-N1': XrayTransition(base.N1, base.M3),
'M3-N4': XrayTransition(base.N4, base.M3),
'M4-O2': XrayTransition(base.O2, base.M4),
'M4-O3': XrayTransition(base.O3, base.M4),
'M5-N1': XrayTransition(base.N1, base.M5),
'M5-O3': XrayTransition(base.O3, base.M5),
'N6-O4': XrayTransition(base.O4, base.N6),
'N7-O5': XrayTransition(base.O5, base.N7),

# Set
#left out transition sets: KBX, KB5+, L2,3-M
'KA': base.Ka,
'KA1,2': base.Ka,
# 'KB': [(M3, K), (M2, K), (M5, K), (M4, K)], # FIXME: Not quite sure what to do with Kb
'KB1,3': base.Kb1_3,
'LA1,2': base.La,
'LB2,15': base.Lb2_15,
'LB5': base.Lb5,
'LB3,4': base.Lb3_4,
'LG2,3': base.Lg2_3,
'MA': base.Ma,
'MZ': base.Mz,

'K-O2,3': base.KO2_3,
'M1-N2,3': base.M1N2_3,
'M2,3M4,5': base.M2_3M4_5,
'M4,5O2,3': base.M4_5O2_3,
'M3-O4,5': base.M3O4_5,
'M4-O2,3': base.M4O2_3,

'LL,N': base.Ll_n,
}

class JEOLTransitionParser(base._Parser):

    def __iter__(self):
        relpath = os.path.join('..', 'data', 'lambda.asc')
        content = pkgutil.get_data(__name__, relpath).decode('utf8')

        notread = set()
        transition_energy = []
        for line in content.splitlines():
            line = line.strip()
            if not line: continue

            z = int(line[0:2])

            siegbahn = line[10:18].strip()
            if siegbahn.startswith('A'):  # skip absorption edges
                continue
            if siegbahn.startswith('S'):  # skip satellite lines
                continue
            if siegbahn not in _TRANSITION_LOOKUP:  # check for equivalence
                notread.add(siegbahn)
                continue

            probability = line[20:23].strip()
            if not probability:  # skip transition with no probability
                continue
            probability = float(probability) / 100.0

            wavelength = float(line[26:35])
            energy = wavelength_to_energy_eV(wavelength * 1e-10)

            if siegbahn in _TRANSITION_LOOKUP:
                transition = _TRANSITION_LOOKUP[siegbahn]
                transition_energy.append((z, transition, probability, energy))
                continue

        length = len(transition_energy)
        for z, transition, probability, eV in transition_energy:
            if eV is None:
                continue
            element = Element(z)

            prop = XrayTransitionEnergy(JEOL, element, transition, eV)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

            prop = XrayTransitionRelativeWeight(JEOL, element, transition, probability)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

        logger.debug(notread)
