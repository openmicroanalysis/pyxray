"""
Base database
"""

# Standard library modules.
import abc

# Third party modules.

# Local modules.
from pyxray.cbook import formatdoc

# Globals and constants variables.

class NotFound(Exception):
    pass

_docextras = {'element': """:arg element: either
            * :class:`Element <pyxray.descriptor.Element>` object
            * atomic number
            * symbol (case insensitive)
            * name (in any language, case insensitive)
            * object with attribute :attr:`atomic_number` or :attr:`z`""",

            'atomic_shell': """:arg atomic_shell: either
            * :class:`AtomicShell <pyxray.descriptor.AtomicShell>` object
            * principal quantum number
            * any notation (case insensitive)""",

            'atomic_subshell': """:arg atomic_subshell: either
            * :class:`AtomicSubshell <pyxray.descriptor.AtomicSubshell>` object
            * a :class:`tuple` of principal quantum number, 
                azimuthal quantum number and total angular momentum_nominator
            * any notation (case insensitive)""",

            'transition': """:arg transition: either
            * :class:`Transition <pyxray.descriptor.Transition>` object
            * a :class:`tuple` of source and destination subshells 
                (or optionally secondary destination subshells)
            * any notation (case insensitive)""",

            'transitionset': """:arg transitionset: either
            * :class:`TransitionSet <pyxray.descriptor.TransitionSet>` object
            * a :class:`tuple` of transitions
            * any notation (case insensitive)""",

            'language': """:arg language: language code (e.g. ``en``, ``fr``, ``de``)""",

            'notation': """:arg notation: name of a notation (case insensitive), 
                ``iupac``, ``siegbahn`` and ``orbital`` are usually supported""",

            'encoding': """:arg encoding: type of encoding, either 
                ``ascii``, ``utf16``, ``html`` or ``latex``""",

            'reference': """:arg reference: reference to use to retrieve this value, either
            * :class:`Reference <pyxray.descriptor.Reference>` object
            * BibTeX key of a reference
            * ``None``, the default reference will be used or the first reference found""",

            'exception': """:raise NotFound:""",
}

class _Database(object, metaclass=abc.ABCMeta):

    def __init__(self):
        self._default_references = {}
        self._available_methods = set()
        for attr in self.__class__.__dict__:
            if attr.startswith('_'): continue
            self._available_methods.add(attr)

    def set_default_reference(self, method, reference):
        """
        Set the default reference for a method. 
        
        :arg method: name of a method
        :type method: :class:`str`
        
        {reference}
        """
        if method not in self._available_methods:
            raise ValueError('Unknown method: {0}'.format(method))
        self._default_references[method] = reference

    def get_default_reference(self, method):
        """
        Returns the default reference for a method. 
        
        :arg method: name of a method
        :type method: :class:`str`
        
        :return: reference
        :rtype: :class:`Reference <pyxray.descriptor.Reference>` or :class:`str`
        """
        if method not in self._available_methods:
            raise ValueError('Unknown method: {0}'.format(method))
        return self._default_references.get(method)

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element(self, element):
        """
        Returns element descriptor.

        {element}
        
        :return: element descriptor
        :rtype: :class:`Element`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_atomic_number(self, element):
        """
        Returns atomic number of an element.

        {element}
        
        :return: atomic number
        :rtype: :class:`int`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_symbol(self, element, reference=None):
        """
        Returns symbol of an element.

        {element}
        {reference}
        
        :return: symbol
        :rtype: :class:`str`
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_name(self, element, language='en', reference=None):
        """
        Returns full name of an element, in the language specified.

        {element}
        {language}
        {reference}
            
        :return: name
        :rtype: :class:`str`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_atomic_weight(self, element, reference=None):
        """
        Returns atomic weight of an element.
        The atomic weight is defined by the CIAAW as it is the ratio of 
        the average atomic mass of an element over 1/12 of the mass of the 
        carbon-12 atom.
        
        {element}
        {reference}
            
        :return: atomic weight
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_mass_density_kg_per_m3(self, element, reference=None):
        """
        Returns mass density (in kg/m3) of an element.

        {element}
        {reference}
        
        :return: mass density (in kg/m3)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @formatdoc(**_docextras)
    def element_mass_density_g_per_cm3(self, element, reference=None):
        """
        Returns mass density (in g/cm3) of an element.
        
        {element}
        {reference}
            
        :return: mass density (in g/cm3)
        :rtype: :class:`float`
        {exception}
        """
        return self.element_mass_density_kg_per_m3(element, reference) / 1e3

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_transitions(self, element, reference=None):
        """
        Returns all transitions which have a probability greater than 0 for an element.

        {element}
        {reference}
        
        :return: transitions
        :rtype: :class:`tuple` of :class:`Transition`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_shell(self, atomic_shell):
        """
        Returns atomic shell descriptor.
        
        {atomic_shell}
        
        :return: atomic shell descriptor
        :rtype: :class:`AtomicShell`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_shell_notation(self, atomic_shell, notation, encoding='utf16', reference=None):
        """
        Returns notation of an atomic shell.
        
        {atomic_shell}
        {notation}
        {encoding}
        {reference}
        
        :return: notation
        :rtype: :class:`str`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_subshell(self, atomic_subshell):
        """
        Returns atomic subshell descriptor.
        
        {atomic_subshell}
        
        :return: atomic subshell descriptor
        :rtype: :class:`AtomicSubshell`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_subshell_notation(self, atomic_subshell, notation, encoding='utf16', reference=None):
        """
        Returns notation of an atomic subshell.
        
        {atomic_subshell}
        {notation}
        {encoding}
        {reference}
        
        :return: notation
        :rtype: :class:`str`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None):
        """
        Returns binding energy of an element and atomic subshell (in eV).
        
        {element}
        {atomic_subshell}
        {reference}
        
        :return: binding energy (in eV)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None):
        """
        Returns radiative width of an element and atomic subshell (in eV).
        
        {element}
        {atomic_subshell}
        {reference}
        
        :return: radiative width (in eV)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None):
        """
        Returns nonradiative width of an element and atomic subshell (in eV).
        
        {element}
        {atomic_subshell}
        {reference}
        
        :return: nonradiative width (in eV)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None):
        """
        Returns occupancy of an element and atomic subshell.
        
        {element}
        {atomic_subshell}
        {reference}
        
        :return: occupancy
        :rtype: :class:`int`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transition(self, transition):
        """
        Returns transition descriptor.
        
        {transition}
        
        :return: transition descriptor
        :rtype: :class:`Transition`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transition_notation(self, transition, notation, encoding='utf16', reference=None):
        """
        Returns notation of a transition.
        
        {transition}
        {notation}
        {encoding}
        {reference}
        
        :return: notation
        :rtype: :class:`str`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transition_energy_eV(self, element, transition, reference=None):
        """
        Returns energy of an element and transition (in eV).
        
        {element}
        {transition}
        {reference}
        
        :return: energy (in eV)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transition_probability(self, element, transition, reference=None):
        """
        Returns probability of an element and transition.
        
        {element}
        {transition}
        {reference}
        
        :return: probability
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transition_relative_weight(self, element, transition, reference=None):
        """
        Returns relative weight of an element and transition.
        
        {element}
        {transition}
        {reference}
        
        :return: relative weight
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transitionset(self, transitionset):
        """
        Returns transition set descriptor.
        
        {transitionset}
        
        :return: transition set descriptor
        :rtype: :class:`TransitionSet`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transitionset_notation(self, transitionset, notation, encoding='utf16', reference=None):
        """
        Returns notation of a transition set.
        
        {transitionset}
        {notation}
        {encoding}
        {reference}
        
        :return: notation
        :rtype: :class:`str`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transitionset_energy_eV(self, element, transitionset, reference=None):
        """
        Returns energy of an element and transition set (in eV).
        
        {element}
        {transitionset}
        {reference}
        
        :return: energy (in eV)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def transitionset_relative_weight(self, element, transitionset, reference=None):
        """
        Returns relative weight of an element and transition set.
        
        {element}
        {transitionset}
        {reference}
        
        :return: relative weight
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

