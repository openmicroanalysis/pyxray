"""
Parsers from JEOL.
"""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)
import os

# Third party modules.
import pkg_resources

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import \
    Reference, Element, XrayTransition, XrayTransitionSet, AtomicSubshell
from pyxray.property import \
    (XrayTransitionEnergy, XrayTransitionSetEnergy,
     XrayTransitionRelativeWeight, XrayTransitionSetRelativeWeight)
from pyxray.util import wavelength_to_energy_eV

# Globals and constants variables.

JEOL = Reference('JEOL'
                 )

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

_TRANSITION_LOOKUP = {
#Siegbahn
'KA1': (L3, K), 'KA2': (L2, K),

'KB1': (M3, K),
'KB2': (N3, K), 'KB2_1': (N3, K), 'KB2+2': (N2, K), 'KB2_2': (N2, K),
'KB3': (M2, K),
'KB4': (N5, K), 'KB4_1': (N5, K), 'KB4_2': (N4, K), 'KB4x': (N4, K),
'KB5': (M5, K), 'KB5_1': (M5, K), 'KB5+2': (M4, K), 'KB5_2': (M4, K),

'LA1': (M5, L3), 'LA2': (M4, L3),

'LN': (M1, L2), 'LL': (M1, L3), 'LS': (M3, L3), 'LT': (M2, L3),
'LV': (N6, L2),

'LB1': (M4, L2), 'LB2': (N5, L3), 'LB3': (M3, L1), 'LB4': (M2, L1),
'LB6': (N1, L3), 'LB7': (O1, L3), 'LB9': (M5, L1), 'LB10': (M4, L1),
'LB15': (N4, L3), 'LB17': (M3, L2),

'LG1': (N4, L2), 'LG2': (N2, L1), 'LG3': (N3, L1), 'LG4': (O3, L1),
'LG4_p': (O2, L1), 'LG5': (N1, L2), 'LG6': (O4, L2), 'LG8': (O1, L2),
'LG8_p': (N6, L2),

'MA1': (N7, M5), 'MA2': (N6, M5),

'MB': (N6, M4),

'MG': (N5, M3),

'MZ1': (N3, M5), 'MZ2': (N2, M4),

#IUPAC
'M1-N2': (N2, M1), 'M1-N3': (N3, M1),
'M2-M4': (M4, M2), 'M2-N1': (N1, M2), 'M2-N4': (N4, M2), 'M2-O4': (O4, M2),
'M3-M5': (M5, M3), 'M3-N1': (N1, M3), 'M3-N4': (N4, M3),
'M4-O2': (O2, M4), 'M4-O3': (O3, M4),
'M5-N1': (N1, M5), 'M5-O3': (O3, M5),
'N6-O4': (O4, N6), 'N7-O5': (O5, N7)
}

_TRANSITION_SET_LOOKUP = {
'KA': [(L3, K), (L2, K)],
'KA1,2': [(L3, K), (L2, K)],
'KB': [(M3, K), (M2, K), (M5, K), (M4, K)],
'KB1,3': [(M3, K), (M2, K)],
'LA1,2': [(M5, L3), (M4, L3)],
'LB5': [(O4, L3), (O5, L3)],
'LB2,15': [(N5, L3), (N4, L3)],
'LB3,4': [(M3, L1), (M2, L1)],
'LG2,3': [(N2, L1), (N3, L1)],
'MA': [(N7, M5), (N6, M5)],
'MZ': [(N3, M5), (N2, M4)],

'K-O2,3': [(O2, K), (O3, K)],
'M1-N2,3': [(N2, M1), (N3, M1)],
'M2,3M4,': [(M4, M2), (M4, M3)],
'M4,5O2,': [(O2, M4), (O2, M5)],
'M3-O4,5': [(O4, M3), (O5, M3)],
'M4-O2,3': [(O2, M4), (O3, M4)],

'LL,N': [(M1, L2), (M1, L3)]
}

#left out Transition Sets: KBX, KB5+, L2,3-M


class JEOLTransitionParser(_Parser):

    def __iter__(self):
        relpath = os.path.join('..', 'data', 'lambda.asc')
        filepath = pkg_resources.resource_filename(__name__, relpath)

        notread = set()
        with open(filepath, 'r') as infile:
            transition_energy = []
            transition_set_energy = []
            for line in infile:
                line = line.strip()
                if not line: continue

                z = int(line[0:2])

                siegbahn = line[10:17].strip()
                if siegbahn.startswith('A'):  # skip absorption edges
                    continue
                if siegbahn.startswith('S'):  # skip satellite lines
                    continue
                if siegbahn not in _TRANSITION_LOOKUP and siegbahn not in _TRANSITION_SET_LOOKUP:  # check for equivalence
                    notread.add(siegbahn)
                    continue

                probability = line[20:23].strip()
                if not probability:  # skip transition with no probability
                    continue
                probability = float(probability) / 100.0

                wavelength = float(line[26:35])
                energy = wavelength_to_energy_eV(wavelength * 1e-10)

                if siegbahn in _TRANSITION_LOOKUP:
                    subshells = list(_TRANSITION_LOOKUP[siegbahn])
                    transition_energy.append((z, subshells, probability, energy))
                    continue

                if siegbahn in _TRANSITION_SET_LOOKUP:
                    transitions = list(_TRANSITION_SET_LOOKUP[siegbahn])
                    transition_set_energy.append((z, transitions, probability, energy))

        length = len(transition_energy)
        for z, subshells, probability, eV in transition_energy:
            if eV is None:
                continue
            transition = XrayTransition(*subshells)
            element = Element(z)

            prop = XrayTransitionEnergy(JEOL, element, transition, eV)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

            prop = XrayTransitionRelativeWeight(JEOL, element, transition, probability)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

        length = len(transition_set_energy)
        for z, transitions, probability, eV in transition_set_energy:
            if eV is None:
                continue
            transitionset = XrayTransitionSet(transitions)
            element = Element(z)

            prop = XrayTransitionSetEnergy(JEOL, element, transitionset, eV)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

            prop = XrayTransitionSetRelativeWeight(JEOL, element, transitionset, probability)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop
