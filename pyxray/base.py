"""
Base database
"""

# Standard library modules.
import abc
import sys
import operator

# Third party modules.
import tabulate

# Local modules.
from pyxray.cbook import formatdoc
import pyxray.descriptor as descriptor

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
            azimuthal quantum number, and total angular momentum_nominator
            * any notation (case insensitive)""",

            'xray_transition': """:arg xray_transition: either
            * :class:`XrayTransition <pyxray.descriptor.XrayTransition>` object
            * a :class:`tuple` of source and destination subshells
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

class _DatabaseMixin(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_preferred_references(self):
        """
        Return the BibTeX keys of the preferred references.

        If no reference is specified when calling a method, the value for the first preferred reference is returned.
        If no preferred reference, the first value is returned.

        :return: preferred references
        :rtype: :class:`tuple`
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def add_preferred_reference(self, reference):
        """
        Adds a preferred reference.

        :arg reference: :class:`Reference` or its BibTeX key

        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    def clear_preferred_references(self):
        """
        Clear all added preferred references.
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element(self, element): #pragma: no cover
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
    def element_atomic_number(self, element): #pragma: no cover
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
    def element_symbol(self, element, reference=None): #pragma: no cover
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
    def element_name(self, element, language='en', reference=None): #pragma: no cover
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
    def element_atomic_weight(self, element, reference=None): #pragma: no cover
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
    def element_mass_density_kg_per_m3(self, element, reference=None): #pragma: no cover
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
    def element_mass_density_g_per_cm3(self, element, reference=None): #pragma: no cover
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
    def element_xray_transition(self, element, xray_transition, reference=None): #pragma: no cover
        """
        Returns X-ray transition descriptor if x-ray transition has a
        probability greater than 0 for that element.

        {element}
        {xray_transition}
        {reference}

        :return: X-ray transition descriptor
        :rtype: :class:`XrayTransition`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def element_xray_transitions(self, element, xray_transition=None, reference=None): #pragma: no cover
        """
        Returns all x-ray transitions which have a probability greater than 0 for that element.
        If *xray_transition* is not ``None``, only the x-ray transitions matching this x-ray transition are returned.

        {element}
        {xray_transition}
        {reference}

        :return: X-ray transitions
        :rtype: :class:`tuple` of :class:`XrayTransition`
        {exception}
        """
        raise NotImplementedError

    @formatdoc(**_docextras)
    def print_element_xray_transitions(self, element, file=sys.stdout, tabulate_kwargs=None):
        """
        Prints all x-ray transitions for an element, with their different
        notations and energy.

        {element}

        :arg file: file for output, default to standard out
        """
        header = ['IUPAC', 'Siegbahn', 'Energy (eV)', 'Probability']

        rows = []
        for xray_transition in self.element_xray_transitions(element):
            try:
                iupac = self.xray_transition_notation(xray_transition, 'iupac')
            except:
                iupac = ''

            try:
                siegbahn = self.xray_transition_notation(xray_transition, 'siegbahn')
            except:
                siegbahn = ''

            try:
                energy_eV = self.xray_transition_energy_eV(element, xray_transition)
            except:
                energy_eV = ''

            try:
                probability = self.xray_transition_probability(element, xray_transition)
            except:
                probability = ''

            rows.append([iupac, siegbahn, energy_eV, probability])

        rows.sort(key=operator.itemgetter(2))

        if tabulate_kwargs is None:
            tabulate_kwargs = {}
        file.write(tabulate.tabulate(rows, header, **tabulate_kwargs))

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def atomic_shell(self, atomic_shell): #pragma: no cover
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
    def atomic_shell_notation(self, atomic_shell, notation, encoding='utf16', reference=None): #pragma: no cover
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
    def atomic_subshell(self, atomic_subshell): #pragma: no cover
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
    def atomic_subshell_notation(self, atomic_subshell, notation, encoding='utf16', reference=None): #pragma: no cover
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
    def atomic_subshell_binding_energy_eV(self, element, atomic_subshell, reference=None): #pragma: no cover
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
    def atomic_subshell_radiative_width_eV(self, element, atomic_subshell, reference=None): #pragma: no cover
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
    def atomic_subshell_nonradiative_width_eV(self, element, atomic_subshell, reference=None): #pragma: no cover
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
    def atomic_subshell_occupancy(self, element, atomic_subshell, reference=None): #pragma: no cover
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
    def xray_transition(self, xray_transition): #pragma: no cover
        """
        Returns x-ray transition descriptor.

        {xray_transition}

        :return: x-ray transition descriptor
        :rtype: :class:`XrayTransition`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def xray_transition_notation(self, xray_transition, notation, encoding='utf16', reference=None): #pragma: no cover
        """
        Returns notation of an x-ray transition.

        {xray_transition}
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
    def xray_transition_energy_eV(self, element, xray_transition, reference=None): #pragma: no cover
        """
        Returns energy of an element and X-ray transition (in eV).

        {element}
        {xray_transition}
        {reference}

        :return: energy (in eV)
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def xray_transition_probability(self, element, xray_transition, reference=None): #pragma: no cover
        """
        Returns probability of an element and X-ray transition.

        {element}
        {xray_transition}
        {reference}

        :return: probability
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @abc.abstractmethod
    @formatdoc(**_docextras)
    def xray_transition_relative_weight(self, element, xray_transition, reference=None): #pragma: no cover
        """
        Returns relative weight of an element and X-ray transition.

        {element}
        {xray_transition}
        {reference}

        :return: relative weight
        :rtype: :class:`float`
        {exception}
        """
        raise NotImplementedError

    @formatdoc(**_docextras)
    def xray_line(self, element, xray_transition):
        """
        Returns x-ray line descriptor.

        {element}
        {xray_transition}

        :return: x-ray line
        :rtype: :class:`XrayLine`
        {exception}
        """
        element = self.element(element)
        symbol = self.element_symbol(element)

        transition = self.xray_transition(xray_transition)

        iupac = '{} {}'.format(symbol, self.xray_transition_notation(transition, 'iupac', 'utf16'))

        try:
            siegbahn = '{} {}'.format(symbol, self.xray_transition_notation(transition, 'siegbahn', 'utf16'))
        except:
            siegbahn = iupac

        try:
            energy_eV = self.xray_transition_energy_eV(element, transition)
        except NotFound:
            energy_eV = None

        try:
            probability = self.xray_transition_probability(element, transition)
        except NotFound:
            probability = None

        try:
            relative_weight = self.xray_transition_relative_weight(element, transition)
        except NotFound:
            relative_weight = None

        return descriptor.XrayLine(element, transition, iupac, siegbahn, energy_eV, probability, relative_weight)
