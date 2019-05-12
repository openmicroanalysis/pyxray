"""

"""

# Standard library modules.
import logging

# Third party modules.

# Local modules.
import pyxray.parser.base as base
from pyxray.descriptor import Element, Reference, XrayTransition, AtomicShell, AtomicSubshell, Notation
from pyxray.property import ElementSymbol, AtomicShellNotation, AtomicSubshellNotation, XrayTransitionNotation

# Globals and constants variables.
logger = logging.getLogger(__name__)

JENKINS1991 = Reference('jenkins1991',
                        author='Jenkins, R. and Manne, R. and Robin, R. and Senemaud, C.',
                        journal='X-Ray Spectrometry',
                        doi='10.1002/xrs.1300200308',
                        pages='149--155',
                        title='{IUPAC} --- nomenclature system for x-ray spectroscopy',
                        volume=20,
                        year=1991)

BEARDEN1967 = Reference('bearden1967',
                        author='Bearden, J. A.',
                        journal='Rev. Mod. Phys.',
                        doi='10.1103/RevModPhys.39.78',
                        pages='78--124',
                        title='X-Ray Wavelengths',
                        volume=39,
                        year=1967)

class ElementSymbolParser(base._Parser):

    SYMBOLS = [
        "H"  , "He" , "Li" , "Be" , "B"  , "C"  , "N"  , "O",
        "F"  , "Ne" , "Na" , "Mg" , "Al" , "Si" , "P"  , "S",
        "Cl" , "Ar" , "K"  , "Ca" , "Sc" , "Ti" , "V"  , "Cr",
        "Mn" , "Fe" , "Co" , "Ni" , "Cu" , "Zn" , "Ga" , "Ge",
        "As" , "Se" , "Br" , "Kr" , "Rb" , "Sr" , "Y"  , "Zr",
        "Nb" , "Mo" , "Tc" , "Ru" , "Rh" , "Pd" , "Ag" , "Cd",
        "In" , "Sn" , "Sb" , "Te" , "I"  , "Xe" , "Cs" , "Ba",
        "La" , "Ce" , "Pr" , "Nd" , "Pm" , "Sm" , "Eu" , "Gd",
        "Tb" , "Dy" , "Ho" , "Er" , "Tm" , "Yb" , "Lu" , "Hf",
        "Ta" , "W"  , "Re" , "Os" , "Ir" , "Pt" , "Au" , "Hg",
        "Tl" , "Pb" , "Bi" , "Po" , "At" , "Rn" , "Fr" , "Ra",
        "Ac" , "Th" , "Pa" , "U"  , "Np" , "Pu" , "Am" , "Cm",
        "Bk" , "Cf" , "Es" , "Fm" , "Md" , "No" , "Lr" , "Rf",
        "Db" , "Sg" , "Bh" , "Hs" , "Mt" , "Ds" , "Rg" , "Cn",
        "Uut", "Fl" , "Uup", "Lv" , "Uus", "Uuo"
    ]

    def __iter__(self):
        length = len(self.SYMBOLS)
        for z, symbol in enumerate(self.SYMBOLS, 1):
            prop = ElementSymbol(base.UNATTRIBUTED, Element(z), symbol)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

MAX_N = 7

def iter_subshells(max_n):
    nprev = 0
    for n in range(1, max_n + 1):
        if nprev != n:
            i = 1

        for l in range(0, n):
            for j in set([abs(l + 0.5), abs(l - 0.5)]):
                j_n = int(j * 2)
                yield n, l, j_n, i
                i += 1
                nprev = n

def iter_transitions(max_n):
    for src_n, src_l, src_j_n, src_i in iter_subshells(max_n):

        for dst_n, dst_l, dst_j_n, dst_i in iter_subshells(MAX_N):
            # Cannot transition to itself
            if src_n == dst_n and src_l == dst_l and src_j_n == dst_j_n:
                continue

            # Transition must be from more to less energytic shell or
            # within the same shell
            if src_n < dst_n:
                continue

            # Coster-Kroning transition must be from more to less energetic subshells
            if src_n == dst_n and src_i <= dst_i:
                continue

            yield XrayTransition(src_n, src_l, src_j_n, dst_n, dst_l, dst_j_n), src_i, dst_i

class AtomicShellNotationParser(base._Parser):

    SIEGBAHN_SHELLS = ['K', 'L', 'M', 'N', 'O', 'P', 'Q']
    IUPAC_SHELLS = ['K', 'L', 'M', 'N', 'O', 'P', 'Q']
    ORBITAL_SHELLS = ['1', '2', '3', '4', '5', '6', '7']

    @classmethod
    def _create_entry_siegbahn(cls, n):
        s = cls.SIEGBAHN_SHELLS[n - 1]
        return s, s, s, s

    @classmethod
    def _create_entry_iupac(cls, n):
        s = cls.IUPAC_SHELLS[n - 1]
        return s, s, s, s

    @classmethod
    def _create_entry_orbital(cls, n):
        s = cls.ORBITAL_SHELLS[n - 1]
        return s, s, s, s

    def __iter__(self):
        length = MAX_N * 3
        progress = 0
        for n in range(1, MAX_N + 1):
            self.update(int(progress / length * 100.0))
            progress += 1

            atomic_shell = AtomicShell(n)

            ascii, utf16, html, latex = self._create_entry_siegbahn(n)
            prop = AtomicShellNotation(base.UNATTRIBUTED,
                                       atomic_shell,
                                       base.SIEGBAHN,
                                       ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            ascii, utf16, html, latex = self._create_entry_iupac(n)
            prop = AtomicShellNotation(base.UNATTRIBUTED,
                                       atomic_shell,
                                       base.IUPAC,
                                       ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            ascii, utf16, html, latex = self._create_entry_orbital(n)
            prop = AtomicShellNotation(base.UNATTRIBUTED,
                                       atomic_shell,
                                       base.ORBITAL,
                                       ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

class AtomicSubshellNotationParser(base._Parser):

    SIEGBAHN_NUMBERS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII',
                        'IX', 'X', 'XI', 'XII', 'XIII']
    ORBITAL_L = ['s', 'p', 'd', 'f', 'g', 'h', 'i']

    @classmethod
    def _create_entry_siegbahn(cls, n, l, j_n, i):
        shell = AtomicShellNotationParser.SIEGBAHN_SHELLS[n - 1]
        s = shell
        if n != 1: # No KI
            s += cls.SIEGBAHN_NUMBERS[i - 1]
        return s, s, s, s

    @classmethod
    def _create_entry_iupac(cls, n, l, j_n, i):
        shell = AtomicShellNotationParser.IUPAC_SHELLS[n - 1]
        s = html = latex = shell
        if n != 1: # No K1
            s += str(i)
            html += '<sub>{0:d}</sub>'.format(i)
            latex += '$_{{{0:d}}}$'.format(i)
        return s, s, html, latex

    @classmethod
    def _create_entry_orbital(cls, n, l, j_n, i):
        l_letter = cls.ORBITAL_L[l]
        s = '{0:d}{1}{2}/2'.format(n, l_letter, j_n)
        html = '{0:d}{1}<sub>{2}/2</sub>'.format(n, l_letter, j_n)
        latex = '{0:d}{1}$_{{{2}/2}}$'.format(n, l_letter, j_n)
        return s, s, html, latex

    def __iter__(self):
        for n, l, j_n, i in iter_subshells(MAX_N):
            self.update(int(n / MAX_N * 100.0))

            atomic_subshell = AtomicSubshell(n, l, j_n)

            ascii, utf16, html, latex = \
                self._create_entry_siegbahn(n, l, j_n, i)
            prop = AtomicSubshellNotation(base.UNATTRIBUTED,
                                          atomic_subshell,
                                          base.SIEGBAHN,
                                          ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            ascii, utf16, html, latex = \
                self._create_entry_iupac(n, l, j_n, i)
            prop = AtomicSubshellNotation(base.UNATTRIBUTED,
                                          atomic_subshell,
                                          base.IUPAC,
                                          ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            ascii, utf16, html, latex = \
                self._create_entry_orbital(n, l, j_n, i)
            prop = AtomicSubshellNotation(base.UNATTRIBUTED,
                                          atomic_subshell,
                                          base.ORBITAL,
                                          ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

class GenericXrayTransitionNotationParser(base._Parser):

    def __iter__(self):
        length = (MAX_N * MAX_N) ** 2
        progress = 0
        for transition, src_i, dst_i in iter_transitions(MAX_N):
            progress += 1
            self.update(int(progress / length * 100.0))

            src = transition.source_subshell
            dst = transition.destination_subshell

            ascii0, utf0, html0, latex0 = \
                AtomicSubshellNotationParser._create_entry_iupac(src.n, src.l, src.j_n, src_i)
            ascii1, utf1, html1, latex1 = \
                AtomicSubshellNotationParser._create_entry_iupac(dst.n, dst.l, dst.j_n, dst_i)

            ascii = '{0}-{1}'.format(ascii1, ascii0)
            utf = '{0}\u2013{1}'.format(utf1, utf0)
            html = '{0}&ndash;{1}'.format(html1, html0)
            latex = '{0}--{1}'.format(latex1, latex0)

            prop = XrayTransitionNotation(base.UNATTRIBUTED,
                                          transition,
                                          base.IUPAC,
                                          ascii, utf, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

class KnownXrayTransitionNotationParser(base._Parser):

    def __iter__(self):
        assert base.Ka1.source_subshell == base.L3
        assert base.Ka1.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Ka1, base.SIEGBAHN,
                                     'Ka1',
                                     'K\u03b11',
                                     'K&alpha;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{K}\\alpha_1}')

        assert base.Ka2.source_subshell == base.L2
        assert base.Ka2.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Ka2, base.SIEGBAHN,
                                     'Ka2',
                                     'K\u03b12',
                                     'K&alpha;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{K}\\alpha_2}')

        assert base.Ka.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Ka, base.SIEGBAHN,
                                     'Ka',
                                     'K\u03b1',
                                     'K&alpha;',
                                     '\\ensuremath{\\mathrm{K}\\alpha}')
        yield XrayTransitionNotation(JENKINS1991, base.Ka, base.IUPAC,
                                     'K-L(2,3)',
                                     'K\u2013L(2,3)',
                                     'K&ndash;L<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{K}}--\\ensuremath{\\mathrm{L}_{2,3}}')

        assert base.Kb1.source_subshell == base.M3
        assert base.Kb1.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb1, base.SIEGBAHN,
                                     'Kb1',
                                     'K\u03b21',
                                     'K&beta;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{K}\\beta_1}')

        assert base.Kb2_1.source_subshell == base.N3
        assert base.Kb2_1.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb2_1, base.SIEGBAHN,
                                     'Kb2I',
                                     'K\u03b22I',
                                     'K&beta;<sub>2</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_2^I}')

        assert base.Kb2_2.source_subshell == base.N2
        assert base.Kb2_2.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb2_2, base.SIEGBAHN,
                                     'Kb2II',
                                     'K\u03b22II',
                                     'K&beta;<sub>2</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_2^{II}}')

        assert base.Kb2.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb2, base.SIEGBAHN,
                                     'Kb2',
                                     'K\u03b22',
                                     'K&beta;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{K}\\beta_2}')

        assert base.Kb3.source_subshell == base.M2
        assert base.Kb3.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb3, base.SIEGBAHN,
                                     'Kb3',
                                     'K\u03b23',
                                     'K&beta;<sub>3</sub>',
                                    '\\ensuremath{\\mathrm{K}\\beta_3}')

        assert base.Kb1_3.destination_subshell == base.K
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Kb1_3, base.SIEGBAHN,
                                     'Kb1,3',
                                     'K\u03b21,3',
                                     'K&beta;<sup>1,3</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_{1,3}}')
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Kb1_3, base.IUPAC,
                                     'K-M(2,3)',
                                     'K\u2013M(2,3)',
                                     'K&ndash;M<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{K}}--\\ensuremath{\\mathrm{M}_{2,3}}')

        assert base.Kb4_1.source_subshell == base.N5
        assert base.Kb4_1.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb4_1, base.SIEGBAHN,
                                     'Kb4I',
                                     'K\u03b24II',
                                     'K&beta;<sub>4</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_4^I}')

        assert base.Kb4_2.source_subshell == base.N4
        assert base.Kb4_2.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb4_2, base.SIEGBAHN,
                                     'Kb4II',
                                     'K\u03b24II',
                                     'K&beta;<sub>4</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_4^{II}}')

        assert base.Kb4.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb4, base.SIEGBAHN,
                                     'Kb4',
                                     'K\u03b24',
                                     'K&beta;<sub>4</sub>',
                                     '\\ensuremath{\\mathrm{K}\\beta_4}')

        assert base.Kb5_1.source_subshell == base.M5
        assert base.Kb5_1.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb5_1, base.SIEGBAHN,
                                     'Kb5I',
                                     'K\u03b25I',
                                     'K&beta;<sub>5</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_5^I}')

        assert base.Kb5_2.source_subshell == base.M4
        assert base.Kb5_2.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb5_2, base.SIEGBAHN,
                                     'Kb5II',
                                     'K\u03b25II',
                                     'K&beta;<sub>5</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{K}\\beta_5^{II}}')

        assert base.Kb5.destination_subshell == base.K
        yield XrayTransitionNotation(JENKINS1991, base.Kb5, base.SIEGBAHN,
                                     'Kb5',
                                     'K\u03b25',
                                     'K&beta;<sub>5</sub>',
                                     '\\ensuremath{\\mathrm{K}\\beta_5}')
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Kb5, base.IUPAC,
                                     'K-M(4,5)',
                                     'K\u2013M(4,5)',
                                     'K&ndash;M<sub>4,5</sub>',
                                     '\\ensuremath{\\mathrm{K}}--\\ensuremath{\\mathrm{M}_{4,5}}')

        assert base.KO2_3.destination_subshell == base.K
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.KO2_3, base.IUPAC,
                                     'K-O(2,3)',
                                     'K\u2013O(2,3)',
                                     'K&ndash;O<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{K}}--\\ensuremath{\\mathrm{O}_{2,3}}')

        assert base.La1.source_subshell == base.M5
        assert base.La1.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.La1, base.SIEGBAHN,
                                     'La1',
                                     'L\u03b11',
                                     'L&alpha;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}\\alpha_1}')

        assert base.La2.source_subshell == base.M4
        assert base.La2.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.La2, base.SIEGBAHN,
                                     'La2',
                                     'L\u03b12',
                                     'L&alpha;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{L}\\alpha_2}')

        assert base.La.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.La, base.SIEGBAHN,
                                     'La',
                                     'L\u03b1',
                                     'L&alpha;',
                                     '\\ensuremath{\\mathrm{L}\\alpha}')
        yield XrayTransitionNotation(JENKINS1991, base.La, base.IUPAC,
                                     'L3-M(4,5)',
                                     'L3\u2013M(4,5)',
                                     'L<sub>3</sub>&ndash;M<sub>4,5</sub>',
                                     '\\ensuremath{\\mathrm{L}_3}--\\ensuremath{\\mathrm{M}_{4,5}}')

        assert base.Lb1.source_subshell == base.M4
        assert base.Lb1.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lb1, base.SIEGBAHN,
                                     'Lb1',
                                     'L\u03b21',
                                     'L&beta;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_1}')

        assert base.Lb2.source_subshell == base.N5
        assert base.Lb2.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Lb2, base.SIEGBAHN,
                                     'Lb2',
                                     'L\u03b22',
                                     'L&beta;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_2}')

        assert base.Lb3.source_subshell == base.M3
        assert base.Lb3.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lb3, base.SIEGBAHN,
                                     'Lb3',
                                     'L\u03b23',
                                     'L&beta;<sub>3</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_3}')

        assert base.Lb4.source_subshell == base.M2
        assert base.Lb4.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lb4, base.SIEGBAHN,
                                     'Lb4',
                                     'L\u03b24',
                                     'L&beta;<sub>4</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_4}')

        assert base.Lb3_4.destination_subshell == base.L1
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Lb3_4, base.SIEGBAHN,
                                     'Lb3,4',
                                     'L\u03b23,4',
                                     'L&beta;<sub>3,4</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{3,4}}')
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Lb3_4, base.IUPAC,
                                     'L1-M(2,3)',
                                     'L1\u2013M(2,3)',
                                     'L<sub>1</sub>&ndash;M<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{L}_1}--\\ensuremath{\\mathrm{M}_{2,3}}')

        assert base.Lb5_1.source_subshell == base.O5
        assert base.Lb5_1.destination_subshell == base.L3
        yield XrayTransitionNotation(BEARDEN1967, base.Lb5_1, base.SIEGBAHN,
                                     'Lb5I',
                                     'L\u03b25I',
                                     'L&beta;<sub>5</sub><sup>I</sup>',
                                     '\\ensuremath{\\mathrm{L}\\beta_5^I}')

        assert base.Lb5_2.source_subshell == base.O4
        assert base.Lb5_2.destination_subshell == base.L3
        yield XrayTransitionNotation(BEARDEN1967, base.Lb5_2, base.SIEGBAHN,
                                     'Lb5II',
                                     'L\u03b25II',
                                     'L&beta;<sub>5</sub><sup>II</sup>',
                                     '\\ensuremath{\\mathrm{L}\\beta_5^{II}}')

        assert base.Lb5.destination_subshell == base.L3
        yield XrayTransitionNotation(BEARDEN1967, base.Lb5, base.SIEGBAHN,
                                     'Lb5',
                                     'L\u03b25',
                                     'L&beta;<sub>5</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_5}')

        assert base.Lb6.source_subshell == base.N1
        assert base.Lb6.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Lb6, base.SIEGBAHN,
                                     'Lb6',
                                     'L\u03b26',
                                     'L&beta;<sub>6</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_6}')

        assert base.Lb7.source_subshell == base.O1
        assert base.Lb7.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Lb7, base.SIEGBAHN,
                                     'Lb7',
                                     'L\u03b27',
                                     'L&beta;<sub>7</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_7}')

        assert base.Lb9.source_subshell == base.M5
        assert base.Lb9.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lb9, base.SIEGBAHN,
                                     'Lb9',
                                     'L\u03b29',
                                     'L&beta;<sub>9</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_9}')

        assert base.Lb10.source_subshell == base.M4
        assert base.Lb10.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lb10, base.SIEGBAHN,
                                     'Lb10',
                                     'L\u03b210',
                                     'L&beta;<sub>10</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{10}}')

        assert base.Lb15.source_subshell == base.N4
        assert base.Lb15.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Lb15, base.SIEGBAHN,
                                     'Lb15',
                                     'L\u03b215',
                                     'L&beta;<sub>15</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{15}}')

        assert base.Lb2_15.destination_subshell == base.L3
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Lb2_15, base.SIEGBAHN,
                                     'Lb2,15',
                                     'L\u03b22,15',
                                     'L&beta;<sub>2,15</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{2,15}}')
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Lb2_15, base.IUPAC,
                                     'L3-N(4,5)',
                                     'L3\u2013N(4,5)',
                                     'L<sub>3</sub>&ndash;N<sub>4,5</sub>',
                                     '\\ensuremath{\\mathrm{L}_3}--\\ensuremath{\\mathrm{N}_{4,5}}')

        assert base.Lb17.source_subshell == base.M3
        assert base.Lb17.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lb17, base.SIEGBAHN,
                                     'Lb17',
                                     'L\u03b217',
                                     'L&beta;<sub>17</sub>',
                                     '\\ensuremath{\\mathrm{L}\\beta_{17}}')

        assert base.Lg1.source_subshell == base.N4
        assert base.Lg1.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lg1, base.SIEGBAHN,
                                     'Lg1',
                                     'L\u03b31',
                                     'L&gamma;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_1}')

        assert base.Lg2.source_subshell == base.N2
        assert base.Lg2.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lg2, base.SIEGBAHN,
                                     'Lg2',
                                     'L\u03b32',
                                     'L&gamma;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_2}')

        assert base.Lg3.source_subshell == base.N3
        assert base.Lg3.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lg3, base.SIEGBAHN,
                                     'Lg3',
                                     'L\u03b33',
                                     'L&gamma;<sub>3</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_3}')

        assert base.Lg2_3.destination_subshell == base.L1
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Lg2_3, base.SIEGBAHN,
                                     'Lg2,3',
                                     'L\u03b32,3',
                                     'L&gamma;<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_{2,3}}')
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Lg2_3, base.IUPAC,
                                     'L1-N(2,3)',
                                     'L1\u2013N(2,3)',
                                     'L<sub>1</sub>&ndash;N<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{L}_1}--\\ensuremath{\\mathrm{N}_{2,3}}')

        assert base.Lg4.source_subshell == base.O3
        assert base.Lg4.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lg4, base.SIEGBAHN,
                                     'Lg4',
                                     'L\u03b34',
                                     'L&gamma;<sub>4</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_4}')

        assert base.Lg4p.source_subshell == base.O2
        assert base.Lg4p.destination_subshell == base.L1
        yield XrayTransitionNotation(JENKINS1991, base.Lg4p, base.SIEGBAHN,
                                     "Lg4'",
                                     "L\u03b34\u2032",
                                     'L&gamma;<sub>4&prime;</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_{4\\prime}}')

        assert base.Lg5.source_subshell == base.N1
        assert base.Lg5.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lg5, base.SIEGBAHN,
                                     'Lg5',
                                     'L\u03b35',
                                     'L&gamma;<sub>5</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_5}')

        assert base.Lg6.source_subshell == base.O4
        assert base.Lg6.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lg6, base.SIEGBAHN,
                                     'Lg6',
                                     'L\u03b36',
                                     'L&gamma;<sub>6</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_6}')

        assert base.Lg8.source_subshell == base.O1
        assert base.Lg8.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lg8, base.SIEGBAHN,
                                     'Lg8',
                                     'L\u03b38',
                                     'L&gamma;<sub>8</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_8}')

        assert base.Lg11.source_subshell == base.N5
        assert base.Lg11.destination_subshell == base.L1
        yield XrayTransitionNotation(BEARDEN1967, base.Lg11, base.SIEGBAHN,
                                     'Lg11',
                                     'L\u03b311',
                                     'L&gamma;<sub>11</sub>',
                                     '\\ensuremath{\\mathrm{L}\\gamma_11}')

        assert base.Ln.source_subshell == base.M1
        assert base.Ln.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Ln, base.SIEGBAHN,
                                     'Ln',
                                     'L\u03b7',
                                     'L&eta;',
                                     '\\ensuremath{\\mathrm{L}\\eta}')

        assert base.Ll.source_subshell == base.M1
        assert base.Ll.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Ll, base.SIEGBAHN,
                                     'Ll',
                                     'L\u2113',
                                     'L&#x2113;',
                                     '\\ensuremath{\\mathrm{L}\\ell}')

        assert base.Ll_n.source_subshell == base.M1
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Ll_n, base.SIEGBAHN,
                                     'Ll,n',
                                     'L\u2113,\u03b7',
                                     'L&#x2113;,&eta;',
                                     '\\ensuremath{\\mathrm{L}\\ell,\\eta}')
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.Ll_n, base.IUPAC,
                                     'L(2,3)-M1',
                                     'L(2,3)\u2013M1',
                                     'L<sup>2,3</sup>&ndash;M<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{L}_{2,3}}--\\ensuremath{\\mathrm{M}_1}')

        assert base.Ls.source_subshell == base.M3
        assert base.Ls.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Ls, base.SIEGBAHN,
                                     'Ls',
                                     'Ls',
                                     'Ls',
                                     '\\ensuremath{\\mathrm{L}s}')

        assert base.Lt.source_subshell == base.M2
        assert base.Lt.destination_subshell == base.L3
        yield XrayTransitionNotation(JENKINS1991, base.Lt, base.SIEGBAHN,
                                     'Lt',
                                     'Lt',
                                     'Lt',
                                     '\\ensuremath{\\mathrm{L}t}')

        assert base.Lu_1.source_subshell == base.N7
        assert base.Lu_1.destination_subshell == base.L3
        yield XrayTransitionNotation(BEARDEN1967, base.Lu_1, base.SIEGBAHN,
                                     'LuI',
                                     'LuI',
                                     'Lu<sup>I</sup>',
                                     '\\ensuremath{\\mathrm{L}u^I}')

        assert base.Lu_2.source_subshell == base.N6
        assert base.Lu_2.destination_subshell == base.L3
        yield XrayTransitionNotation(BEARDEN1967, base.Lu_2, base.SIEGBAHN,
                                     'LuII',
                                     'LuII',
                                     'Lu<sup>II</sup>',
                                     '\\ensuremath{\\mathrm{L}u^{II}}')

        assert base.Lu.destination_subshell == base.L3
        yield XrayTransitionNotation(BEARDEN1967, base.Lu, base.SIEGBAHN,
                                     'Lu',
                                     'Lu',
                                     'Lu',
                                     '\\ensuremath{\\mathrm{L}u}')

        assert base.Lv.source_subshell == base.N6
        assert base.Lv.destination_subshell == base.L2
        yield XrayTransitionNotation(JENKINS1991, base.Lv, base.SIEGBAHN,
                                     'Lv',
                                     'L\u03bd',
                                     'L&nu;',
                                     '\\ensuremath{\\mathrm{L}\\nu}')

        assert base.Ma1.source_subshell == base.N7
        assert base.Ma1.destination_subshell == base.M5
        yield XrayTransitionNotation(JENKINS1991, base.Ma1, base.SIEGBAHN,
                                     'Ma1',
                                     'M\u03b11',
                                     'M&alpha;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{M}\\alpha_1}')

        assert base.Ma2.source_subshell == base.N6
        assert base.Ma2.destination_subshell == base.M5
        yield XrayTransitionNotation(JENKINS1991, base.Ma2, base.SIEGBAHN,
                                     'Ma2',
                                     'M\u03b12',
                                     'M&alpha;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{M}\\alpha_2}')

        assert base.Ma.destination_subshell == base.M5
        yield XrayTransitionNotation(JENKINS1991, base.Ma, base.SIEGBAHN,
                                     'Ma',
                                     'M\u03b1',
                                     'M&alpha;',
                                     '\\ensuremath{\\mathrm{M}\\alpha}')
        yield XrayTransitionNotation(JENKINS1991, base.Ma, base.IUPAC,
                                     'M5-N(6,7)',
                                     'M5\u2013N(6,7)',
                                     'M<sub>5</sub>&ndash;N<sub>6,7</sub>',
                                     '\\ensuremath{\\mathrm{M}_5}--\\ensuremath{\\mathrm{N}_{6,7}}')

        assert base.Mb.source_subshell == base.N6
        assert base.Mb.destination_subshell == base.M4
        yield XrayTransitionNotation(JENKINS1991, base.Mb, base.SIEGBAHN,
                                     'Mb',
                                     'M\u03b2',
                                     'M&beta;',
                                     '\\ensuremath{\\mathrm{M}\\beta}')

        assert base.Mg.source_subshell == base.N5
        assert base.Mg.destination_subshell == base.M3
        yield XrayTransitionNotation(JENKINS1991, base.Mg, base.SIEGBAHN,
                                     'Mg',
                                     'M\u03b3',
                                     'M&gamma;',
                                     '\\ensuremath{\\mathrm{M}\\gamma}')

        assert base.Mz1.source_subshell == base.N3
        assert base.Mz1.destination_subshell == base.M5
        yield XrayTransitionNotation(BEARDEN1967, base.Mz1, base.SIEGBAHN,
                                     'Mz1',
                                     'M\u03b61',
                                     'M&zeta;<sub>1</sub>',
                                     '\\ensuremath{\\mathrm{M}\\zeta_1}')

        assert base.Mz2.source_subshell == base.N2
        assert base.Mz2.destination_subshell == base.M4
        yield XrayTransitionNotation(BEARDEN1967, base.Mz2, base.SIEGBAHN,
                                     'Mz2',
                                     'M\u03b62',
                                     'M&zeta;<sub>2</sub>',
                                     '\\ensuremath{\\mathrm{M}\\zeta_2}')

        yield XrayTransitionNotation(BEARDEN1967, base.Mz, base.SIEGBAHN,
                                     'Mz',
                                     'M\u03b6',
                                     'M&zeta;',
                                     '\\ensuremath{\\mathrm{M}\\zeta}')
        yield XrayTransitionNotation(BEARDEN1967, base.Mz, base.IUPAC,
                                     'M(4,5)-N(2,3)',
                                     'M(4,5)\u2013N(2,3)',
                                     'M<sub>4,5</sub>&ndash;N<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{M}_{4,5}}--\\ensuremath{\\mathrm{N}_{2,3}}')

        assert base.M1N2_3.destination_subshell == base.M1
        yield XrayTransitionNotation(base.UNATTRIBUTED, base.M1N2_3, base.IUPAC,
                                     'M1-N(2,3)',
                                     'M1\u2013N(2,3)',
                                     'M<sub>1</sub>&ndash;N<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{M}_1}--\\ensuremath{\\mathrm{N}_{2,3}}')

        yield XrayTransitionNotation(base.UNATTRIBUTED, base.M2_3M4_5, base.IUPAC,
                                     'M(2,3)-M(4,5)',
                                     'M(2,3)\u2013M(4,5)',
                                     'M<sub>2,3</sub>&ndash;M<sub>4,5</sub>',
                                     '\\ensuremath{\\mathrm{M}_{2,3}}--\\ensuremath{\\mathrm{M}_{4,5}}')

        yield XrayTransitionNotation(base.UNATTRIBUTED, base.M4_5O2_3, base.IUPAC,
                                     'M(4,5)-O(2,3)',
                                     'M(4,5)\u2013O(2,3)',
                                     'M<sub>4,5</sub>&ndash;O<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{M}_{4,5}}--\\ensuremath{\\mathrm{O}_{2,3}}')

        yield XrayTransitionNotation(base.UNATTRIBUTED, base.M3O4_5, base.IUPAC,
                                     'M3-O(4,5)',
                                     'M3\u2013O(4,5)',
                                     'M<sub>3</sub>&ndash;O<sub>4,5</sub>',
                                     '\\ensuremath{\\mathrm{M}_3}--\\ensuremath{\\mathrm{O}_{4,5}}')

        yield XrayTransitionNotation(base.UNATTRIBUTED, base.M4O2_3, base.IUPAC,
                                     'M4-O(2,3)',
                                     'M4\u2013O(2,3)',
                                     'M<sub>4</sub>&ndash;O<sub>2,3</sub>',
                                     '\\ensuremath{\\mathrm{M}_4}--\\ensuremath{\\mathrm{O}_{2,3}}')

class SeriesXrayTransitionNotationParser(base._Parser):

    def __iter__(self):
        for n in range(1, MAX_N + 1):
            transition = XrayTransition(None, None, None, n, None, None) # All transitions to this shell

            ascii, utf16, html, latex = AtomicShellNotationParser._create_entry_siegbahn(n)
            yield XrayTransitionNotation(base.UNATTRIBUTED, transition, base.SIEGBAHN,
                                         ascii, utf16, html, latex)

            ascii, utf16, html, latex = AtomicShellNotationParser._create_entry_iupac(n)
            yield XrayTransitionNotation(base.UNATTRIBUTED, transition, base.IUPAC,
                                         ascii, utf16, html, latex)

class FamilyXrayTransitionNotationParser(base._Parser):

    def __iter__(self):
        families = set()
        for transition, _src_i, dst_i in iter_transitions(MAX_N):
            dst = transition.destination_subshell
            families.add((dst, dst_i))

        # Create family notations
        for atomic_subshell, i in families:
            if i == 0: # Skip K, already a series
                continue

            n = atomic_subshell.n
            l = atomic_subshell.l
            j_n = atomic_subshell.j_n

            transition = XrayTransition(None, None, None, n, l, j_n) # All transitions to this subshell

            ascii, utf16, html, latex = AtomicSubshellNotationParser._create_entry_siegbahn(n, l, j_n, i)
            yield XrayTransitionNotation(base.UNATTRIBUTED, transition, base.SIEGBAHN,
                                         ascii, utf16, html, latex)

            ascii, utf16, html, latex = AtomicSubshellNotationParser._create_entry_iupac(n, l, j_n, i)
            yield XrayTransitionNotation(base.UNATTRIBUTED, transition, base.IUPAC,
                                         ascii, utf16, html, latex)
