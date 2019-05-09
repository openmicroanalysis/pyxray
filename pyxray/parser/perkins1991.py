#!/usr/bin/env python
"""
Parser for the Evaluated Atomic Data Library (EADL)
"""

# Standard library modules.
import os
import re
import logging

# Third party modules.
import requests

try:
    import requests_cache
    dirpath = os.path.join(os.path.dirname(__file__), '..', 'data', 'cache')
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, 'eadl')
    requests_cache.install_cache(filepath)
except ImportError:
    pass

# Local modules.
from pyxray.descriptor import Reference, Element, AtomicSubshell, XrayTransition
from pyxray.property import \
    (ElementAtomicWeight,
     AtomicSubshellBindingEnergy,
     AtomicSubshellRadiativeWidth, AtomicSubshellNonRadiativeWidth,
     AtomicSubshellOccupancy,
     XrayTransitionEnergy, XrayTransitionProbability)
import pyxray.parser.base as base

# Globals and constants variables.
logger = logging.getLogger(__name__)

PERKINS1991 = Reference('perkins1991',
                        author='Perkins, S.T. and Cullen, D.E.',
                        title='Tables and Graphs of Atomic Subshell and Relaxation Data Derived from the LLNL Evaluated Atomic Data Library (EADL), Z = 1 - 100',
                        organization='Lawrence Livermore National Laboratory',
                        year=1991,
                        volume=30)

EADL_URL = 'https://www-nds.iaea.org/epdl97/data/endl/eadl/eadl.all'

FLOAT_PATTERN = re.compile(r'([\d.]+)([\+\-])([\d ]+)')

def float_(text):
    text = text.strip()
    base, sign, exp = FLOAT_PATTERN.match(text).groups()
    base = float(base)
    exp = float(exp) if sign == '+' else -float(exp)
    return base * 10 ** exp

# Conversion from EADL to AtomicSubshell descriptor
ATOMIC_SUBSHELLS = {
    # K
    1: base.K,

    # L
    3: base.L1,
    5: base.L2,
    6: base.L3,

    # M
    8: base.M1,
    10: base.M2,
    11: base.M3,
    13: base.M4,
    14: base.M5,

    # N
    16: base.N1,
    18: base.N2,
    19: base.N3,
    21: base.N4,
    22: base.N5,
    24: base.N6,
    25: base.N7,

    # O
    27: base.O1,
    29: base.O2,
    30: base.O3,
    32: base.O4,
    33: base.O5,
    35: base.O6,
    36: base.O7,
    38: base.O8,
    39: base.O9,

    # P
    41: base.P1,
    43: base.P2,
    44: base.P3,
    46: base.P4,
    47: base.P5,
    49: base.P6,
    50: base.P7,
    52: base.P8,
    53: base.P9,
    55: base.P10,
    56: base.P11,

    # Q
    58: base.Q1,
    60: base.Q2,
    61: base.Q3,
    }

# C
REACTION_DESCRIPTOR_SUBSHELL = 91
REACTION_DESCRIPTOR_TRANSITION = 92

# I
REACTION_PROPERTY_NUMBER_ELECTRON = 912
REACTION_PROPERTY_BINDING_ENERGY = 913
REACTION_PROPERTY_RADIATIVE_WIDTH = 921
REACTION_PROPERTY_NONRADIATIVE_WIDTH = 922
REACTION_PROPERTY_RADIATIVE_PROBABILITY = 931
REACTION_PROPERTY_NONRADIATIVE_PROBABILITY = 932

# S
REACTION_MODIFIER_NONE = 0
REACTION_MODIFIER_EXTRA = 91

# Yo
OUTGOING_PARTICLE_NONE = 0
OUTGOING_PARTICLE_PHOTON = 7
OUTGOING_PARTICLE_ELECTRON = 9

SEPERATOR = '                                                                       1'

MAX_Z = 100

class Perkins1991Parser(base._Parser):

    def __iter__(self):
        r = requests.get(EADL_URL, stream=True, verify=False)

        try:
            rows = []
            for line in r.iter_lines():
                line = line.decode('ascii')

                if line == SEPERATOR:
                    yield from self._iter_rows(rows)

                    element = self._extract_element(rows)
                    self.update(int(element.z / MAX_Z * 100.0))

                    rows = []
                    continue

                rows.append(line)

        finally:
            r.close()

    def _iter_rows(self, rows):
        yield from self._parse_atomic_weight(rows)
        yield from self._parse_atomic_subshell_binding_energy(rows)
        yield from self._parse_atomic_subshell_radiative_width(rows)
#        yield from self._parse_atomic_subshell_nonradiative_width(rows)
        yield from self._parse_atomic_subshell_occupaqncy(rows)
        yield from self._parse_radiative_transition(rows)
#        yield from self._parse_nonradiative_transition(rows)

    def _extract_element(self, rows):
        return Element(int(rows[0][0:3]))

    def _extract_reaction_descriptor(self, rows):
        return int(rows[1][0:2])

    def _extract_reaction_modifier(self, rows):
        return int(rows[1][5:8])

    def _extract_reaction_property(self, rows):
        return int(rows[1][2:5])

    def _extract_outgoing_particle(self, rows):
        return int(rows[0][10:12])

    def _extract_source_subshell(self, rows):
        return ATOMIC_SUBSHELLS[int(float_(rows[0][0:11]))]

    def _extract_secondary_destination_subshell(self, rows):
        return ATOMIC_SUBSHELLS[int(float_(rows[0][11:22]))]

    def _extract_destination_subshell(self, rows):
        return ATOMIC_SUBSHELLS[int(float_(rows[1][21:32]))]

    def _parse_atomic_weight(self, rows):
        # Note: Fake descriptor and property. Selected just in order to only
        # have one entry for the atomic weight
        reaction_descriptor = self._extract_reaction_descriptor(rows)
        if reaction_descriptor != REACTION_DESCRIPTOR_SUBSHELL:
            return

        reaction_property = self._extract_reaction_property(rows)
        if reaction_property != REACTION_PROPERTY_NUMBER_ELECTRON:
            return

        element = self._extract_element(rows)
        value = float_(rows[0][13:24])
        prop = ElementAtomicWeight(PERKINS1991, element, value)
        logger.debug('Parsed: {0}'.format(prop))
        yield prop

    def _parse_atomic_subshell_binding_energy(self, rows):
        reaction_descriptor = self._extract_reaction_descriptor(rows)
        if reaction_descriptor != REACTION_DESCRIPTOR_SUBSHELL:
            return

        reaction_modifier = self._extract_reaction_modifier(rows)
        if reaction_modifier != REACTION_MODIFIER_NONE:
            return

        outgoing_particle = self._extract_outgoing_particle(rows)
        if outgoing_particle != OUTGOING_PARTICLE_NONE:
            return

        reaction_property = self._extract_reaction_property(rows)
        if reaction_property != REACTION_PROPERTY_BINDING_ENERGY:
            return

        element = self._extract_element(rows)

        for row in rows[2:]:
            atomic_subshell = self._extract_source_subshell([row])
            value_eV = float_(row[11:22]) * 1e6
            prop = AtomicSubshellBindingEnergy(PERKINS1991, element,
                                               atomic_subshell, value_eV)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

    def _parse_atomic_subshell_radiative_width(self, rows):
        reaction_descriptor = self._extract_reaction_descriptor(rows)
        if reaction_descriptor != REACTION_DESCRIPTOR_SUBSHELL:
            return

        reaction_modifier = self._extract_reaction_modifier(rows)
        if reaction_modifier != REACTION_MODIFIER_NONE:
            return

        outgoing_particle = self._extract_outgoing_particle(rows)
        if outgoing_particle != OUTGOING_PARTICLE_NONE:
            return

        reaction_property = self._extract_reaction_property(rows)
        if reaction_property != REACTION_PROPERTY_RADIATIVE_WIDTH:
            return

        element = self._extract_element(rows)

        for row in rows[2:]:
            atomic_subshell = self._extract_source_subshell([row])
            value_eV = float_(row[11:22]) * 1e6
            prop = AtomicSubshellRadiativeWidth(PERKINS1991, element,
                                                atomic_subshell, value_eV)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

    def _parse_atomic_subshell_nonradiative_width(self, rows):
        reaction_descriptor = self._extract_reaction_descriptor(rows)
        if reaction_descriptor != REACTION_DESCRIPTOR_SUBSHELL:
            return

        reaction_modifier = self._extract_reaction_modifier(rows)
        if reaction_modifier != REACTION_MODIFIER_NONE:
            return

        outgoing_particle = self._extract_outgoing_particle(rows)
        if outgoing_particle != OUTGOING_PARTICLE_NONE:
            return

        reaction_property = self._extract_reaction_property(rows)
        if reaction_property != REACTION_PROPERTY_NONRADIATIVE_WIDTH:
            return

        element = self._extract_element(rows)

        for row in rows[2:]:
            atomic_subshell = self._extract_source_subshell([row])
            value_eV = float_(row[11:22]) * 1e6
            prop = AtomicSubshellNonRadiativeWidth(PERKINS1991, element,
                                                   atomic_subshell, value_eV)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

    def _parse_atomic_subshell_occupaqncy(self, rows):
        reaction_descriptor = self._extract_reaction_descriptor(rows)
        if reaction_descriptor != REACTION_DESCRIPTOR_SUBSHELL:
            return

        reaction_modifier = self._extract_reaction_modifier(rows)
        if reaction_modifier != REACTION_MODIFIER_NONE:
            return

        outgoing_particle = self._extract_outgoing_particle(rows)
        if outgoing_particle != OUTGOING_PARTICLE_NONE:
            return

        reaction_property = self._extract_reaction_property(rows)
        if reaction_property != REACTION_PROPERTY_NUMBER_ELECTRON:
            return

        element = self._extract_element(rows)

        for row in rows[2:]:
            atomic_subshell = self._extract_source_subshell([row])
            value = int(float_(row[11:22]))
            prop = AtomicSubshellOccupancy(PERKINS1991, element,
                                           atomic_subshell, value)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

    def _parse_radiative_transition(self, rows):
        reaction_descriptor = self._extract_reaction_descriptor(rows)
        if reaction_descriptor != REACTION_DESCRIPTOR_TRANSITION:
            return

        reaction_modifier = self._extract_reaction_modifier(rows)
        if reaction_modifier != REACTION_MODIFIER_EXTRA:
            return

        outgoing_particle = self._extract_outgoing_particle(rows)
        if outgoing_particle != OUTGOING_PARTICLE_PHOTON:
            return

        reaction_property = self._extract_reaction_property(rows)
        if reaction_property != REACTION_PROPERTY_RADIATIVE_PROBABILITY:
            return

        element = self._extract_element(rows)

        destination_subshell = self._extract_destination_subshell(rows)

        for row in rows[2:]:
            source_subshell = self._extract_source_subshell([row])
            transition = XrayTransition(source_subshell, destination_subshell)

            value = float_(row[11:22])
            prop = XrayTransitionProbability(PERKINS1991, element, transition, value)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

            value_eV = float_(row[22:33]) * 1e6
            prop = XrayTransitionEnergy(PERKINS1991, element, transition, value_eV)
            logger.debug('Parsed: {0}'.format(prop))
            yield prop

#    def _parse_nonradiative_transition(self, rows):
#        reaction_descriptor = self._extract_reaction_descriptor(rows)
#        if reaction_descriptor != REACTION_DESCRIPTOR_TRANSITION:
#            return
#
#        reaction_modifier = self._extract_reaction_modifier(rows)
#        if reaction_modifier != REACTION_MODIFIER_EXTRA:
#            return
#
#        outgoing_particle = self._extract_outgoing_particle(rows)
#        if outgoing_particle != OUTGOING_PARTICLE_ELECTRON:
#            return
#
#        reaction_property = self._extract_reaction_property(rows)
#        if reaction_property != REACTION_PROPERTY_NONRADIATIVE_PROBABILITY:
#            return
#
#        element = self._extract_element(rows)
#
#        destination_subshell = self._extract_destination_subshell(rows)
#
#        for row in rows[2:]:
#            source_subshell = self._extract_source_subshell([row])
#            secondary_destination_subshell = \
#                self._extract_secondary_destination_subshell([row])
#            transition = Transition(source_subshell, destination_subshell,
#                                    secondary_destination_subshell)
#
#            value = float_(row[22:33])
#            prop = TransitionProbability(PERKINS1991, element, transition, value)
#            logger.debug('Parsed: {0}'.format(prop))
#            yield prop
#
#            value_eV = float_(row[33:44]) * 1e6
#            prop = TransitionEnergy(PERKINS1991, element, transition, value_eV)
#            logger.debug('Parsed: {0}'.format(prop))
#            yield prop
