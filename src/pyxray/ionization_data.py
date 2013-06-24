#!/usr/bin/env python
"""
================================================================================
:mod:`ionization_data` -- Ionization energies of atomic subshell
================================================================================

.. module:: ionization_data
   :synopsis: Ionization energies of atomic subshell

.. inheritance-diagram:: pyxray.ionization_data

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

class _IonizationDatabase(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def energy_eV(self, z, subshell):
        """
        Returns the ionization energy of a subshell in eV.
        
        :arg z: atomic number
        :arg subshell: index of the subshells (1 to 29 inclu.) 
            or :class:`Subshell` object
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, z, subshell):
        """
        Returns whether the subshell exists.
        
        :arg z: atomic number
        :arg subshell: index of the subshells (1 to 29 inclu.) 
            or :class:`Subshell` object
        """
        raise NotImplementedError

class CarlsonIonizationDatabase(_IonizationDatabase):
    """
    Ionization energies of atomic subshell. 
    
    The relaxation data should be comma-separated with the following
    columns: atomic number, shell and ionization energy (in eV). 
        
    The ionization energies are taken from T.A. Carlson, 'Photoelectron and 
    Auger Spectroscopy' (Plenum Press, New York and London, 1975).
    """

    def __init__(self):
        fileobj = resource_stream(__name__, 'data/ionization_data.csv')
        self.data = self._read(fileobj)

    def _read(self, fileobj):
        data = {}
        reader = csv.reader(fileobj)
        reader.next() # skip header

        for row in reader:
            z = int(row[0])
            subshell = int(row[1])
            energy_eV = float(row[2])

            data.setdefault(z, {})
            data[z].setdefault(subshell, energy_eV)

        return data

    def energy_eV(self, z, subshell):
        if not z in self.data:
            raise ValueError, "No ionization energy for atomic number %i." % z

        if hasattr(subshell, 'index'):
            subshell = subshell.index

        try:
            return self.data[z][subshell]
        except KeyError:
            return 0.0

    def exists(self, z, subshell):
        if hasattr(subshell, 'index'):
            subshell = subshell.index

        try:
            self.data[z][subshell]
            return True
        except KeyError:
            return False

# Utility functions at module level.
# Basically delegate everything to the instance object.
#---------------------------------------------------------------------------

instance = CarlsonIonizationDatabase()

def get_instance():
    return instance

def set_instance(inst):
    global instance
    instance = inst

def energy_eV(z, subshell):
    """
    Returns the ionization energy of a subshell in eV.
    
    :arg z: atomic number
    :arg subshell: index of the subshells (1 to 29 inclu.)
        or :class:`Subshell` object
    """
    return instance.energy_eV(z, subshell)

def exists(z, subshell):
    """
    Returns whether the subshell exists.
    
    :arg z: atomic number
    :arg subshell: index of the subshells (1 to 29 inclu.)
        or :class:`Subshell` object
    """
    return instance.exists(z, subshell)
