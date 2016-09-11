"""
Parsers from unattributed references.
"""

# Standard library modules.
import logging
logger = logging.getLogger(__name__)

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Element, AtomicShell, Notation, AtomicSubshell
from pyxray.property import ElementSymbol, AtomicShellNotation, AtomicSubshellNotation

# Globals and constants variables.

UNATTRIBUTED = Reference('unattributed')

MAX_N = 7

def iter_subshells(max_n):
    for n in range(1, max_n + 1):
        for l in range(0, n):
            for j in set([abs(l + 0.5), abs(l - 0.5)]):
                j_n = int(j * 2)
                yield n, l, j_n

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

    def _create_entry_siegbahn(self, n, l, j_n, i):
        shell = self.SHELLS['siegbahn'][n - 1]
        s = shell
        if i > 1:
            s += self.SIEGBAHN_NUMBERS[i - 1]
        return s, s, s, s

    def _create_entry_iupac(self, n, l, j_n, i):
        shell = self.SHELLS['iupac'][n - 1]
        s = html = latex = shell
        if i > 1:
            s += str(i)
            html += '<sub>{0:d}</sub>'.format(i)
            latex += '$_{{{0:d}}}$'.format(i)
        return s, s, html, latex

    def _create_entry_orbital(self, n, l, j_n, i):
        l_letter = self.ORBITAL_L[l]
        s = '{0:d}{1}{2}/2'.format(n, l_letter, j_n)
        html = '{0:d}{1}<sub>{2}/2</sub>'.format(n, l_letter, j_n)
        latex = '{0:d}{1}$_{{{2}/2}}$'.format(n, l_letter, j_n)
        return s, s, html, latex

    def __iter__(self):
        length = MAX_N
        progress = 0
        nprev = 0
        for n, l, j_n in iter_subshells(MAX_N):
            if nprev != n:
                i = 1
                self.update(int(progress / length * 100.0))
                progress += 1

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

            i += 1
            nprev = n


