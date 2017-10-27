""""""

# Standard library modules.

# Third party modules.

# Local modules.
import pyxray
from pyxray.cbook import Validable, Cachable

# Globals and constants variables.

class _XrayLineMeta(Validable, Cachable):
    pass

class XrayLine(metaclass=_XrayLineMeta):

    __slots__ = ('__weakref__', '_element', '_line', '_is_xray_transitionset', '_iupac', '_siegbahn')

    @classmethod
    def validate(cls, element, line):
        if not isinstance(element, pyxray.Element):
            element = pyxray.element(element)

        if not isinstance(line, (pyxray.XrayTransition, pyxray.XrayTransitionSet)):
            try:
                line = pyxray.xray_transition(line)
            except pyxray.NotFound:
                line = pyxray.xray_transitionset(line)

        return (element, line)

    def __init__(self, element, line):
        is_xray_transitionset = isinstance(line, pyxray.XrayTransitionSet)

        symbol = pyxray.element_symbol(element)

        if is_xray_transitionset:
            method = pyxray.xray_transitionset_notation
        else:
            method = pyxray.xray_transition_notation

        iupac = '{} {}'.format(symbol, method(line, 'iupac', 'utf16'))

        try:
            siegbahn = '{} {}'.format(symbol, method(line, 'siegbahn', 'utf16'))
        except pyxray.NotFound:
            siegbahn = iupac

        self._element = element
        self._line = line
        self._is_xray_transitionset = is_xray_transitionset
        self._iupac = iupac
        self._siegbahn = siegbahn

    def __hash__(self):
        return hash((self.element, self.line))

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.element == other.element and \
            self.line == other.line

    def __iter__(self):
        return iter((self.element, self.line))

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.iupac)

    def is_xray_transitionset(self):
        return self._is_xray_transitionset

    @property
    def element(self):
        return self._element

    @property
    def atomic_number(self):
        return self.element.atomic_number

    @property
    def line(self):
        return self._line

    @property
    def iupac(self):
        return self._iupac

    @property
    def siegbahn(self):
        return self._siegbahn
