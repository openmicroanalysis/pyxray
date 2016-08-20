""""""

# Standard library modules.
import itertools

# Third party modules.

# Local modules.
from pyxray.meta.parser import _CachedParser
from pyxray.meta.reference import UNATTRIBUTED, Reference

# Globals and constants variables.
MAX_N = 7

class _BaseParser(_CachedParser):

    def __init__(self, usecache=True):
        super().__init__(UNATTRIBUTED, usecache)

#--- Mix-ins

class _NotationParserMixin(object):

    KEY_NOTATION = 'notation'
    KEY_VALUE = 'value'
    KEY_VALUE_HTML = 'html'
    KEY_VALUE_LATEX = 'latex'

class _AtomicShellParserMixin(object):

    KEY_N = 'n'

class _AtomicSubshellParserMixin(object):

    KEY_N = 'n'
    KEY_L = 'l'
    KEY_Jn = 'jn'

class _TransitionParserMixin(object):

    KEY_SOURCE_N = 'n0'
    KEY_SOURCE_L = 'l0'
    KEY_SOURCE_Jn = 'j0_n'
    KEY_DESTINATION_N = 'n1'
    KEY_DESTINATION_L = 'l1'
    KEY_DESTINATION_Jn = 'j1_n'
    KEY_SECONDARY_DESTINATION_N = 'n2'
    KEY_SECONDARY_DESTINATION_L = 'l2'
    KEY_SECONDARY_DESTINATION_Jn = 'j2_n'

#--- Parsers

class NotationTypeParser(_BaseParser):

    KEY_NAME = 'name'
    KEY_REFERENCE = 'reference'

    REFERENCES = \
        {'siegbahn': Reference('siegbahn1925',
                               author='Siegbahn, M.',
                               publisher='Oxford University Press',
                               title='The spectroscopy of X-rays',
                               year='1925'),
         'iupac': Reference('jenkins1991',
                            author='Jenkins, R. and Manne, R. and Robin, R. and Senemaud, C.',
                            year='1991',
                            pages='149--155',
                            journal='X-Ray Spectrometry',
                            title='{IUPAC} --- nomenclature system for x-ray spectroscopy',
                            volume='20',
                            doi='10.1002/xrs.1300200308'),
         'orbital': UNATTRIBUTED,
         }

    def parse_nocache(self):
        entries = []
        for name, reference in self.REFERENCES.items():
            entries.append({self.KEY_NAME: name,
                            self.KEY_REFERENCE: reference.todict()})
        return entries

    def keys(self):
        return set([self.KEY_NAME, self.KEY_REFERENCE])

class ElementParser(_BaseParser):

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

    KEY_Z = 'z'
    KEY_SYMBOL = 'symbol'

    def parse_nocache(self):
        entries = []
        for z, symbol in enumerate(self.SYMBOLS, 1):
            entries.append({self.KEY_Z: z, self.KEY_SYMBOL: symbol})
        return entries

    def keys(self):
        return set([self.KEY_Z, self.KEY_SYMBOL])

class AtomicShellParser(_AtomicShellParserMixin,
                        _BaseParser):

    def parse_nocache(self):
        entries = []
        for n in range(1, MAX_N + 1):
            entries.append({self.KEY_N: n})
        return entries

    def keys(self):
        return set([self.KEY_N])

class AtomicShellNotationParser(_NotationParserMixin,
                                _AtomicShellParserMixin,
                                _BaseParser):

    NOTATIONS = {'siegbahn': ['K', 'L', 'M', 'N', 'O', 'P', 'Q'],
                 'iupac': ['K', 'L', 'M', 'N', 'O', 'P', 'Q'],
                 'orbital': ['1', '2', '3', '4', '5', '6', '7']}

    def parse_nocache(self):
        entries = []
        for notation, values in self.NOTATIONS.items():
            for n, value in enumerate(values, 1):
                entries.append({self.KEY_N: n,
                                self.KEY_NOTATION: notation,
                                self.KEY_VALUE: value,
                                self.KEY_VALUE_HTML: value,
                                self.KEY_VALUE_LATEX: value})
        return entries

    def keys(self):
        return set([self.KEY_N, self.KEY_NOTATION, self.KEY_VALUE,
                    self.KEY_VALUE_HTML, self.KEY_VALUE_LATEX])

def iter_subshells(max_n):
    for n in range(1, max_n + 1):
        for l in range(0, n):
            for j in set([abs(l + 0.5), abs(l - 0.5)]):
                j_n = int(j * 2)
                yield n, l, j_n

class AtomicSubshellParser(_AtomicSubshellParserMixin,
                           _BaseParser):

    def parse_nocache(self):
        entries = []
        for n, l, j_n in iter_subshells(MAX_N):
            entries.append({self.KEY_N: n,
                            self.KEY_L: l,
                            self.KEY_Jn: j_n})
        return entries

    def keys(self):
        return set([self.KEY_N, self.KEY_L, self.KEY_Jn])

class AtomicSubshellNotationParser(_AtomicSubshellParserMixin,
                                   _NotationParserMixin,
                                   _BaseParser):

    SHELLS = AtomicShellNotationParser.NOTATIONS
    SIEGBAHN_NUMBERS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII',
                        'IX', 'X', 'XI', 'XII', 'XIII']
    ORBITAL_L = ['s', 'p', 'd', 'f', 'g', 'h', 'i']

    def _create_entry_siegbahn(self, n, l, j_n, i):
        shell = self.SHELLS['siegbahn'][n - 1]
        value = shell
        if i > 1:
            value += self.SIEGBAHN_NUMBERS[i - 1]
        value_html = value_latex = value
        return {self.KEY_N: n,
                self.KEY_L: l,
                self.KEY_Jn: j_n,
                self.KEY_NOTATION: 'siegbahn',
                self.KEY_VALUE: value,
                self.KEY_VALUE_HTML: value_html,
                self.KEY_VALUE_LATEX: value_latex}

    def _create_entry_iupac(self, n, l, j_n, i):
        shell = self.SHELLS['iupac'][n - 1]
        value = value_html = value_latex = shell
        if i > 1:
            value += str(i)
            value_html += '<sub>{0:d}</sub>'.format(i)
            value_latex += '$_{{{0:d}}}$'.format(i)

        return {self.KEY_N: n,
                self.KEY_L: l,
                self.KEY_Jn: j_n,
                self.KEY_NOTATION: 'iupac',
                self.KEY_VALUE: value,
                self.KEY_VALUE_HTML: value_html,
                self.KEY_VALUE_LATEX: value_latex}

    def _create_entry_orbital(self, n, l, j_n, i):
        l_letter = self.ORBITAL_L[l]
        value = '{0:d}{1}{2}/2'.format(n, l_letter, j_n)
        value_html = '{0:d}{1}<sub>{2}/2</sub>'.format(n, l_letter, j_n)
        value_latex = '{0:d}{1}$_{{{2}/2}}$'.format(n, l_letter, j_n)

        return {self.KEY_N: n,
                self.KEY_L: l,
                self.KEY_Jn: j_n,
                self.KEY_NOTATION: 'orbital',
                self.KEY_VALUE: value,
                self.KEY_VALUE_HTML: value_html,
                self.KEY_VALUE_LATEX: value_latex}

    def parse_nocache(self):
        entries = []
        nprev = 0
        for n, l, j_n in iter_subshells(MAX_N):
            if nprev != n:
                i = 1

            entries.append(self._create_entry_siegbahn(n, l, j_n, i))
            entries.append(self._create_entry_iupac(n, l, j_n, i))
            entries.append(self._create_entry_orbital(n, l, j_n, i))

            i += 1
            nprev = n

        return entries

    def keys(self):
        return set([self.KEY_N, self.KEY_L, self.KEY_Jn,
                    self.KEY_NOTATION, self.KEY_VALUE,
                    self.KEY_VALUE_HTML, self.KEY_VALUE_LATEX])

class TransitionParser(_TransitionParserMixin,
                       _BaseParser):

    def _should_exist(self, n0, l0, j0_n, n1, l1, j1_n):
        """
        Inspired from NIST EPQ library by Nicholas Ritchie.
        """
        def electric_dipole_permitted(n0, l0, j0_n, n1, l1, j1_n):
            delta_j_n = abs(j1_n - j0_n)
            if delta_j_n > 2:
                return False
            assert delta_j_n == 0 or delta_j_n == 2
            return abs(l1 - l0) == 1

        def electric_quadrupole_permitted(n0, l0, j0_n, n1, l1, j1_n):
            delta_j_n = abs(j1_n - j0_n)
            if delta_j_n > 4:
                return False
            assert delta_j_n == 0 or delta_j_n == 2 or delta_j_n == 4

            delta_l = abs(l1 - l0)
            return delta_l == 0 or delta_l == 2

        if n0 == n1:
            return False

        return electric_dipole_permitted(n0, l0, j0_n, n1, l1, j1_n) or \
                electric_quadrupole_permitted(n0, l0, j0_n, n1, l1, j1_n)

    def parse_nocache(self):
        entries = []
        for (n0, l0, j0_n), (n1, l1, j1_n) in \
                itertools.product(iter_subshells(MAX_N), repeat=2):
            should_exist = self._should_exist(n0, l0, j0_n, n1, l1, j1_n)
            if not should_exist:
                continue
            entries.append({self.KEY_SOURCE_N: n0,
                            self.KEY_SOURCE_L: l0,
                            self.KEY_SOURCE_Jn: j0_n,
                            self.KEY_DESTINATION_N: n1,
                            self.KEY_DESTINATION_L: l1,
                            self.KEY_DESTINATION_Jn: j1_n})
        return entries

    def keys(self):
        return set([self.KEY_SOURCE_N])
