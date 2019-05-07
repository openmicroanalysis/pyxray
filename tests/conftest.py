#!/usr/bin/env python
""" """

# Standard library modules.
import os

# Third party modules.
import pytest

# Local modules.

# Globals and constants variables.

@pytest.fixture
def testdatadir():
    return os.path.join(os.path.dirname(__file__), 'testdata')