""" """

# Standard library modules.
import os
import csv
import ast

# Third party modules.
import pytest
import sqlalchemy

# Local modules.
from pyxray.parser.notation import AtomicSubshellNotationParser, KnownXrayTransitionNotationParser
from pyxray.sql.build import SqlDatabaseBuilder
from pyxray.sql.data import SqlDatabase
import pyxray.descriptor as descriptor
from pyxray.base import NotFound

# Globals and constants variables.

class EpqDatabaseBuilder(SqlDatabaseBuilder):

    def _find_parsers(self):
        return [('atomic subshell notation', AtomicSubshellNotationParser()),
                ('xray transition notation', KnownXrayTransitionNotationParser())]

@pytest.fixture
def database(tmp_path):
    engine = sqlalchemy.create_engine('sqlite:///' + str(tmp_path.joinpath('epq.sql')))

    builder = EpqDatabaseBuilder(engine)
    builder.build()

    return SqlDatabase(engine)

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
                actual = database.xray_transition_notation(transition, 'siegbahn')
            except NotFound:
                continue

            actual = actual.strip('I')

            assert actual == expected