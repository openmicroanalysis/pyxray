""" """

# Standard library modules.
import os
import csv
import sqlite3
import ast

# Third party modules.
import pytest

# Local modules.
from pyxray.parser.unattributed import AtomicSubshellNotationParser
from pyxray.parser.jenkins1991 import Jenkins1991TransitionNotationParser
from pyxray.sql.build import SqliteDatabaseBuilder
from pyxray.sql.data import SqlDatabase
import pyxray.descriptor as descriptor
from pyxray.base import NotFound

# Globals and constants variables.

class EpqDatabaseBuilder(SqliteDatabaseBuilder):

    def _find_parsers(self):
        return [('atomic subshell notation', AtomicSubshellNotationParser()),
                ('xray transition notation', Jenkins1991TransitionNotationParser())]

@pytest.fixture
def database(tmp_path):
    filepath = str(tmp_path.joinpath('pyxray.sql'))

    builder = EpqDatabaseBuilder(filepath)
    builder.build()

    with sqlite3.connect(builder.filepath) as connection:
        yield SqlDatabase(connection)

def test_epq_atomicsubshell_notation(database, testdatadir):
    filepath = os.path.join(testdatadir, 'epq_atomicsubshell.csv')
    with open(filepath, 'r') as fp:
        reader = csv.DictReader(fp)

        for row in reader:
            atomic_subshell = descriptor.AtomicSubshell(int(row['n']), int(row['l']), int(float(row['j']) * 2))
            assert database.atomic_subshell_notation(atomic_subshell, 'siegbahn') == row['notation']

def test_epq_xraytransition_notation(database, testdatadir):
    filepath = os.path.join(testdatadir, 'epq_xraytransition.csv')
    with open(filepath, 'r') as fp:
        reader = csv.DictReader(fp)

        for row in reader:
            source = database.atomic_subshell(row['source'])
            destination = database.atomic_subshell(row['destination'])
            transition = descriptor.XrayTransition(source, destination)

            expected = ast.literal_eval('"' + row['notation'] + '"')
            expected = expected.replace('p', "\u2032")

            try:
                assert database.xray_transition_notation(transition, 'siegbahn') == expected
            except NotFound:
                continue