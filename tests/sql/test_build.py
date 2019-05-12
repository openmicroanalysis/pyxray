#!/usr/bin/env python
""" """

# Standard library modules.
import os
import sqlite3

# Third party modules.
import pytest

# Local modules.

# Globals and constants variables.

def test_database_build(builder):
    assert os.path.exists(builder.engine.url.database)

    conn = sqlite3.connect(builder.engine.url.database)
    command = "SELECT count(*) FROM sqlite_master WHERE type = 'table'"
    ntable, = conn.execute(command).fetchone()
    assert ntable == 21

def test_database_fail(builder):
    builder.badparser = True

    with pytest.raises(Exception):
        builder.build()
