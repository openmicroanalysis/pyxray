"""

"""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.parser import _Parser
from pyxray.descriptor import Reference, Transition, AtomicSubshell, Notation, TransitionSet
from pyxray.property import TransitionNotation, TransitionSetNotation

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
M1 = AtomicSubshell(3, 0, 1)
M2 = AtomicSubshell(3, 1, 1)
M3 = AtomicSubshell(3, 1, 3)
M4 = AtomicSubshell(3, 2, 3)
M5 = AtomicSubshell(3, 2, 5)

class Jenkins1991TransitionNotationParser(_Parser):

    def __iter__(self):
        siegbahn = Notation('siegbahn')
        iupac = Notation('iupac')

        transition_ka1 = Transition(L3, K)
        ascii = 'Ka1'
        utf16 = 'K\u03b11'
        html = 'K&alpha;<sub>1</sub>'
        latex = '\\ensuremath{\\mathrm{K}\\alpha_1}'
        yield TransitionNotation(JENKINS1991, transition_ka1, siegbahn,
                                 ascii, utf16, html, latex)

        transition_ka2 = Transition(L2, K)
        ascii = 'Ka2'
        utf16 = 'K\u03b12'
        html = 'K&alpha;<sub>2</sub>'
        latex = '\\ensuremath{\\mathrm{K}\\alpha_2}'
        yield TransitionNotation(JENKINS1991, transition_ka2, siegbahn,
                                 ascii, utf16, html, latex)

        transition_la1 = Transition(M5, L3)
        ascii = 'La1'
        utf16 = 'L\u03b11'
        html = 'L&alpha;<sub>1</sub>'
        latex = '\\ensuremath{\\mathrm{L}\\alpha_1}'
        yield TransitionNotation(JENKINS1991, transition_la1, siegbahn,
                                 ascii, utf16, html, latex)

        transition_la2 = Transition(M4, L3)
        ascii = 'La2'
        utf16 = 'L\u03b12'
        html = 'L&alpha;<sub>2</sub>'
        latex = '\\ensuremath{\\mathrm{L}\\alpha_2}'
        yield TransitionNotation(JENKINS1991, transition_la2, siegbahn,
                                 ascii, utf16, html, latex)

        transitionset_ka = TransitionSet([transition_ka1, transition_ka2])
        ascii = 'Ka'
        utf16 = 'K\u03b1'
        html = 'K&alpha;'
        latex = '\\ensuremath{\\mathrm{K}\\alpha}'
        yield TransitionSetNotation(JENKINS1991, transitionset_ka, siegbahn,
                                    ascii, utf16, html, latex)

        ascii = 'K-L23'
        utf16 = 'K-L23'
        html = 'K-L<sub>2,3</sub>'
        latex = '\\ensuremath{\\mathrm{\\mathrm{K}}}--\\ensuremath{\\mathrm{\\mathrm{L}_{2,3}}}'
        yield TransitionSetNotation(JENKINS1991, transitionset_ka, iupac,
                                    ascii, utf16, html, latex)

        transitionset_la = TransitionSet([transition_la1, transition_la2])
        ascii = 'La'
        utf16 = 'L\u03b1'
        html = 'L&alpha;'
        latex = '\\ensuremath{\\mathrm{L}\\alpha}'
        yield TransitionSetNotation(JENKINS1991, transitionset_la, siegbahn,
                                    ascii, utf16, html, latex)


