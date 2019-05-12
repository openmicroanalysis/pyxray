# Standard library modules.
import collections.abc
import inspect

# Third party modules.
import pkg_resources

# Local modules.
from pyxray.cbook import ProgressReportMixin
from pyxray.descriptor import AtomicSubshell, XrayTransition, Notation, Reference

# Globals and constants variables.
ENTRY_POINT = 'pyxray.parser'

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
P1 = AtomicSubshell(6, 0, 1)
P2 = AtomicSubshell(6, 1, 1)
P3 = AtomicSubshell(6, 1, 3)
P4 = AtomicSubshell(6, 2, 3)
P5 = AtomicSubshell(6, 2, 5)
P6 = AtomicSubshell(6, 3, 5)
P7 = AtomicSubshell(6, 3, 7)
P8 = AtomicSubshell(6, 4, 7)
P9 = AtomicSubshell(6, 4, 9)
P10 = AtomicSubshell(6, 5, 9)
P11 = AtomicSubshell(6, 5, 11)
Q1 = AtomicSubshell(7, 0, 1)
Q2 = AtomicSubshell(7, 1, 1)
Q3 = AtomicSubshell(7, 1, 3)

Ka1 =  XrayTransition(L3, K)
Ka2 = XrayTransition(L2, K)
Ka = XrayTransition(2, 1, None, K)
Kb1 = XrayTransition(M3, K)
Kb2_1 = XrayTransition(N3, K)
Kb2_2 = XrayTransition(N2, K)
Kb2 = XrayTransition(4, 1, None, K)
Kb3 = XrayTransition(M2, K)
Kb1_3 = XrayTransition(3, 1, None, K) # K-M2,3
Kb4_1 = XrayTransition(N5, K)
Kb4_2 = XrayTransition(N4, K)
Kb4 = XrayTransition(4, 2, None, K)
Kb5_1 = XrayTransition(M5, K)
Kb5_2 = XrayTransition(M4, K)
Kb5 = XrayTransition(3, 2, None, K) # K-M4,5
KO2_3 = XrayTransition(5, 1, None, K) # K-O2,3

La1 = XrayTransition(M5, L3)
La2 = XrayTransition(M4, L3)
La = XrayTransition(3, 2, None, L3)
Lb1 = XrayTransition(M4, L2)
Lb2 = XrayTransition(N5, L3)
Lb3 = XrayTransition(M3, L1)
Lb4 = XrayTransition(M2, L1)
Lb3_4 = XrayTransition(3, 1, None, L1) # L1-M2,3
Lb5_1 = XrayTransition(O5, L3)
Lb5_2 = XrayTransition(O4, L3)
Lb5 = XrayTransition(5, 2, None, L3) # L3-O4,5
Lb6 = XrayTransition(N1, L3)
Lb7 = XrayTransition(O1, L3)
Lb9 = XrayTransition(M5, L1)
Lb10 = XrayTransition(M4, L1)
Lb15 = XrayTransition(N4, L3)
Lb2_15 = XrayTransition(4, 2, None, L3) # L3-N4,5
Lb17 = XrayTransition(M3, L2)
Leta = XrayTransition(M1, L2)
Lg1 = XrayTransition(N4, L2)
Lg2 = XrayTransition(N2, L1)
Lg3 = XrayTransition(N3, L1)
Lg2_3 = XrayTransition(4, 1, None, L1) # L1-N2,3
Lg4 = XrayTransition(O3, L1)
Lg4p = XrayTransition(O2, L1)
Lg5 = XrayTransition(N1, L2)
Lg6 = XrayTransition(O4, L2)
Lg8 = XrayTransition(O1, L2)

Lg11 = XrayTransition (N5, L1)
Ln = XrayTransition(M1, L2)
Ll = XrayTransition(M1, L3)
Ll_n = XrayTransition(M1, 2, 1, None) # L2,3-M1
Ls = XrayTransition(M3, L3)
Lt = XrayTransition(M2, L3)
Lv = XrayTransition(N6, L2)
Lu_1 = XrayTransition(N7, L3)
Lu_2 = XrayTransition(N6, L3)
Lu = XrayTransition(4, 3, None, L3)

Ma1 = XrayTransition(N7, M5)
Ma2 = XrayTransition(N6, M5)
Ma = XrayTransition(4, 3, None, M5)
Mb = XrayTransition(N6, M4)
Mg = XrayTransition(N5, M3)
Mz1 = XrayTransition(N3, M5)
Mz2 = XrayTransition(N2, M4)
Mz = XrayTransition(4, 1, None, 3, 2, None)
M1N2_3 = XrayTransition(4, 1, None, M1) # M1-N2,3
M2_3M4_5 = XrayTransition(3, 2, None, 3, 1, None) # M2,3-M4,5
M4_5O2_3 = XrayTransition(5, 1, None, 3, 2, None) # M4,5-O2,3
M3O4_5 = XrayTransition(5, 2, None, M3) # M3-O4,5
M4O2_3 = XrayTransition(5, 1, None, M4) # M4-O2,3

SIEGBAHN = Notation('siegbahn')
IUPAC = Notation('iupac')
ORBITAL = Notation('orbital')

UNATTRIBUTED = Reference('unattributed')

class _Parser(collections.abc.Iterable, ProgressReportMixin):
    """
    (abstract) Class to parse X-ray related information from a data source.

    A parser is simply an iterable object which returns a new property at each
    iteration. For example::

    class ElementSymbolParser(_Parser):

        def __iter__(self):
            yield ElementSymbol(...)

    Each parser should be registered in the setup.py under the entry point:
    `pyxray.parser`
    """
    pass

def find_parsers():
    parsers = []
    for entry_point in pkg_resources.iter_entry_points(ENTRY_POINT):
        name = entry_point.name
        parser = entry_point.load()
        if inspect.isclass(parser):
            parser = parser()
        parsers.append((name, parser))
    return parsers
