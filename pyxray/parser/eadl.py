#!/usr/bin/env python
"""
================================================================================
:mod:`eadl` -- Parser for the Evaluated Atomic Data Library (EADL)
================================================================================

.. module:: eadl
   :synopsis: Parser for the Evaluated Atomic Data Library (EADL)

.. inheritance-diagram:: pyxray.parser.eadl

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2013 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import re
import itertools
import csv

# Third party modules.

# Local modules.

# Globals and constants variables.

FLOAT_PATTERN = re.compile(r'([\d.]+)([\+\-])([\d ]+)')

def float_(text):
    text = text.strip()
    base, sign, exp = FLOAT_PATTERN.match(text).groups()
    base = float(base)
    exp = float(exp) if sign == '+' else -float(exp)
    return base * 10 ** exp

# Conversion from EADL to pyxray index for subshell
SUBSHELL_LOOKUP = {
    1: 1, # K
    3: 2, 5: 3, 6: 4, # L
    8: 4, 10: 5, 11: 7, 13: 8, 14: 9, # M
    16: 10, 18: 11, 19: 12, 21: 13, 22: 14, 24: 15, 25: 16, # N
    27: 17, 29: 18, 30: 19, 32: 20, 33: 21, 35: 22, 36: 23, # O
    41: 24, 43: 25, 44: 26, 46: 27, 47: 28, # P
    58: 29 # Q
    }

ATOMIC_NUMBER = 'Z'
MASS_NUMBER = 'A'
INCIDENT_PARTICLE = 'Yi'
OUTGOING_PARTICLE = 'Yo'
ATOMIC_MASS = 'AW'
DATE = 'Date'

REACTION_DESCRIPTOR = 'C'
REACTION_PROPERTY = 'I'
REACTION_MODIFIER = 'S'
SUBSHELL_DESIGNATOR = 'X1'

PRIMARY_SUBSHELL = 'i'
SECONDARY_SUBSHELL = 'j'
BINDING_ENERGY = 'Ebe'
RADIATIVE_WIDTH = 'width r'
RADIATIVE_PROBABILITY = 'f r'
RADIATIVE_ENERGY = 'Er'

class EADLParser(object):

    def extract(self, infile, outfile, fieldnames, parser_func):
        writer = csv.DictWriter(outfile, fieldnames, extrasaction='ignore')

        group_separator = self._get_group_separator()
        for key, group in itertools.groupby(infile, group_separator):
            if key: continue

            inrows = list(group)
            outrow = {}

            header = self._parse_group_header(inrows)
            outrow.update(header)

            results = parser_func(header, inrows[2:])
            if not results:
                continue

            for result in results:
                outrow.update(result)
                writer.writerow(outrow)

    def extract_subshell_binding_energy(self, infile, outfile):
        fieldnames = [ATOMIC_NUMBER, PRIMARY_SUBSHELL, BINDING_ENERGY]
        self.extract(infile, outfile, fieldnames, self._parse_subshell_binding_energy)

    def extract_subshell_width(self, infile, outfile):
        fieldnames = [ATOMIC_NUMBER, PRIMARY_SUBSHELL, RADIATIVE_WIDTH]
        self.extract(infile, outfile, fieldnames, self._parse_subshell_radiative_width)

    def extract_radiative_transition(self, infile, outfile):
        fieldnames = [ATOMIC_NUMBER, PRIMARY_SUBSHELL, SECONDARY_SUBSHELL,
                      RADIATIVE_PROBABILITY, RADIATIVE_ENERGY]
        self.extract(infile, outfile, fieldnames, self._parse_radiative_transition)

    def _get_group_separator(self):
        def group_separator(line):
            return line.rstrip() == '                                                                       1'
        return group_separator

    def _parse_group_header(self, rows):
        header = {}

        # First row
        row = rows[0]
        header[ATOMIC_NUMBER] = int(row[0:3])
        header[MASS_NUMBER] = int(row[3:6])
        header[INCIDENT_PARTICLE] = int(row[7:9])
        header[OUTGOING_PARTICLE] = int(row[10:12])
        header[ATOMIC_MASS] = float_(row[13:24])
        header[DATE] = int(row[25:31])

        # Second row
        row = rows[1]
        header[REACTION_DESCRIPTOR] = int(row[0:2])
        header[REACTION_PROPERTY] = int(row[2:5])
        header[REACTION_MODIFIER] = int(row[5:8])
        header[SUBSHELL_DESIGNATOR] = float_(row[21:32])

        return header

    def _parse_subshell_binding_energy(self, header, inrows):
        if header[REACTION_DESCRIPTOR] != 91 or \
                header[REACTION_PROPERTY] != 913:
            return []

        outrows = []
        for row in inrows:
            subshell = int(float_(row[0:11]))
            if subshell not in SUBSHELL_LOOKUP:
                continue
            subshell = SUBSHELL_LOOKUP[subshell]

            energy = float_(row[11:22]) * 1e6

            outrows.append({PRIMARY_SUBSHELL: subshell, BINDING_ENERGY: energy})

        return outrows

    def _parse_subshell_radiative_width(self, header, inrows):
        if header[REACTION_DESCRIPTOR] != 91 or \
                header[REACTION_PROPERTY] != 921:
            return []

        outrows = []
        for row in inrows:
            subshell = int(float_(row[0:11]))
            if subshell not in SUBSHELL_LOOKUP:
                continue
            subshell = SUBSHELL_LOOKUP[subshell]

            width = float_(row[11:22]) * 1e6

            outrows.append({PRIMARY_SUBSHELL: subshell, RADIATIVE_WIDTH: width})

        return outrows

    def _parse_radiative_transition(self, header, inrows):
        if header[REACTION_DESCRIPTOR] != 92 or \
                header[REACTION_PROPERTY] != 931 or \
                header[REACTION_MODIFIER] != 91 or \
                header[OUTGOING_PARTICLE] != 7:
            return []

        # Destination
        destshell = header[SUBSHELL_DESIGNATOR]
        if destshell not in SUBSHELL_LOOKUP:
            return []
        destshell = SUBSHELL_LOOKUP[destshell]

        outrows = []
        for row in inrows:
            srcshell = int(float_(row[0:11]))
            if srcshell not in SUBSHELL_LOOKUP:
                continue
            srcshell = SUBSHELL_LOOKUP[srcshell]

            probability = float_(row[11:22])
            energy = float_(row[22:33]) * 1e6

            outrows.append({PRIMARY_SUBSHELL: destshell,
                            SECONDARY_SUBSHELL: srcshell,
                            RADIATIVE_PROBABILITY: probability,
                            RADIATIVE_ENERGY: energy})

        return outrows

if __name__ == '__main__':
    parser = EADLParser()

    infile = open('/tmp/eadl.all.txt', 'r')
    outfile = open('/tmp/eadl.csv', 'w')

    parser.extract_subshell_width(infile, outfile)

    infile.close()
    outfile.close()
