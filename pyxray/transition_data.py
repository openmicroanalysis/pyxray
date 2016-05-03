"""
Subshell, transition and relaxation data
"""

# Standard library modules.
import os
import csv
from abc import ABCMeta, abstractmethod
try:
    from io import StringIO
except ImportError:
    import StringIO

# Third party modules.
import pkg_resources

# Local modules.

# Globals and constants variables.

class _TransitionDatabase(object):

    __metaclass__ = ABCMeta

    def _get_z_subshells(self, z=None, subshells=None, transition=None):
        """
        Parses the arguments and returns:

            * z
            * index of source subshell
            * index of destination subshell
            * index of satellite
        """
        if z is None:
            z = transition.z

        if subshells is None:
            subshells = transition.src, transition.dest, transition.satellite

        src = subshells[0]
        if hasattr(src, 'index'):
            src = src.index

        dest = subshells[1]
        if hasattr(dest, 'index'):
            dest = dest.index

        satellite = subshells[2] if len(subshells) == 3 else 0

        return z, src, dest, satellite

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
        z, src, dest, satellite = \
            self._get_z_subshells(z, subshells, transition)

        if not z in self.data:
            raise ValueError("No relaxation data for atomic number %i." % z)

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
        resource = os.path.join('data', 'penelope_mod_transition_data.csv')
        fileobj = pkg_resources.resource_stream('pyxray', resource) #@UndefinedVariable
        buffer = StringIO(fileobj.read().decode('ascii'))
        _BaseTransitionDatabase.__init__(self, buffer)
        fileobj.close()
        buffer.close()

class JEOLTransitionDatabase(_BaseTransitionDatabase):
    """
    Transition database from JEOL.
    File extracted from the database provided with the JEOL JXA-8530F.
    """

    def __init__(self):
        resource = os.path.join('data', 'jeol_transition_data.csv')
        fileobj = pkg_resources.resource_stream('pyxray', resource) #@UndefinedVariable
        buffer = StringIO(fileobj.read().decode('ascii'))
        _BaseTransitionDatabase.__init__(self, buffer)
        fileobj.close()
        buffer.close()

class SuperDatabase(_TransitionDatabase):

    def __init__(self):
        self.penelope = PENELOPETransitionDatabaseMod()
        self.jeol = JEOLTransitionDatabase()

    def energy_eV(self, z=None, subshells=None, transition=None):
        energy = self.penelope.energy_eV(z, subshells, transition)
        if energy > 0.0:
            return energy
        return self.jeol.energy_eV(z, subshells, transition)

    def probability(self, z=None, subshells=None, transition=None):
        probability = self.penelope.probability(z, subshells, transition)
        if probability > 0.0:
            return probability

        factor = self.jeol.probability(z, subshells, transition)

        # Convert JEOL probability using other line from PENELOPE
        z, _, dest, _ = self._get_z_subshells(z, subshells, transition)
        if dest == 1: # K
            maxsubshells = (4, 1, 0)
        elif dest in [2, 3, 4]:
            maxsubshells = (9, 4, 0)
        elif dest in [5, 6, 7, 8, 9]:
            maxsubshells = (16, 9, 0)
        else:
            return 0.0
        maxprobability = self.penelope.probability(z, maxsubshells)
        maxfactor = self.jeol.probability(z, maxsubshells)

        try:
            return factor * maxprobability / maxfactor
        except ZeroDivisionError:
            return 0.0

    def exists(self, z=None, subshells=None, transition=None):
        if self.penelope.exists(z, subshells, transition):
            return True

        if self.jeol.exists(z, subshells, transition):
            return True

        return False

# Utility functions at module level.
# Basically delegate everything to the instance object.
#---------------------------------------------------------------------------

instance = SuperDatabase()

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
