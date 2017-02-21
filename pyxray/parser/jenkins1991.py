"""

"""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, XrayTransition, AtomicSubshell, Notation
from pyxray.property import XrayTransitionNotation

# Globals and constants variables.

JENKINS1991 = Reference('jenkins1991',
                        author='Jenkins, R. and Manne, R. and Robin, R. and Senemaud, C.',
                        journal='X-Ray Spectrometry',
                        doi='10.1002/xrs.1300200308',
                        pages='149--155',
                        title='{IUPAC} --- nomenclature system for x-ray spectroscopy',
                        volume=20,
                        year=1991)

SIEGBAHN = Notation('siegbahn')
IUPAC = Notation('iupac')

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

KA1 = XrayTransition(L3, K)
KA2 = XrayTransition(L2, K)
KB1 = XrayTransition(M3, K)
KB2_1 = XrayTransition(N3, K)
KB2_2 = XrayTransition(N2, K)
KB3 = XrayTransition(M2, K)
KB4_1 = XrayTransition(N5, K)
KB4_2 = XrayTransition(N4, K)
KB4x = XrayTransition(N4, K)
KB5_1 = XrayTransition(M5, K)
KB5_2 = XrayTransition(M4, K)

LA1 = XrayTransition(M5, L3)
LA2 = XrayTransition(M4, L3)
LB1 = XrayTransition(M4, L2)
LB2 = XrayTransition(N5, L3)
LB3 = XrayTransition(M3, L1)
LB4 = XrayTransition(M2, L1)
LB6 = XrayTransition(N1, L3)
LB7 = XrayTransition(O1, L3)
LB9 = XrayTransition(M5, L1)
LB10 = XrayTransition(M4, L1)
LB15 = XrayTransition(N4, L3)
LB17 = XrayTransition(M3, L2)
LG1 = XrayTransition(N4, L2)
LG2 = XrayTransition(N2, L1)
LG3 = XrayTransition(N3, L1)
LG4 = XrayTransition(O3, L1)
LG4_p = XrayTransition(O2, L1)
LG5 = XrayTransition(N1, L2)
LG6 = XrayTransition(O4, L2)
LG8 = XrayTransition(O1, L2)
LG8_p = XrayTransition(N6, L2)
LN = XrayTransition(M1, L2)
LL = XrayTransition(M1, L3)
LS = XrayTransition(M3, L3)
LT = XrayTransition(M2, L3)
LV = XrayTransition(N6, L2)

MA1 = XrayTransition(N7, M5)
MA2 = XrayTransition(N6, M5)
MB = XrayTransition(N6, M4)
MG = XrayTransition(N5, M3)

class Jenkins1991TransitionNotationParser(_Parser):

    def __iter__(self):
        yield XrayTransitionNotation(JENKINS1991, KA1, SIEGBAHN,
                                     'Ka1',
                                     'K\u03b11',
                                     'K&alpha;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{K}\\alpha_1}')
        yield XrayTransitionNotation(JENKINS1991, KA2, SIEGBAHN,
                                     'Ka2',
                                     'K\u03b12',
                                     'K&alpha;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{K}\\alpha_2}')
        yield XrayTransitionNotation(JENKINS1991, KB1, SIEGBAHN,
                                     'Kb1',
                                     'K\u03b21',
                                     'K&beta;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{K}\\beta_1}')
        yield XrayTransitionNotation(JENKINS1991, KB2_1, SIEGBAHN,
                                     'Kb2I',
                                     'K\u03b22I',
                                     'K&beta;<sub>2</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_2^I}')
        yield XrayTransitionNotation(JENKINS1991, KB2_2, SIEGBAHN,
                                     'Kb2II',
                                     'K\u03b22II',
                                     'K&beta;<sub>2</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_2^{II}}')
        yield XrayTransitionNotation(JENKINS1991, KB3, SIEGBAHN,
                                     'Kb3',
                                     'K\u03b23',
                                     'K&beta;<sub>3</sub>',
                                    '\\ensuremath{\\mathrm{K}\\beta_3}')
        yield XrayTransitionNotation(JENKINS1991, KB4_1, SIEGBAHN,
                                     'Kb4I',
                                     'K\u03b24I',
                                     'K&beta;<sub>4</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_4^I}')
        yield XrayTransitionNotation(JENKINS1991, KB4_2, SIEGBAHN,
                                     'Kb4II',
                                     'K\u03b24II',
                                     'K&beta;<sub>4</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_4^{II}}')
        yield XrayTransitionNotation(JENKINS1991, KB4x, SIEGBAHN,
                                     'Kb4x',
                                     'K\u03b24x',
                                     'K&beta;<sub>4x</sub>',
                                     '\\ensuremath{\\mathrm{K}\\beta_{4x}}')
        yield XrayTransitionNotation(JENKINS1991, KB5_1, SIEGBAHN,
                                     'Kb5I',
                                     'K\u03b25I',
                                     'K&beta;<sub>5</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_5^I}')
        yield XrayTransitionNotation(JENKINS1991, KB5_2, SIEGBAHN,
                                     'Kb5II',
                                     'K\u03b25II',
                                     'K&beta;<sub>5</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_5^{II}}')

        yield XrayTransitionNotation(JENKINS1991, LA1, SIEGBAHN,
                                     'La1',
                                     'L\u03b11',
                                     'L&alpha;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}\\alpha_1}')
        yield XrayTransitionNotation(JENKINS1991, LA2, SIEGBAHN,
                                     'La2',
                                     'L\u03b12',
                                     'L&alpha;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{L}\\alpha_2}')
        yield XrayTransitionNotation(JENKINS1991, LB1, SIEGBAHN,
                                     'Lb1',
                                     'L\u03b21',
                                     'L&beta;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_1}')
        yield XrayTransitionNotation(JENKINS1991, LB2, SIEGBAHN,
                                     'Lb2',
                                     'L\u03b22',
                                     'L&beta;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_2}')
        yield XrayTransitionNotation(JENKINS1991, LB3, SIEGBAHN,
                                     'Lb3',
                                     'L\u03b23',
                                     'L&beta;<sub>3</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_3}')
        yield XrayTransitionNotation(JENKINS1991, LB4, SIEGBAHN,
                                     'Lb4',
                                     'L\u03b24',
                                     'L&beta;<sub>4</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_4}')
        yield XrayTransitionNotation(JENKINS1991, LB6, SIEGBAHN,
                                     'Lb6',
                                     'L\u03b26',
                                     'L&beta;<sub>6</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_6}')
        yield XrayTransitionNotation(JENKINS1991, LB7, SIEGBAHN,
                                     'Lb7',
                                     'L\u03b27',
                                     'L&beta;<sub>7</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_7}')
        yield XrayTransitionNotation(JENKINS1991, LB9, SIEGBAHN,
                                     'Lb9',
                                     'L\u03b29',
                                     'L&beta;<sub>9</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_9}')
        yield XrayTransitionNotation(JENKINS1991, LB10, SIEGBAHN,
                                     'Lb10',
                                     'L\u03b210',
                                     'L&beta;<sub>10</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{10}}')
        yield XrayTransitionNotation(JENKINS1991, LB15, SIEGBAHN,
                                     'Lb15',
                                     'L\u03b215',
                                     'L&beta;<sub>15</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{15}}')
        yield XrayTransitionNotation(JENKINS1991, LB17, SIEGBAHN,
                                     'Lb17',
                                     'L\u03b217',
                                     'L&beta;<sub>17</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{17}}')
        yield XrayTransitionNotation(JENKINS1991, LG1, SIEGBAHN,
                                     'Lg1',
                                     'L\u03b31',
                                     'L&gamma;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_1}')
        yield XrayTransitionNotation(JENKINS1991, LG2, SIEGBAHN,
                                     'Lg2',
                                     'L\u03b32',
                                     'L&gamma;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_2}')
        yield XrayTransitionNotation(JENKINS1991, LG3, SIEGBAHN,
                                     'Lg3',
                                     'L\u03b33',
                                     'L&gamma;<sub>3</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_3}')
        yield XrayTransitionNotation(JENKINS1991, LG4, SIEGBAHN,
                                     'Lg4',
                                     'L\u03b34',
                                     'L&gamma;<sub>4</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_4}')
        yield XrayTransitionNotation(JENKINS1991, LG4_p, SIEGBAHN,
                                     "Lg4'",
                                     "L\u03b34\u2032",
                                     'L&gamma;<sub>4&prime;</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_{4\\prime}}')
        yield XrayTransitionNotation(JENKINS1991, LG5, SIEGBAHN,
                                     'Lg5',
                                     'L\u03b35',
                                     'L&gamma;<sub>5</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_5}')
        yield XrayTransitionNotation(JENKINS1991, LG6, SIEGBAHN,
                                     'Lg6',
                                     'L\u03b36',
                                     'L&gamma;<sub>6</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_6}')
        yield XrayTransitionNotation(JENKINS1991, LG8, SIEGBAHN,
                                     'Lg8',
                                     'L\u03b38',
                                     'L&gamma;<sub>8</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_8}')
        yield XrayTransitionNotation(JENKINS1991, LG8_p, SIEGBAHN,
                                     "Lg8'",
                                     "L\u03b38\u2032",
                                     'L&gamma;<sub>8&prime;</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_{8\\prime}}')
        yield XrayTransitionNotation(JENKINS1991, LN, SIEGBAHN,
                                     'Ln',
                                     'L\u03b7',
                                     'L&eta;',
                                     '\\ensuremath{\\mathrm{L}\\eta}')
        yield XrayTransitionNotation(JENKINS1991, LL, SIEGBAHN,
                                     'Ll',
                                     'L\u2113',
                                     'L&#x2113;',
                                     '\\ensuremath{\\mathrm{L}\\ell}')
        yield XrayTransitionNotation(JENKINS1991, LS, SIEGBAHN,
                                     'Ls',
                                     'Ls',
                                     'Ls',
                                     '\\ensuremath{\\mathrm{L}s}')
        yield XrayTransitionNotation(JENKINS1991, LT, SIEGBAHN,
                                     'Lt',
                                     'Lt',
                                     'Lt',
                                     '\\ensuremath{\\mathrm{L}t}')
        yield XrayTransitionNotation(JENKINS1991, LV, SIEGBAHN,
                                     'Lv',
                                     'Lv',
                                     'Lv',
                                     '\\ensuremath{\\mathrm{L}v}')

        yield XrayTransitionNotation(JENKINS1991, MA1, SIEGBAHN,
                                     'Ma1',
                                     'M\u03b11',
                                     'M&alpha;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{M}\\alpha_1}')
        yield XrayTransitionNotation(JENKINS1991, MA2, SIEGBAHN,
                                     'Ma2',
                                     'M\u03b12',
                                     'M&alpha;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{M}\\alpha_2}')
        yield XrayTransitionNotation(JENKINS1991, MB, SIEGBAHN,
                                     'Mb',
                                     'M\u03b2',
                                     'M&beta;',
                                     '\\ensuremath{\\mathrm{M}\\beta}')
        yield XrayTransitionNotation(JENKINS1991, MG, SIEGBAHN,
                                     'Mg',
                                     'M\u03b3',
                                     'M&gamma;',
                                     '\\ensuremath{\\mathrm{M}\\gamma}')


