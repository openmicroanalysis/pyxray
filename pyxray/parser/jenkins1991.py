"""

"""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Transition, AtomicSubshell, Notation
from pyxray.property import TransitionNotation

# Globals and constants variables.

JENKINS1991 = Reference('jenkins1991',
                        author='Jenkins, R. and Manne, R. and Robin, R. and Senemaud, C.',
                        journal='X-Ray Spectrometry',
                        doi='10.1002/xrs.1300200308',
                        pages='149--155',
                        title='{IUPAC} --- nomenclature system for x-ray spectroscopy',
                        volume=20,
                        year=1991)

K = AtomicSubshell(1, 0, 1)
L1 = AtomicSubshell(2, 0, 1)
L2 = AtomicSubshell(2, 1, 1)
L3 = AtomicSubshell(2, 1, 3)

class Jenkins1991TransitionNotationParser(_Parser):

    def __iter__(self):
        transition = Transition(L3, K)
        notation = Notation('siegbahn')
        ascii = 'Ka1'
        utf16 = 'K\u03b11'
        html = 'K&alpha;<sub>1</sub>'
        latex = 'K$\\alpha_1$'
        yield TransitionNotation(JENKINS1991, transition, notation,
                                 ascii, utf16, html, latex)
