#!/usr/bin/env python
""" """

# Standard library modules.

# Third party modules.

# Local modules.
from pyxray.parser.unattributed import \
    (ElementSymbolPropertyParser, AtomicShellNotationParser,
     AtomicSubshellNotationParser, TransitionNotationParser,
     iter_subshells)

# Globals and constants variables.

def test_iter_subshells():
    assert len(list(iter_subshells(1))) == 1
    assert len(list(iter_subshells(2))) == 4
    assert len(list(iter_subshells(7))) == 49

def test_unattributed_symbol():
    parser = ElementSymbolPropertyParser()
    assert len(list(parser)) == 118

def test_unattributed_atomicshell_notation():
    parser = AtomicShellNotationParser()
    assert len(list(parser)) == 21

def test_unattributed_atomicsubshell_notation():
    parser = AtomicSubshellNotationParser()
    assert len(list(parser)) == 147

def test_unattributed_transition_notation():
    parser = TransitionNotationParser()
    assert len(list(parser)) == 1176
