######
pyxray
######

.. image:: https://img.shields.io/pypi/v/pyxray.svg
   :target: https://pypi.python.org/pypi/pyxray

.. image:: https://img.shields.io/travis/openmicroanalysis/pyxray.svg
   :target: https://travis-ci.org/openmicroanalysis/pyxray

.. image:: https://img.shields.io/codecov/c/github/openmicroanalysis/pyxray.svg
   :target: https://codecov.io/github/openmicroanalysis/pyxray

*pyxray* is a Python library that defines basic object to specify atomic 
subshells and X-ray transitions. 
The objects also provide critical information as the energy, existence and 
different notations of the X-ray transitions.

*pyxray* supports 3.x (no Python 2.x support).

The library is provided under the MIT license.

*pyxray* was partially developed as part of the doctorate thesis project of 
Philippe T. Pinard at RWTH Aachen University (Aachen, Germany) under the 
supervision of Dr. Silvia Richter, in collaboration with Hendrix Demers 
(McGill University, Canada).

Installation
============

Easiest way to install using ``pip``::

    pip install pyxray

For development installation from the git repository::

    git clone git@github.com/openmicroanalysis/pyxray.git
    cd pyxray
    pip install -e .

See development section below

Methods
=======

All methods below are accessed by importing ``pyxray``:

.. code:: python

    import pyxray

Variables of the methods are defined as follows

* ``element``: 
    either
    
    * `Element <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * atomic number
    * symbol (case insensitive)
    * name (in any language, case insensitive)
    * object with attribute ``atomic_number`` or ``z``
    
* ``atomic_shell``: 
    either
    
    * `AtomicShell <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * principal quantum number
    * any notation (case insensitive)

* ``atomic_subshell``: 
    either
    
    * `AtomicSubshell <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * a ``tuple`` of principal quantum number, azimuthal quantum number 
      and total angular momentum nominator (e.g. ``(1, 0, 1)`` for the atomic 
      subshell ``1s^{0.5}``
    * any notation (case insensitive)

* ``transition``: 
    either
    
    * `Transition <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * a ``tuple`` of source and destination subshells
      (or optionally secondary destination subshells)
    * any notation (case insensitive)

* ``transitionset``:
    either
    
    * `TransitionSet <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * a ``tuple`` of transitions
    * any notation (case insensitive)

* ``language``: 
    language code (e.g. ``en``, ``fr``, ``de``)

* ``notation``: 
    name of a notation (case insensitive),
    ``iupac``, ``siegbahn`` and ``orbital`` are usually supported
    
* ``encoding``: 
    type of encoding, either ``ascii``, ``utf16``, ``html`` or ``latex``

* ``reference``: 
    reference to use to retrieve this value, either
    
    * `Reference <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * BibTeX key of a reference
    * ``None``, the default reference will be used or the first reference found

Element properties
------------------

Properties associated with an element, defined as the ground state of an atom 
where the number of protons equal the number of electrons.

* ``pyxray.element(element)``
    Returns element descriptor.

* ``pyxray.element_atomic_number(element)``
    Returns atomic number of an element.
    
    Examples:
    
    .. code:: python
    
        pyxray.element.atomic_number('fe') #=> 26
        pyxray.element.atomic_number('Fe') #=> 26
        pyxray.element.atomic_number('iron') #=> 26
        pyxray.element.atomic_number('eisen') #=> 26

* ``pyxray.element_symbol(element, reference=None)``
    Returns symbol of an element.
    
* ``pyxray.element_name(element, language='en', reference=None)``
    Returns full name of an element, in the language specified.
    
* ``pyxray.element_atomic_weight(element, reference=None)``
    Returns atomic weight of an element. 
    The atomic weight is defined by the CIAAW as it is the ratio of 
    the average atomic mass of an element over 1/12 of the mass of the 
    carbon-12 atom.
    
* ``pyxray.element_mass_density_kg_per_m3(element, reference=None)``
    Returns mass density (in kg/m3) of an element.

* ``pyxray.element_mass_density_g_per_cm3(element, reference=None)``
    Returns mass density (in g/cm3) of an element.
    
* ``pyxray.element_transitions(element, reference=None)``
    Returns all transitions which have a probability greater than 0 for an element.

Atomic shell properties
-----------------------

Properties associated with an `atomic shell <https://en.wikipedia.org/wiki/Electron_shell>`_, 
defined by its principal quantum number.

* ``pyxray.atomic_shell(atomic_shell)``
    Returns atomic shell descriptor.

* ``pyxray.atomic_shell_notation(atomic_shell, notation, encoding='utf16', reference=None)``
    Returns notation of an atomic shell.

Atomic subshell properties
--------------------------

Properties associated with an `atomic subshell <https://en.wikipedia.org/wiki/Electron_shell#Subshells>`_,
a subdivision of atomic shells.

* ``pyxray.atomic_subshell(atomic_subshell)``
    Returns atomic subshell descriptor.

* ``pyxray.atomic_subshell_notation(atomic_subshell, notation, encoding='utf16', reference=None)``
    Returns notation of an atomic subshell.
    
    Examples:
        
    .. code:: python
    
        pyxray.atomic_subshell_notation('L3', 'iupac', 'latex') #=> 'L$_{3}$'
        pyxray.atomic_subshell_notation('L3', 'orbital') #-> '2p3/2'

* ``pyxray.atomic_subshell_binding_energy_eV(element, atomic_subshell, reference=None)``
    Returns binding energy of an element and atomic subshell (in eV).

* ``pyxray.atomic_subshell_radiative_width_eV(element, atomic_subshell, reference=None)``
    Returns radiative width of an element and atomic subshell (in eV).

* ``pyxray.atomic_subshell_nonradiative_width_eV(element, atomic_subshell, reference=None)``
    Returns nonradiative width of an element and atomic subshell (in eV).

* ``pyxray.atomic_subshell_occupancy(element, atomic_subshell, reference=None)``
    Returns occupancy of an element and atomic subshell.

Transition properties
---------------------

Properties associated with an electron transition, relaxation process of an 
electron between quantum states leading to X-rays emission, Auger electrons or 
Coster-Kronig transitions.

* ``pyxray.transition(transition)``
    Returns transition descriptor.

* ``pyxray.transition_notation(transition, notation, encoding='utf16', reference=None)``
    Returns notation of a transition.
    
    Examples:

    .. code:: python

        pyxray.transition_notation('Ka1', 'iupac') #=> 'K-L3'
        pyxray.transition_notation('L3-M1', 'siegbahn', 'ascii') #=> 'Ll'

* ``pyxray.transition_energy_eV(element, transition, reference=None)``
    Returns energy of an element and transition (in eV).
    
    Examples:
        
    .. code:: python
        
        pyxray.transition_energy_eV(14, 'Ka1') #=> 1740.0263764535946
        pyxray.transition_energy_eV(14, 'Ma1') #=> NotFound exception

* ``pyxray.transition_probability(element, transition, reference=None)``
    Returns probability of an element and transition.

* ``pyxray.transition_relative_weight(element, transition, reference=None)``
    Returns relative weight of an element and transition.

Transition set properties
-------------------------

Properties associated with a transition set, an indistinguishable transition 
(e.g. Ka from Ka1/Ka2).

* ``pyxray.transitionset(transitionset)``
    Returns transition set descriptor.

* ``pyxray.transitionset_notation(transitionset, notation, encoding='utf16', reference=None)``
    Returns notation of a transition set.
    
* ``pyxray.transitionset_energy_eV(element, transitionset, reference=None)``
    Returns energy of an element and transition set (in eV).

* ``pyxray.transitionset_relative_weight(element, transitionset, reference=None)``
    Returns relative weight of an element and transition set.

Development
===========

*pyxray* stores all data for the above functions in a *SQLite* database. 
The database is constructed during the build process of the Python package 
(i.e. ``python setup.py build``) using registered parsers. 
The provided parsers are located in the package ``pyxray.parser``, but external
parsers can be provided by registering to the entry point ``pyxray.parser``.
In short, the database is not provide in the source code, only in the 
distributed version. 
It is therefore necessary to build the *SQLite* database when running *pyxray*
in development mode.
Building the database will take several minutes.








