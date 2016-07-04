"""
Base database
"""

# Standard library modules.
import abc

# Third party modules.
import six

# Local modules.

# Globals and constants variables.

@six.add_metaclass(abc.ABCMeta)
class _Database(object):

    def __init__(self):
        self.reference_priority = []

    @property
    def reference_priority(self):
        """
        Returns the preferable references to use, in decreasing order of priority.
        
        :rtype: :class:`list` of reference keys
        """
        return list(self._reference_priority)

    @reference_priority.setter
    def reference_priority(self, references):
        """
        Sets the preferable references to use, in decreasing order of priority.
        
        :arg references: :class:`list` of reference keys
        """
        self._reference_priority = list(references)

    def _get_z(self, zeq):
        """
        Returns the atomic number.
        
        :arg zeq: atomic number equivalent, accepts atomic number, symbol,
            object with :attr:`z` or :attr:`atomic_number`
            
        :rtype: :class:`int`
        """
        if isinstance(zeq, int) and zeq >= 1 and zeq <= 100:
            return zeq
        elif isinstance(zeq, six.string_types):
            return self.element_atomic_number(zeq)
        elif hasattr(zeq, 'z'):
            return zeq.z
        elif hasattr(zeq, 'atomic_number'):
            return zeq.atomic_number
        else:
            raise ValueError('Unknown object: {0}'.format(zeq))

    @abc.abstractmethod
    def element_symbol(self, z):
        """
        Returns the element's symbol.

        :arg z: atomic number
        
        :return: symbol
        """
        raise NotImplementedError

    @abc.abstractmethod
    def element_atomic_number(self, symbol):
        """
        Returns the atomic number for the specified symbol.
        This function is case insensitive.

        :arg symbol: symbol of the element (e.g. ``C``), case-insensitive
        
        :return: atomic number
        """
        raise NotImplementedError

    @abc.abstractmethod
    def element_name(self, zeq, language='en', reference=None):
        """
        Returns the full name of an element, in the language specified, and
        its reference.

        :arg symbol: symbol of the element (e.g. ``C``)
        :arg language: language to be returned (e.g. ``en``)
        :arg reference: key of the reference to use to retrieve this value.
            If ``None``, the reference is selected from the reference priority
            (see :attr:`reference_priority`) or from the first listed reference
            in the database.
            
        :return: name and reference key
        """
        raise NotImplementedError

    @abc.abstractmethod
    def element_atomic_weight(self, zeq, reference=None):
        """
        Returns the atomic weight and its reference.
        The atomic weight is defined by the CIAAW as it is the ratio of 
        the average atomic mass of an element over 1/12 of the mass of the 
        carbon-12 atom.

        :arg zeq: atomic number equivalent, accepts atomic number, symbol,
            object with :attr:`z` or :attr:`atomic_number`
        :arg reference: key of the reference to use to retrieve this value.
            If ``None``, the reference is selected from the reference priority
            (see :attr:`reference_priority`) or from the first listed reference
            in the database.
            
        :return: atomic weight and reference key
        """
        raise NotImplementedError

    @abc.abstractmethod
    def element_mass_density_kg_per_m3(self, zeq, reference=None):
        """
        Returns the mass density (in kg/m3) and its reference.

        :arg zeq: atomic number equivalent, accepts atomic number, symbol,
            object with :attr:`z` or :attr:`atomic_number`
        :arg reference: key of the reference to use to retrieve this value.
            If ``None``, the reference is selected from the reference priority
            (see :attr:`reference_priority`) or from the first listed reference
            in the database.
        
        :return: mass density (in kg/m3) and reference key
        """
        raise NotImplementedError

    def element_mass_density_g_per_cm3(self, zeq, reference=None):
        """
        Returns the mass density (in g/cm3) and its reference.

        :arg zeq: atomic number equivalent, accepts atomic number, symbol,
            object with :attr:`z` or :attr:`atomic_number`
        :arg reference: key of the reference to use to retrieve this value.
            If ``None``, the reference is selected from the reference priority
            (see :attr:`reference_priority`) or from the first listed reference
            in the database.
            
        :return: mass density (in g/cm3) and reference key
        """
        return self.element_mass_density_kg_per_m3(zeq, reference) / 1e3

