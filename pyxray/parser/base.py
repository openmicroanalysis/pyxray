""""""

# Standard library modules.

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

class AtomicSubshellParser(_AtomicSubshellParserMixin,
                           _BaseParser):

    def parse_nocache(self):
        entries = []
        for n in range(1, MAX_N + 1):
            for l in range(0, n):
                for j in set([abs(l + 0.5), abs(l - 0.5)]):
                    j_n = int(j * 2)
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

    def parse_nocache(self):
        entries = []
        for n in range(1, MAX_N + 1):
            i = 1
            for l in range(0, n):
                for j in set([abs(l + 0.5), abs(l - 0.5)]):
                    j_n = int(j * 2)

                    # Siegbahn
                    shell = self.SHELLS['siegbahn'][n - 1]
                    value = shell
                    if i > 1:
                        value += self.SIEGBAHN_NUMBERS[i - 1]
                    value_html = value_latex = value

                    entries.append({self.KEY_N: n,
                                    self.KEY_L: l,
                                    self.KEY_Jn: j_n,
                                    self.KEY_NOTATION: 'siegbahn',
                                    self.KEY_VALUE: value,
                                    self.KEY_VALUE_HTML: value_html,
                                    self.KEY_VALUE_LATEX: value_latex})

                    # IUPAC
                    shell = self.SHELLS['iupac'][n - 1]
                    value = value_html = value_latex = shell
                    if i > 1:
                        value += str(i)
                        value_html += '<sub>{0:d}</sub>'.format(i)
                        value_latex += '$_{{{0:d}}}$'.format(i)

                    entries.append({self.KEY_N: n,
                                    self.KEY_L: l,
                                    self.KEY_Jn: j_n,
                                    self.KEY_NOTATION: 'iupac',
                                    self.KEY_VALUE: value,
                                    self.KEY_VALUE_HTML: value_html,
                                    self.KEY_VALUE_LATEX: value_latex})

                    # Orbital
                    l_letter = self.ORBITAL_L[l]
                    value = '{0:d}{1}{2}/2'.format(n, l_letter, j_n)
                    value_html = '{0:d}{1}<sub>{2}/2</sub>'.format(n, l_letter, j_n)
                    value_latex = '{0:d}{1}$_{{{2}/2}}$'.format(n, l_letter, j_n)

                    entries.append({self.KEY_N: n,
                                    self.KEY_L: l,
                                    self.KEY_Jn: j_n,
                                    self.KEY_NOTATION: 'orbital',
                                    self.KEY_VALUE: value,
                                    self.KEY_VALUE_HTML: value_html,
                                    self.KEY_VALUE_LATEX: value_latex})

                    i += 1

        return entries

    def keys(self):
        return set([self.KEY_N, self.KEY_L, self.KEY_Jn,
                    self.KEY_NOTATION, self.KEY_VALUE,
                    self.KEY_VALUE_HTML, self.KEY_VALUE_LATEX])

class TransitionParser(_TransitionParserMixin,
                       _BaseParser):

    pass