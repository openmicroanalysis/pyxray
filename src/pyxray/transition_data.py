#!/usr/bin/env python
"""
================================================================================
:mod:`relaxation_data` -- Subshell, transition and relaxation data
================================================================================

.. module:: relaxation_data
   :synopsis: ubshell, transition and relaxation data

.. inheritance-diagram:: pyxray.relaxation_data

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
from abc import ABCMeta, abstractmethod
import csv

# Third party modules.
from pkg_resources import resource_stream #@UnresolvedImport

# Local modules.

# Globals and constants variables.

class _TransitionDatabase(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def energy_eV(self, z=None, subshells=None, transition=None):
        """
        Returns the energy of a transition in eV.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number
        :arg subshells: :class:`tuple` of length 2 or 3. 
            The first and second values are respectively the source and 
            destination subshells id. They can be specified either using an
            integer between 1 and 30 or a :class:`Subshell` object.
            The third value is optional. It specifies the satellite index.
            0 indicates the main diagram line.
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        raise NotImplementedError

    @abstractmethod
    def probability(self, z=None, subshells=None, transition=None):
        """
        Returns the probability of an transition.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number
        :arg subshells: :class:`tuple` of length 2 or 3. 
            The first and second values are respectively the source and 
            destination subshells id. They can be specified either using an
            integer between 1 and 30 or a :class:`Subshell` object.
            The third value is optional. It specifies the satellite index.
            0 indicates the main diagram line.
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, z=None, subshells=None, transition=None):
        """
        Returns whether the transition exists.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number
        :arg subshells: :class:`tuple` of length 2 or 3. 
            The first and second values are respectively the source and 
            destination subshells id. They can be specified either using an
            integer between 1 and 30 or a :class:`Subshell` object.
            The third value is optional. It specifies the satellite index.
            0 indicates the main diagram line.
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        raise NotImplementedError

class _BaseTransitionDatabase(_TransitionDatabase):

    KEY_Z = 'z'
    KEY_SUBSHELL_SRC = 'src'
    KEY_SUBSHELL_DEST = 'dest'
    KEY_SUBSHELL_SATELLITE = 'satellite'
    KEY_PROBABILITY = 'probability'
    KEY_ENERGY = 'energy_eV'

    def __init__(self, fileobj):
        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.DictReader(fileobj)

        for rowdict in reader:
            z = int(rowdict[self.KEY_Z])

            src = int(rowdict[self.KEY_SUBSHELL_SRC])
            dest = int(rowdict[self.KEY_SUBSHELL_DEST])
            satellite = int(rowdict.get(self.KEY_SUBSHELL_SATELLITE, 0))

            probability = float(rowdict[self.KEY_PROBABILITY])
            energy_eV = float(rowdict[self.KEY_ENERGY])

            data.setdefault(z, {})
            data[z].setdefault(src, {})
            data[z][src].setdefault(dest, {})
            data[z][src][dest].setdefault(satellite, {})

            data[z][src][dest][satellite][self.KEY_ENERGY] = energy_eV

            if probability >= 0:
                data[z][src][dest][satellite][self.KEY_PROBABILITY] = probability

        return data

    def _get_datum(self, z=None, subshells=None, transition=None):
        if z is None:
            z = transition.z

        if not z in self.data:
            raise ValueError, "No relaxation data for atomic number %i." % z

        if subshells is None:
            subshells = transition.src, transition.dest, transition.satellite

        src = subshells[0]
        if hasattr(src, 'index'):
            src = src.index

        dest = subshells[1]
        if hasattr(dest, 'index'):
            dest = dest.index

        satellite = subshells[2] if len(subshells) == 3 else 0

        return self.data[z][src][dest][satellite]

    def _get_value(self, key, z=None, subshells=None, transition=None):
        try:
            return self._get_datum(z, subshells, transition)[key]
        except KeyError:
            return 0.0

    def energy_eV(self, z=None, subshells=None, transition=None):
        return self._get_value(self.KEY_ENERGY, z, subshells, transition)

    def probability(self, z=None, subshells=None, transition=None):
        return self._get_value(self.KEY_PROBABILITY, z, subshells, transition)

    def exists(self, z=None, subshells=None, transition=None):
        try:
            self._get_datum(z, subshells, transition)
            return True
        except KeyError:
            return False

class PENELOPETransitionDatabaseMod(_BaseTransitionDatabase):
    
    """
    Relaxation data for singly-ionised atoms.
    
    The relaxation data should be comma-separated with the following
    columns: atomic number, destination shell, source shell, transition
    probability and transition energy (in eV). 
        
    The relaxation data is taken from PENELOPE 2011, where the transition 
    probabilities and energies were extracted from the LLNL Evaluated 
    Atomic Data Library (Perkins et al. 1991). 
    Some energies values were replaced by more accurate, when available.
    Energies of x rays from K- and L-shell transitions were taken from 
    Deslattes et al. (2004). 
    The energies of characteristic M lines are from Bearden's (1967) review.
    The energies for Lithium, Beryllium and Boron were taken from the
    DTSA database.
    However, no probabilities are available for these elements.
    """

    def __init__(self):
        fileobj = resource_stream(__name__, 'data/penelope_mod_transition_data.csv')
        _BaseTransitionDatabase.__init__(self, fileobj)

# Utility functions at module level.
# Basically delegate everything to the instance object.
#---------------------------------------------------------------------------

instance = PENELOPETransitionDatabaseMod()

def get_instance():
    return instance

def set_instance(inst):
    global instance
    instance = inst

def energy_eV(z=None, subshells=None, transition=None):
    """
    Returns the energy of a transition in eV.
    One can either specified the atomic number and subshells or an atomic
    transition object.
    
    :arg z: atomic number
    :arg subshells: :class:`tuple` of length 2 or 3. 
            The first and second values are respectively the source and 
            destination subshells id. They can be specified either using an
            integer between 1 and 30 or a :class:`Subshell` object.
            The third value is optional. It specifies the satellite index.
            0 indicates the main diagram line.
    :arg transition: atomic transition
    :type transition: :class:`.Transition`
    """
    return instance.energy_eV(z, subshells, transition)

def probability(z=None, subshells=None, transition=None):
    """
    Returns the probability of an transition.
    One can either specified the atomic number and subshells or an atomic
    transition object.
    
    :arg z: atomic number
    :arg subshells: :class:`tuple` of length 2 or 3. 
            The first and second values are respectively the source and 
            destination subshells id. They can be specified either using an
            integer between 1 and 30 or a :class:`Subshell` object.
            The third value is optional. It specifies the satellite index.
            0 indicates the main diagram line.
    :arg transition: atomic transition
    :type transition: :class:`.Transition`
    """
    return instance.probability(z, subshells, transition)

def exists(z=None, subshells=None, transition=None):
    """
    Returns whether the transition exists.
    One can either specified the atomic number and subshells or an atomic
    transition object.
    
    :arg z: atomic number
    :arg subshells: :class:`tuple` of length 2 or 3. 
            The first and second values are respectively the source and 
            destination subshells id. They can be specified either using an
            integer between 1 and 30 or a :class:`Subshell` object.
            The third value is optional. It specifies the satellite index.
            0 indicates the main diagram line.
    :arg transition: atomic transition
    :type transition: :class:`.Transition`
    """
    return instance.exists(z, subshells, transition)
