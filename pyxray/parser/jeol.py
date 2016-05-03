#!/usr/bin/env python
"""
Parser of JEOL transition data
"""

# Standard library modules.
import csv

# Third party modules.

# Local modules.

# Globals and constants variables.

_TRANSITION_LOOKUP = {
    'KA': (4, 1, 0), 'KA1': (4, 1, 0), 'KA2': (3, 1, 0),
    'SKA+': (4, 1, 1), 'SKA+2': (4, 1, 2), 'SKA3': (4, 1, 3), 'SKA4': (4, 1, 4),
    'SKA5': (4, 1, 5), 'SKA6': (4, 1, 6),

    'KB1': (7, 1, 0), 'KB2': (12, 1, 0), 'KB3': (6, 1, 0), 'KB4': (14, 1, 0),
    'KB5': (9, 1, 0), 'SKB+': (7, 1, 1),

    'LA1': (9, 4, 0), 'LA2': (8, 4, 0),

    'LL': (5, 4, 0), 'LN': (5, 3, 0),

    'LB1': (8, 3, 0), 'LB2': (14, 4, 0), 'LB3': (7, 2, 0), 'LB4': (6, 2, 0),
    'LB5': (20, 4, 0), 'LB6': (10, 4, 0), 'LB7': (17, 4, 0), 'LB15': (13, 4, 0),

    'LG1': (13, 3, 0), 'LG2': (11, 2, 0), 'LG3': (12, 2, 0),

    'MA': (16, 9, 0), 'MA1': (16, 9, 0), 'MA2': (15, 9, 0),

    'MB': (15, 8, 0),

    'MZ': (12, 9, 0), 'MZ1': (12, 9, 0), 'MZ2': (11, 8, 0),

    'MG': (14, 7, 0),

    'M2-M4': (8, 6, 0), 'M2-N1': (10, 6, 0), 'M2-N4': (13, 6, 0),
    'M3-M5': (9, 7, 0), 'M3-N1': (10, 7, 0), 'M5-O3': (21, 7, 0),
    'M1-N2': (11, 5, 0), 'M1-N3': (12, 5, 0), 'M3-N4': (13, 7, 0),
    'M2-O4': (20, 6, 0), 'M4-O2': (18, 8, 0)

    }

def extract(infile, outfile):
    writer = csv.writer(outfile)

    # Header
    writer.writerow(['z', 'src', 'dest', 'satellite',
                     'probability', 'transition energy (in eV)'])

    # Probability and energy
    notread = set()

    for line in infile:
        line = line.strip()
        if not line: continue

        z = int(line[0:2])

        siegbahn = line[10:17].strip()
        if siegbahn.startswith('A'): # skip absorption edges
            continue
        if siegbahn not in _TRANSITION_LOOKUP: # check for equivalence
            notread.add(siegbahn)
            continue
        subshells = list(_TRANSITION_LOOKUP[siegbahn])

        probability = line[20:23].strip()
        if not probability: # skip transition with no probability
            continue

        probability = float(probability) / 100.0
        if probability > 100: # skip sum of transitions
            continue

        wavelength = float(line[26:35])
        energy = (4.13566733e-15 * 299792458) / (wavelength * 1e-10)

        writer.writerow([z] + subshells + [probability, energy])

    print('Not read transition(s): %s' % ', '.join(notread))

if __name__ == '__main__':
    infile = open('lambda.asc', 'r')
    outfile = open('/tmp/jeol.csv', 'w')

    extract(infile, outfile)

    infile.close()
    outfile.close()
