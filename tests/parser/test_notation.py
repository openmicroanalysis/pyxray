""""""

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.notation import iter_subshells, ElementSymbolParser, AtomicShellNotationParser, AtomicSubshellNotationParser, GenericXrayTransitionNotationParser, KnownXrayTransitionNotationParser, SeriesXrayTransitionNotationParser, FamilyXrayTransitionNotationParser

# Globals and constants variables.

def test_iter_subshells():
    assert len(list(iter_subshells(1))) == 1
    assert len(list(iter_subshells(2))) == 4
    assert len(list(iter_subshells(7))) == 49

def test_unattributed_symbol():
    parser = ElementSymbolParser()
    assert len(list(parser)) == 118

def test_atomicshell_notation():
    parser = AtomicShellNotationParser()
    assert len(list(parser)) == 21

def test_atomicsubshell_notation():
    parser = AtomicSubshellNotationParser()
    assert len(list(parser)) == 147

def test_generic_xray_transition_notation():
    parser = GenericXrayTransitionNotationParser()
    assert len(list(parser)) == 1176

def test_known_xray_transition_notation():
    parser = KnownXrayTransitionNotationParser()
    assert len(list(parser)) == 76

def test_series_xray_transition_notation():
    parser = SeriesXrayTransitionNotationParser()
    assert len(list(parser)) == 14

def test_family_xray_transition_notation():
    parser = FamilyXrayTransitionNotationParser()
    assert len(list(parser)) == 96