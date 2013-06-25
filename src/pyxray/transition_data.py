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
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30) or 
            two :class:`Subshell` objects
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
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30) or 
            two :class:`Subshell` objects
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
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30) or 
            two :class:`Subshell` objects
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        raise NotImplementedError

class PENELOPETransitionDatabaseMod(_TransitionDatabase):
    
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

    KEY_PROBABILITY = 'probability'
    KEY_ENERGY = 'energy'

    def __init__(self, fileobj=None):
        fileobj = resource_stream(__name__, 'data/penelope_mod_transition_data.csv')
        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)
        reader.next() # skip header

        for row in reader:
            z = int(row[0])
            subshell_dest = int(row[1])
            subshell_src = int(row[2])

            probability = float(row[3])
            energy_eV = float(row[4])

            data.setdefault(z, {})
            data[z].setdefault(subshell_src, {})
            data[z][subshell_src].setdefault(subshell_dest, {})

            data[z][subshell_src][subshell_dest][self.KEY_ENERGY] = energy_eV

            if probability >= 0:
                data[z][subshell_src][subshell_dest][self.KEY_PROBABILITY] = probability

        return data

    def _get_value(self, key, z=None, subshells=None, transition=None):
        if z is None:
            z = transition.z
        if subshells is None:
            subshells = transition.src, transition.dest

        if not z in self.data:
            raise ValueError, "No relaxation data for atomic number %i." % z
        
        srcshell = subshells[0]
        if hasattr(srcshell, 'index'):
            srcshell = srcshell.index

        destshell = subshells[1]
        if hasattr(destshell, 'index'):
            destshell = destshell.index

        try:
            return self.data[z][srcshell][destshell][key]
        except KeyError:
            return 0.0

    def energy_eV(self, z=None, subshells=None, transition=None):
        """
        Returns the energy of a transition in eV.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (3 to 99)
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        return self._get_value(self.KEY_ENERGY, z, subshells, transition)

    def probability(self, z=None, subshells=None, transition=None):
        """
        Returns the probability of an transition.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (6 to 99)
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        return self._get_value(self.KEY_PROBABILITY, z, subshells, transition)

    def exists(self, z=None, subshells=None, transition=None):
        """
        Returns whether the transition exists.
        One can either specified the atomic number and subshells or an atomic
        transition object.
        
        :arg z: atomic number (6 to 99)
        :arg subshells: :class:`tuple` of length 2 of the source and 
            destination subshells id (between 1 and 30)
        :arg transition: atomic transition
        :type transition: :class:`.Transition`
        """
        if z is None:
            z = transition.z
        if subshells is None:
            subshells = transition.src, transition.dest

        srcshell = subshells[0]
        if hasattr(srcshell, 'index'):
            srcshell = srcshell.index

        destshell = subshells[1]
        if hasattr(destshell, 'index'):
            destshell = destshell.index

        try:
            self.data[z][srcshell][destshell]
            return True
        except KeyError:
            return False

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
    :arg subshells: :class:`tuple` of length 2 of the source and 
        destination subshells id (between 1 and 30) or 
        two :class:`Subshell` objects
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
    :arg subshells: :class:`tuple` of length 2 of the source and 
        destination subshells id (between 1 and 30) or 
        two :class:`Subshell` objects
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
    :arg subshells: :class:`tuple` of length 2 of the source and 
        destination subshells id (between 1 and 30) or 
        two :class:`Subshell` objects
    :arg transition: atomic transition
    :type transition: :class:`.Transition`
    """
    return instance.exists(z, subshells, transition)
