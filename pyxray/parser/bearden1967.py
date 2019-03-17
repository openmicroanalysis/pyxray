""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Notation, XrayTransition, AtomicSubshell
from pyxray.property import XrayTransitionNotation

# Globals and constants variables.

BEARDEN1967 = Reference('bearden1967',
                        author='Bearden, J. A.',
                        journal='Rev. Mod. Phys.',
                        doi='10.1103/RevModPhys.39.78',
                        pages='78--124',
                        title='X-Ray Wavelengths',
                        volume=39,
                        year=1967)

SIEGBAHN = Notation('siegbahn')

L1 = AtomicSubshell(2, 0, 1)
L3 = AtomicSubshell(2, 1, 3)
M4 = AtomicSubshell(3, 2, 3)
M5 = AtomicSubshell(3, 2, 5)
N2 = AtomicSubshell(4, 1, 1)
N3 = AtomicSubshell(4, 1, 3)
N5 = AtomicSubshell(4, 2, 5)
N7 = AtomicSubshell(4, 3, 7)
O5 = AtomicSubshell(5, 2, 5)

class Bearden1967XrayTransitionNotationParser(_Parser):

    def __iter__(self):
        LB5 = XrayTransition(O5, L3)
        yield XrayTransitionNotation(BEARDEN1967, LB5, SIEGBAHN,
                                     'Lb5',
                                     'L\u03b25',
                                     'L&beta;<sub>5</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_5}')

        LG11 = XrayTransition(N5, L1)
        yield XrayTransitionNotation(BEARDEN1967, LG11, SIEGBAHN,
                                     'Lg11',
                                     'L\u03b311',
                                     'L&gamma;<sub>11</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_11}')

        LU = XrayTransition(N7, L3)
        yield XrayTransitionNotation(BEARDEN1967, LU, SIEGBAHN,
                                     'Lu',
                                     'Lu',
                                     'Lu',
                                     '\\ensuremath{\\mathrm{L}u}')

        MZ1 = XrayTransition(N3, M5)
        yield XrayTransitionNotation(BEARDEN1967, MZ1, SIEGBAHN,
                                     'Mz1',
                                     'M\u03961',
                                     'M&zeta;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{M}\\zeta_1}')

        MZ2 = XrayTransition(N2, M4)
        yield XrayTransitionNotation(BEARDEN1967, MZ2, SIEGBAHN,
                                     'Mz2',
                                     'M\u03962',
                                     'M&zeta;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{M}\\zeta_2}')
