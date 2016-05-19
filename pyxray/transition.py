"""
Atomic transition
"""

# Standard library modules.
import sys
from abc import ABCMeta, abstractmethod
from operator import methodcaller, attrgetter
import string
from functools import total_ordering
from collections import Set

# Third party modules.
from pyparsing import Word, Group, Optional, OneOrMore, QuotedString, Literal

# Local modules.
import pyxray.element_properties as ep
from pyxray.subshell import Subshell
import pyxray.transition_data as transition_data
from pyxray.util import energy_to_wavelength_m

# Globals and constants variables.
_ZGETTER = attrgetter('z')

_level_pattern = Optional(QuotedString("(", endQuoteChar=")") | Word(string.digits))
_shell_pattern = Group(Word(string.ascii_uppercase) + _level_pattern)
_iupac_pattern = _shell_pattern + Literal('-') + OneOrMore(_shell_pattern)

def iupac2latex(iupac):
    """
    Formats IUPAC symbol for LaTeX.

    :arg iupac: string of an IUPAC symbol, transition or transitionset
    """
    s = ''
    if isinstance(iupac, _BaseTransition):
        s = iupac.symbol + ' '
        iupac = getattr(iupac, 'iupac')

    for parts in _iupac_pattern.parseString(iupac):
        if len(parts) == 2:
            s += '%s$_{%s}$' % tuple(parts)
        else:
            s += ''.join(parts)

    return s

def siegbahn2latex(siegbahn):
    """
    Formats Siegbahn symbol for LaTeX.

    :arg siegbahn: string of a Siegbahn symbol, transition or transitionset
    """
    if isinstance(siegbahn, _BaseTransition):
        siegbahn = siegbahn.symbol + " " + getattr(siegbahn, 'siegbahn')

    s = ''
    for c in siegbahn:
        s += "$_{%s}$" % c if c.isdigit() else c

    s = s.replace(u'\u03B1', r'$\alpha$')
    s = s.replace(u'\u03B2', r'$\beta$')
    s = s.replace(u'\u03B3', r'$\gamma$')
    s = s.replace(u'\u03B6', r'$\zeta$')
    s = s.replace(u'\u03B7', r'$\eta$')
    s = s.replace(u'\u03BD', r'$\nu')
    s = s.replace(u'\u2113', r'$l$')

    s = s.replace('$$', '')

    return str(s)

def _siegbahn_ascii_to_unicode(siegbahn):
    """
    Replaces some ascii characters in Siegbahn with unicode characters.
    """
    siegbahn = siegbahn.replace('a', u'\u03B1')
    siegbahn = siegbahn.replace('b', u'\u03B2')
    siegbahn = siegbahn.replace('g', u'\u03B3')
    siegbahn = siegbahn.replace('z', u'\u03B6')
    siegbahn = siegbahn.replace('n', u'\u03B7')
    siegbahn = siegbahn.replace('v', u'\u03BD')
    siegbahn = siegbahn.replace('l', u'\u2113')
    siegbahn = siegbahn.replace("'", u'\u2032')
    return siegbahn

def _siegbahn_unicode_to_ascii(siegbahn):
    """
    Replaces unicode characters in Siegbahn with ascii characters.
    """
    siegbahn = siegbahn.replace(u'\u03B1', 'a')
    siegbahn = siegbahn.replace(u'\u03B2', 'b')
    siegbahn = siegbahn.replace(u'\u03B3', 'g')
    siegbahn = siegbahn.replace(u'\u03B6', 'z')
    siegbahn = siegbahn.replace(u'\u03B7', 'n')
    siegbahn = siegbahn.replace(u'\u03BD', 'v')
    siegbahn = siegbahn.replace(u'\u2113', 'l')
    siegbahn = siegbahn.replace(u'\u2032', "'")
    return siegbahn

"""
Subshells (source -> destination) of all transitions.
"""
_SUBSHELLS = \
    [(4, 1, 0) , (3, 1, 0) , (7, 1, 0) , (12, 1, 0), (6, 1, 0) , (14, 1, 0) , (9, 1, 0) ,
     (11, 4, 0), (12, 4, 0), (18, 4, 0), (19, 4, 0), (24, 4, 0), (9, 4, 0)  , (8, 4, 0) ,
     (13, 4, 0), (14, 4, 0), (20, 4, 0), (10, 4, 0), (17, 4, 0), (5, 4, 0)  , (7, 4, 0) ,
     (6, 4, 0) , (15, 4, 0), (6, 3, 0) , (9, 3, 0) , (11, 3, 0), (12, 3, 0) , (14, 3, 0),
     (18, 3, 0), (19, 3, 0), (25, 3, 0), (8, 3, 0) , (7, 3, 0) , (13, 3, 0) , (10, 3, 0),
     (20, 3, 0), (17, 3, 0), (5, 3, 0) , (15, 3, 0), (5, 2, 0) , (10, 2, 0) , (13, 2, 0),
     (17, 2, 0), (20, 2, 0), (8, 2, 0) , (7, 2, 0) , (6, 2, 0) , (9, 2, 0)  , (11, 2, 0),
     (14, 2, 0), (12, 2, 0), (19, 2, 0), (18, 2, 0), (11, 5, 0), (12, 5, 0) , (8, 6, 0) ,
     (10, 6, 0), (13, 6, 0), (20, 6, 0), (8, 7, 0) , (9, 7, 0) , (10, 7, 0) , (13, 7, 0),
     (17, 7, 0), (20, 7, 0), (21, 7, 0), (14, 7, 0), (12, 8, 0), (18, 8, 0) , (15, 8, 0),
     (11, 8, 0), (19, 9, 0), (16, 9, 0), (15, 9, 0), (12, 9, 0), (15, 13, 0), (15, 14, 0)]

# Append for satellites
_SUBSHELLS += \
    [(4, 1, 1), (4, 1, 2), (4, 1, 3), (4, 1, 4), (4, 1, 5), (4, 1, 6),
     (7, 1, 1)]

_SIEGBAHNS = \
    [u"K\u03B11", u"K\u03B12", u"K\u03B21", u"K\u03B22", u"K\u03B23",
     u"K\u03B24", u"K\u03B25", "L3N2", "L3N3", "L3O2", "L3O3", "L3P1",
     u"L\u03B11", u"L\u03B12", u"L\u03B215", u"L\u03B22", u"L\u03B25",
     u"L\u03B26", u"L\u03B27", u"L\u2113", "Ls", "Lt", "Lu", "L2M2",
     "L2M5", "L2N2", "L2N3", "L2N5", "L2O2", "L2O3", "L2P2",
     u"L\u03B21", u"L\u03B217", u"L\u03B31", u"L\u03B35", u"L\u03B36",
     u"L\u03B38", u"L\u03B7", u"L\u03BD", "L1M1", "L1N1", "L1N4",
     "L1O1", "L1O4", u"L\u03B210", u"L\u03B23", u"L\u03B24",
     u"L\u03B29", u"L\u03B32", u"L\u03B311", u"L\u03B33", u"L\u03B34",
     u"L\u03B34p", "M1N2", "M1N3", "M2M4", "M2N1", "M2N4", "M2O4",
     "M3M4", "M3M5", "M3N1", "M3N4", "M3O1", "M3O4", "M3O5",
     u"M\u03B3", "M4N3", "M4O2", u"M\u03B2", u"M\u03B62", "M5O3",
     u"M\u03B11", u"M\u03B12", u"M\u03B61", "N4N6", "N5N6"]

# Append for satellites
_SIEGBAHNS += \
    [u"SK\u03B1\u2032", u"SK\u03B1\u2032\u2032", u"SK\u03B13", u"SK\u03B14",
     u"SK\u03B15", u"SK\u03B16", u"SK\u03B2\u2032"]

@total_ordering
class _BaseTransition(object):

    __metaclass__ = ABCMeta

    def __init__(self, z, siegbahn, iupac):
        self._z = z
        self._symbol = ep.symbol(z)
        self._siegbahn = siegbahn
        self._iupac = iupac

    if sys.version_info > (3, 0):
        __str__ = lambda x: x.__unicode__()
    else: # Python 2
        __str__ = lambda x: "%s %s" % (x.symbol, x.siegbahn_nogreek)

    def __unicode__(self):
        return "%s %s" % (self.symbol, self.siegbahn)

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError

    @property
    def z(self):
        """
        Atomic number of this transition.
        """
        return self._z

    atomicnumber = z

    @property
    def symbol(self):
        """
        Symbol of the element of this transition.
        """
        return self._symbol

    @property
    def iupac(self):
        """
        IUPAC symbol of this transition.
        """
        return self._iupac

    @property
    def siegbahn(self):
        """
        Seigbahn symbol of this transition.
        """
        return self._siegbahn

    @property
    def siegbahn_nogreek(self):
        """
        Seigbahn symbol of this transition (greek characters removed).
        """
        return _siegbahn_unicode_to_ascii(self.siegbahn)

class Transition(_BaseTransition):

    def __init__(self, z, src=None, dest=None, satellite=0, siegbahn=None):
        """
        Creates a new transition from a source and destination subshells
        or from its Siegbahn symbol::

           t = Transition(29, 4, 1)
           t = Transition(29, siegbahn='Ka1')

        :arg z: atomic number (from 3 to 99 inclusively)
        :arg src: source subshell index between 1 (K) and 30 (outer) or subshell object
        :arg dest: destination subshell index between 1 (K) and 30 (outer) or subshell object
        :arg satellite: index representing the satellite, 0 for main line
        :arg siegbahn: Siegbahn symbol
        """
        if src is not None and dest is not None:
            if src < dest:
                raise ValueError("The source subshell (%s) must be greater " + \
                        "than the destination subshell (%s)" % (src, dest))

            if hasattr(src, 'index'): src = src.index
            if hasattr(dest, 'index'): dest = dest.index

            try:
                index = _SUBSHELLS.index((src, dest, satellite))
            except ValueError:
                raise ValueError("Unknown transition (%i -> %i, %i)" % \
                        (src, dest, satellite))
        elif siegbahn is not None:
            siegbahn = _siegbahn_ascii_to_unicode(siegbahn)

            # Fix to be compatible with old transition, e.g. N5N6/N6N7
            if '/' in siegbahn: siegbahn = siegbahn[:siegbahn.index('/')]

            try:
                index = _SIEGBAHNS.index(siegbahn)
            except ValueError:
                raise ValueError("Unknown transition (%s)" % siegbahn)
        else:
            raise ValueError("Specify shells or Siegbahn")

        src, dest, satellite = _SUBSHELLS[index]

        self._src = Subshell(z, src)
        self._dest = Subshell(z, dest)
        self._satellite = satellite

        siegbahn = _SIEGBAHNS[index]
        iupac = '-'.join([self._dest.iupac, self._src.iupac])
        _BaseTransition.__init__(self, z, siegbahn, iupac)

        subshells = (src, dest, satellite)
        self._exists = transition_data.exists(z, subshells)
        self._energy_eV = transition_data.energy_eV(z, subshells)
        self._probability = transition_data.probability(z, subshells)

        try:
            self._wavelength_m = energy_to_wavelength_m(self._energy_eV)
        except ZeroDivisionError: # Energy == 0.0 if transition does not exist
            self._wavelength_m = float('inf')

        self._width_eV = self._src.width_eV + self._dest.width_eV

        try:
            self._width_m = energy_to_wavelength_m(self._width_eV)
        except ZeroDivisionError:
            self._width_m = float('inf')

    def __repr__(self):
        return '<Transition(%s %s)>' % (self.symbol, self.siegbahn_nogreek)

    def __eq__(self, other):
        if type(other) is self.__class__:
            return (self.z, self.src, self.dest, self.satellite) == \
                    (other.z, other.src, other.dest, other.satellite)
        elif type(other) is transitionset:
            if len(other) > 1:
                return False
            return self == next(iter(other))
        else:
            return NotImplemented

    def __lt__(self, other):
        if type(other) is self.__class__:
            return (self.z, self.src, self.dest, self.satellite) < \
                    (other.z, other.src, other.dest, other.satellite)
        elif type(other) is transitionset:
            if len(other) > 1:
                return True
            return self < next(iter(other))
        else:
            return NotImplemented

    def __hash__(self):
        return hash((self.__class__, self.z, self.src, self.dest, self.satellite))

    def __getstate__(self):
        # Only pickle the required information to create a transition
        return {'z': self.z,
                'src': self.src.index,
                'dest': self.dest.index,
                'satellite': self.satellite}

    def __reduce__(self):
        return (self.__class__,
                (self.z, self.src, self.dest, self.satellite))

    def exists(self):
        """
        Whether this transition exists.
        """
        return self._exists

    def is_diagram_line(self):
        """
        Whether this transition is a diagram line (main line).
        """
        return self._satellite == 0

    def is_satellite(self):
        """
        Whether this transition is a satellite line / non-diagram line.
        """
        return self._satellite != 0

    @property
    def src(self):
        """
        Source shell of this transition.
        """
        return self._src

    @property
    def dest(self):
        """
        Destination shell of this transition.
        """
        return self._dest

    @property
    def satellite(self):
        """
        Index of the satellite. 0 if this transition is the main diagram line.
        """
        return self._satellite

    @property
    def energy_eV(self):
        """
        Energy of this transition in eV.
        """
        return self._energy_eV

    @property
    def wavelength_m(self):
        """
        Wavelength of this transition in meters.
        """
        return self._wavelength_m

    @property
    def probability(self):
        """
        Probability of this transition.
        """
        return self._probability

    @property
    def width_eV(self):
        """
        Natural width of this transition in eV.
        """
        return self._width_eV

    @property
    def width_m(self):
        """
        Natural width of this transition in meters.
        """
        return self._width_m

class transitionset(Set, _BaseTransition):

    @classmethod
    def _from_iterable(cls, it):
        transitions = list(it)
        zs = list(set(map(_ZGETTER, transitions)))
        if len(zs) != 1:
            raise ValueError("All transitions in a set must have the same atomic number")
        return cls(zs[0], "", "", transitions)

    def __init__(self, z, siegbahn, iupac, transitions):
        """
        Creates a frozen set (immutable) of transitions.
        The atomic number must be the same for all transitions.

        :arg z: atomic number of all transitions
        :arg siegbahn: Siegbahn symbol of the set
        :arg iupac: IUPAC symbol of the set
        :arg transitions: transitions of the set
        """
        if not transitions:
            raise ValueError('A transitionset must contain at least one transition')

        # Common z
        zs = set(map(_ZGETTER, transitions))
        if len(zs) != 1:
            raise ValueError("All transitions in a set must have the same atomic number")

        _BaseTransition.__init__(self, z, siegbahn, iupac)
        self._transitions = frozenset(transitions)

        self._most_probable = \
            sorted(self, key=attrgetter('probability'), reverse=True)[0]

    def __repr__(self):
        s = ', '.join(map(attrgetter('siegbahn_nogreek'), sorted(self)))
        return '<transitionset(%s %s: %s)>' % (self.symbol, self.siegbahn_nogreek, s)

    def __len__(self):
        return len(self._transitions)

    def __hash__(self):
        return hash((self.__class__,) + tuple(sorted(self)))

    def __iter__(self):
        return iter(self._transitions)

    def __contains__(self, other):
        return other in self._transitions

    def __eq__(self, other):
        if type(other) is  self.__class__:
            if len(self) != len(other):
                return False
            return tuple(sorted(self)) == tuple(sorted(other))
        elif type(other) is Transition:
            if len(self) > 1:
                return False
            return next(iter(self)) == other
        else:
            return NotImplemented

    def __lt__(self, other):
        if type(other) is self.__class__:
            return tuple(sorted(self)) < tuple(sorted(other))
        elif type(other) is Transition:
            if len(self) > 1:
                return False
            return next(iter(self)) < other
        else:
            return NotImplemented

    def __gt__(self, other):
        if self < other:
            return False
        elif self == other:
            return False
        else:
            return True

    @property
    def most_probable(self):
        return self._most_probable

def get_transitions(z, energylow_eV=0.0, energyhigh_eV=1e6, include_satellite=False):
    """
    Returns all the X-ray transitions for the specified atomic number if
    the energy of these transitions is between the specified energy limits.
    The energy limits are inclusive.

    :arg z: atomic number (3 to 99)
    :arg energylow_eV: lower energy limit in eV (default: 0 eV)
    :arg energyhigh_eV: upper energy limit in eV (default: 1 MeV)
    """
    transitions = []

    for src, dest, satellite in _SUBSHELLS:
        if not include_satellite and satellite != 0:
            continue

        if not transition_data.exists(z, (src, dest)):
            continue

        energy = transition_data.energy_eV(z, (src, dest))
        if energy < energylow_eV or energy > energyhigh_eV:
            continue

        transitions.append(Transition(z, src, dest, satellite))

    return sorted(transitions)

def from_string(s):
    """
    Returns a :class:`Transition` or :class:`transitionset` from the given
    string.
    The first word must be the symbol of the element followed by either the
    Siegbahn (e.g. ``Al Ka1``) or IUPAC (``Al K-L3``) notation of the
    transition.
    The second word can also represent transition family (e.g. ``Al K``) or
    shell (``Al LIII``).

    :arg s: string representing the transition

    :return: transition or set of transitions
    """
    words = s.split(" ")
    if len(words) != 2:
        raise ValueError("The transition string must have 2 words: " + \
            "1. the symbol of the element and 2. the transition notation")

    z = ep.atomic_number(symbol=words[0])
    notation = words[1]

    # Fix to be compatible with old transition, e.g. N5N6/N6N7
    if '/' in notation: notation = notation[:notation.index('/')]
    if notation == 'Le': notation = 'Ln'

    notation = _siegbahn_ascii_to_unicode(notation)

    if notation in _SIEGBAHNS: # Transition with Siegbahn notation
        return Transition(z, siegbahn=notation)
    elif notation in _TRANSITIONSETS: # transitionset from Family, group or shell
        return _TRANSITIONSETS[notation](z)
    elif '-' in notation: # Transition with IUPAC notation
        dest, src = notation.split('-')
        return Transition(z, src=Subshell(z, iupac=src), dest=Subshell(z, iupac=dest))
    else:
        raise ValueError("Cannot parse transition string: %s" % s)

def _group(z, siegbahn, iupac, include_satellite=False):
    transitions = []

    for ssiegbahn in _SIEGBAHNS:
        if ssiegbahn.startswith(siegbahn):
            transitions.append(Transition(z, siegbahn=ssiegbahn))

    transitions = filter(methodcaller('exists'), transitions)
    if not include_satellite:
        transitions = filter(methodcaller('is_diagram_line'), transitions)

    if not transitions:
        raise ValueError('No transition for %s %s' % (ep.symbol(z), iupac))

    return transitionset(z, siegbahn, iupac, list(transitions))

def _shell(z, dest, include_satellite=False):
    subshell = Subshell(z, dest)
    siegbahn = subshell.siegbahn
    iupac = subshell.iupac

    transitions = []

    for src, ddest, satellite in _SUBSHELLS:
        if ddest != dest: continue
        if satellite != 0 and not include_satellite: continue
        transitions.append(Transition(z, src, dest))

    transitions = filter(methodcaller('exists'), transitions)
    if not transitions:
        raise ValueError('No transition for %s %s' % (ep.symbol(z), iupac))

    return transitionset(z, siegbahn, iupac, list(transitions))

def K_family(z, include_satellite=False):
    """
    Returns all transitions from the K family.
    """
    return _group(z, 'K', 'K', include_satellite)

def L_family(z, include_satellite=False):
    """
    Returns all transitions from the L family.
    """
    return _group(z, 'L', 'L', include_satellite)

def M_family(z, include_satellite=False):
    """
    Returns all transitions from the M family.
    """
    return _group(z, 'M', 'M', include_satellite)

def N_family(z, include_satellite=False):
    """
    Returns all transitions from the N family.
    """
    return _group(z, 'N', 'N', include_satellite)

def Ka(z, include_satellite=False):
    """
    Returns all transitions from the Ka group.
    """
    return _group(z, u'K\u03b1', 'K-L(2,3)', include_satellite)

def Kb(z, include_satellite=False):
    """
    Returns all transitions from the Kb group.
    """
    return _group(z, u'K\u03b2', 'K-M(2-5)N(2-5)', include_satellite)

def La(z, include_satellite=False):
    """
    Returns all transitions from the La group.
    """
    return _group(z, u'L\u03b1', 'L3-M(4,5)', include_satellite)

def Lb(z, include_satellite=False):
    """
    Returns all transitions from the Lb group.
    """
    return _group(z, u'L\u03b2', 'L(1-3)-M(2-5)N(1,4-7)O(1,4-5)', include_satellite)

def Lg(z, include_satellite=False):
    """
    Returns all transitions from the Lg group.
    """
    return _group(z, u'L\u03b3', 'L(1,2)-N(1-6)O(1-3)', include_satellite)

def Ma(z, include_satellite=False):
    """
    Returns all transitions from the Ma group.
    """
    return _group(z, u'M\u03b1', 'M5-N(6,7)', include_satellite)

def Mb(z, include_satellite=False):
    """
    Returns all transitions from the Mb group.
    """
    return _group(z, u'M\u03b2', 'M4-N6', include_satellite)

def Mg(z, include_satellite=False):
    """
    Returns all transitions from the Mg group.
    """
    return _group(z, u'M\u03b3', 'M3-N5', include_satellite)

def Mz(z, include_satellite=False):
    """
    Returns all transitions from the Mz group.
    """
    return _group(z, u'M\u03b6', 'M(4-5)-N(2-3)', include_satellite)

def LI(z, include_satellite=False):
    """
    Returns all transitions ending on the L\ :sub:`I` shell.
    """
    return _shell(z, 2, include_satellite)

def LII(z, include_satellite=False):
    """
    Returns all transitions ending on the L\ :sub:`II` shell.
    """
    return _shell(z, 3, include_satellite)

def LIII(z, include_satellite=False):
    """
    Returns all transitions ending on the L\ :sub:`III` shell.
    """
    return _shell(z, 4, include_satellite)

def MI(z, include_satellite=False):
    """
    Returns all transitions ending on the M\ :sub:`I` shell.
    """
    return _shell(z, 5, include_satellite)

def MII(z, include_satellite=False):
    """
    Returns all transitions ending on the M\ :sub:`II` shell.
    """
    return _shell(z, 6, include_satellite)

def MIII(z, include_satellite=False):
    """
    Returns all transitions ending on the M\ :sub:`III` shell.
    """
    return _shell(z, 7, include_satellite)

def MIV(z, include_satellite=False):
    """
    Returns all transitions ending on the M\ :sub:`IV` shell.
    """
    return _shell(z, 8, include_satellite)

def MV(z, include_satellite=False):
    """
    Returns all transitions ending on the M\ :sub:`V` shell.
    """
    return _shell(z, 9, include_satellite)

_TRANSITIONSETS = {'K': K_family, 'L': L_family, 'M': M_family,
                   u'K\u03b1': Ka, u'K\u03b2': Kb,
                   u'L\u03b1': La, u'L\u03b2': Lb, u'L\u03b3': Lg,
                   u'M\u03b1': Ma, u'M\u03b2': Mb, u'M\u03b3': Mg,
                   'L1': LI, 'L2': LII, 'L3': LIII,
                   'M1': MI, 'M2': MII, 'M3': MIII, 'M4': MIV, 'M5': MV,
                   'K-L(2,3)': Ka, 'K-M(2-5)N(2-5)': Kb,
                   'L3-M(4,5)': La, 'L(1-3)-M(2-5)N(1,4-7)O(1,4-5)': Lb, 'L(1,2)-N(1-6)O(1-3)': Lg,
                   'M5-N(6,7)': Ma, 'M4-N6': Mb, 'M3-N5': Mg}
