"""
Parsers from unattributed references.
"""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import \
    Reference, Element, AtomicShell, Notation, AtomicSubshell, Transition
from pyxray.property import \
    ElementSymbol, AtomicShellNotation, AtomicSubshellNotation, TransitionNotation

# Globals and constants variables.

UNATTRIBUTED = Reference('unattributed')

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

class ElementSymbolPropertyParser(_Parser):

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
            prop = ElementSymbol(UNATTRIBUTED, Element(z), symbol)
            logger.debug('Parsed: {0}'.format(prop))
            self.update(int((z - 1) / length * 100.0))
            yield prop

class AtomicShellNotationParser(_Parser):

    NOTATIONS = {'siegbahn': ['K', 'L', 'M', 'N', 'O', 'P', 'Q'],
                 'iupac': ['K', 'L', 'M', 'N', 'O', 'P', 'Q'],
                 'orbital': ['1', '2', '3', '4', '5', '6', '7']}

    def __iter__(self):
        length = len(self.NOTATIONS) * MAX_N
        progress = 0
        for notation_name, values in self.NOTATIONS.items():
            notation = Notation(notation_name)
            for n, value in enumerate(values, 1):
                atomic_shell = AtomicShell(n)
                prop = AtomicShellNotation(UNATTRIBUTED, atomic_shell, notation,
                                           value, value, value, value)
                logger.debug('Parsed: {0}'.format(prop))
                self.update(int(progress / length * 100.0))
                progress += 1
                yield prop

class AtomicSubshellNotationParser(_Parser):

    SHELLS = AtomicShellNotationParser.NOTATIONS
    SIEGBAHN_NUMBERS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII',
                        'IX', 'X', 'XI', 'XII', 'XIII']
    ORBITAL_L = ['s', 'p', 'd', 'f', 'g', 'h', 'i']

    @classmethod
    def _create_entry_siegbahn(cls, n, l, j_n, i):
        shell = cls.SHELLS['siegbahn'][n - 1]
        s = shell
        if n != 1: # No KI
            s += cls.SIEGBAHN_NUMBERS[i - 1]
        return s, s, s, s

    @classmethod
    def _create_entry_iupac(cls, n, l, j_n, i):
        shell = cls.SHELLS['iupac'][n - 1]
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
            prop = AtomicSubshellNotation(UNATTRIBUTED,
                                          atomic_subshell,
                                          Notation('siegbahn'),
                                          ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            ascii, utf16, html, latex = \
                self._create_entry_iupac(n, l, j_n, i)
            prop = AtomicSubshellNotation(UNATTRIBUTED,
                                          atomic_subshell,
                                          Notation('iupac'),
                                          ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            ascii, utf16, html, latex = \
                self._create_entry_orbital(n, l, j_n, i)
            prop = AtomicSubshellNotation(UNATTRIBUTED,
                                          atomic_subshell,
                                          Notation('orbital'),
                                          ascii, utf16, html, latex)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

class TransitionNotationParser(_Parser):

    def __iter__(self):
        length = (MAX_N * MAX_N) ** 2
        progress = 0
        for n0, l0, j0_n, i0 in iter_subshells(MAX_N):
            src = AtomicSubshell(n0, l0, j0_n)
            ascii0, utf0, html0, latex0 = \
                AtomicSubshellNotationParser._create_entry_iupac(n0, l0, j0_n, i0)

            for n1, l1, j1_n, i1 in iter_subshells(MAX_N):
                progress += 1
                self.update(int(progress / length * 100.0))

                # Cannot transition to itself
                if n0 == n1 and l0 == l1 and j0_n == j1_n:
                    continue

                # Transition must be from more to less energytic shell or
                # within the same shell
                if n0 < n1:
                    continue

                # Coster-Kroning transition must be from more to less energetic subshells
                if n0 == n1 and i0 <= i1:
                    continue

                dest = AtomicSubshell(n1, l1, j1_n)
                transition = Transition(src, dest)

                ascii1, utf1, html1, latex1 = \
                    AtomicSubshellNotationParser._create_entry_iupac(n1, l1, j1_n, i1)

                ascii = '{0}-{1}'.format(ascii1, ascii0)
                utf = '{0}\u2013{1}'.format(utf1, utf0)
                html = '{0}&ndash;{1}'.format(html1, html0)
                latex = '{0}--{1}'.format(latex1, latex0)

                prop = TransitionNotation(UNATTRIBUTED,
                                          transition,
                                          Notation('iupac'),
                                          ascii, utf, html, latex)
                logger.debug('Parsed: {0}'.format(prop))
                yield prop

