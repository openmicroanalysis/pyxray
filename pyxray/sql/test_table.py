#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging
import os
import tempfile
import shutil
import sqlite3

# Third party modules.
from sqlalchemy import create_engine

# Local modules.
from pyxray.sql.table import metadata

# Globals and constants variables.

class Testtable(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.tmpdir = tempfile.mkdtemp()
        self.dbpath = os.path.join(self.tmpdir, 'test.db')

        self.engine = create_engine("sqlite:///" + self.dbpath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def testcreateall(self):
        metadata.create_all(self.engine)

        conn = sqlite3.connect(self.dbpath)
        command = "SELECT count(*) FROM sqlite_master WHERE type = 'table'"
        ntable, = conn.execute(command).fetchone()
        self.assertEqual(26, ntable)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
