"""
Data for elements, atoms, isotopes' properties
"""

# Standard library modules.
import abc

# Third party modules.
import six

# Local modules.

# Globals and constants variables.

@six.add_metaclass(abc.ABCMeta)
class _ElementDatabase(object):

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
            return self.atomic_number(zeq)
        elif hasattr(zeq, 'z'):
            return zeq.z
        elif hasattr(zeq, 'atomic_number'):
            return zeq.atomic_number
        else:
            raise ValueError('Unknown object: {0}'.format(zeq))

    @abc.abstractmethod
    def symbol(self, z, reference='unattributed'):
        """
        Returns the element's symbol.

        :arg z: atomic number
        :arg reference: key of the reference to use to retrieve this value
        """
        raise NotImplementedError

    @abc.abstractmethod
    def atomic_number(self, symbol, reference='unattributed'):
        """
        Returns the atomic number for the specified symbol.
        This function is case insensitive.

        :arg symbol: symbol of the element (e.g. ``C``), case-insensitive
        :arg reference: key of the reference to use to retrieve this value
        """
        raise NotImplementedError

    @abc.abstractmethod
    def name(self, zeq, language='en', reference='unattributed'):
        """
        Returns the full name of an element, in the language specified.

        :arg symbol: symbol of the element (e.g. ``C``)
        :arg language: language to be returned (e.g. ``en``)
        :arg reference: key of the reference to use to retrieve this value
        """
        raise NotImplementedError

    @abc.abstractmethod
    def atomic_weight(self, zeq, ref='unattributed'):
        """
        Returns the atomic weight, defined by the CIAAW as it is the ratio of 
        the average atomic mass of an element over 1/12 of the mass of the 
        carbon-12 atom.

        :arg zeq: atomic number equivalent, accepts atomic number, symbol,
            object with :attr:`z` or :attr:`atomic_number`
        :arg reference: key of the reference to use to retrieve this value
        """
        raise NotImplementedError

    @abc.abstractmethod
    def mass_density_kg_per_m3(self, zeq, ref='unattributed'):
        """
        Returns the mass density (in kg/m3).

        :arg zeq: atomic number equivalent, accepts atomic number, symbol,
            object with :attr:`z` or :attr:`atomic_number`
        :arg reference: key of the reference to use to retrieve this value
        """
        raise NotImplementedError

