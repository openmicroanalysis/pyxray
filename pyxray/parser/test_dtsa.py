#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyxray.parser.dtsa import DtsaSubshellParser

# Globals and constants variables.


class TestDtsaSubshellParser(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.parser = DtsaSubshellParser()

    def test__iter__(self):
        props = list(self.parser)
        self.assertEqual(1045, len(props))

        self.assertEqual(3, props[0].element.z)
        self.assertAlmostEqual(54.75, props[0].value_eV, 2)

        self.assertEqual(95, props[-1].element.z)
        self.assertAlmostEqual(366.49, props[-1].value_eV, 2)


if __name__ == '__main__':  # pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
