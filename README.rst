######
pyxray
######

.. image:: https://img.shields.io/pypi/v/pyxray.svg
   :target: https://pypi.python.org/pypi/pyxray

.. image:: https://img.shields.io/travis/openmicroanalysis/pyxray.svg
   :target: https://travis-ci.org/openmicroanalysis/pyxray

.. image:: https://img.shields.io/codecov/c/github/openmicroanalysis/pyxray.svg
   :target: https://codecov.io/github/openmicroanalysis/pyxray

.. image:: https://readthedocs.org/projects/pyxray/badge/?version=latest
   :target: https://pyxray.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

*pyxray* is a Python library that defines basic object to specify atomic
subshells and X-ray transitions.
The objects also provide critical information as the energy, existence and
different notations of the X-ray transitions.

*pyxray* supports 3.6+ (no Python 2.x support).

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

* ``xray_transition``:
    either

    * `XrayTransition <http://github.com/openmicroanalysis/pyxray/blob/master/pyxray/descriptor.py>`_ object
    * a ``tuple`` of source and destination subshells
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

        pyxray.element_atomic_number('fe') #=> 26
        pyxray.element_atomic_number('Fe') #=> 26
        pyxray.element_atomic_number('iron') #=> 26
        pyxray.element_atomic_number('eisen') #=> 26

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

* ``pyxray.element_xray_transition(element, reference=None)``
    Returns X-ray transition descriptor if x-ray transition has a
    probability greater than 0 for that element.

* ``pyxray.element_xray_transitions(element, xray_transition_set=None, reference=None)``
    Returns all X-ray transitions which have a probability greater than 0
    for that element. If *xray_transition_set* is not ``None``, returns all
    x-ray transitions for this x-ray transition set.

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

X-ray transition properties
---------------------------

Properties associated with an electron transition, relaxation process of an
electron between quantum states leading to X-rays emission.

* ``pyxray.xray_transition(xray_transition)``
    Returns X-ray transition descriptor.

* ``pyxray.xray_transition_notation(xray_transition, notation, encoding='utf16', reference=None)``
    Returns notation of an X-ray transition.

    Examples:

    .. code:: python

        pyxray.transition_notation('Ka1', 'iupac') #=> 'K-L3'
        pyxray.transition_notation('Ka', 'iupac') #=> 'K-L2,3'
        pyxray.transition_notation('L3-M1', 'siegbahn', 'ascii') #=> 'Ll'

* ``pyxray.xray_transition_energy_eV(element, xray_transition, reference=None)``
    Returns energy of an element and X-ray transition (in eV).

    Examples:

    .. code:: python

        pyxray.xray_transition_energy_eV(14, 'Ka1') #=> 1740.0263764535946
        pyxray.xray_transition_energy_eV(14, 'Ma1') #=> NotFound exception

* ``pyxray.xray_transition_probability(element, xray_transition, reference=None)``
    Returns probability of an element and X-ray transition.

* ``pyxray.xray_transition_relative_weight(element, xray_transition, reference=None)``
    Returns relative weight of an element and X-ray transition.

X-ray line
----------

Object to represent an x-ray transition and its properties.

* ``pyxray.xray_line(element, xray_transition, reference=None)``
    Returns X-ray line descriptor.

.. code:: python

   xrayline = pyxray.xray_line(14, 'Ka1')
   xrayline.atomic_number #=> 14
   xrayline.transition #=> XrayTransition(2, 1, 3, 1, 0, 1)
   xrayline.iupac #=> Si K–L3
   xrayline.siegbahn #=> Si Kα1
   xrayline.energy_eV #=> 1740.0
   xrayline.probability #=> 0.031705199999999996
   xrayline.relative_weight #=> 1.0

As any other descriptors, X-ray line objects are immutable and hashable so they can be used as keys of a dictionary.

.. code:: python

   xrayline1 = pyxray.xray_line(13, 'Ka1')
   xrayline2 = pyxray.xray_line('Al', 'Ka1')
   xrayline1 == xrayline2 #=> True
   pyxray.xray_line(13, 'Ka1') == pyxray.xray_line(13, 'Ka') #=> False

To sort X-ray lines, use one of their properties:

.. code:: python

   from operator import attrgetter
   lines = [pyxray.xray_line(14, 'Ka1'), pyxray.xray_line(13, 'Ka1'), pyxray.xray_line(14, 'Ll')]
   sorted(lines, key=attrgetter('energy_eV')) #=> [XrayLine(Si L3–M1), XrayLine(Al K–L3), XrayLine(Si K–L3)]

Composition
-----------

Defines a composition of a compound.

To create a composition, use the class methods:

* ``Composition.from_pure(z)``
* ``Composition.from_formula(formula)``
* ``Composition.from_mass_fractions(mass_fractions, formula=None)``
* ``Composition.from_atomic_fractions(atomic_fractions, formula=None)``

Use the following attributes to access the composition values:

* ``mass_fractions``: ``dict`` where the keys are atomic numbers and the values weight fractions.
* ``atomic_fractions``: ``dict`` where the keys are atomic numbers and the values atomic fractions.
* ``formula``: chemical formula

The composition object is immutable, i.e. it cannot be modified once created.
Equality can be checked.
It is hashable.
It can be pickled or copied.

Release notes
=============

1.6.1
-----

- Fix deprecation warning with new setuptools
- Fix problem with requests caching

1.6
---

- Add ordering of Element, AtomicShell, AtomicSubshell
- Use `sqlalchemy <https://sqlalchemy.org>`_ to create and interact with database
- Add probability and relative weight properties to XrayLine
- Add possibility to define preferred references

1.5
---

- Add composition object

1.4
---

* `#13 <https://github.com/openmicroanalysis/pyxray/pull/13>`_ Add DTSA X-ray subshell and line data
* `#14 <https://github.com/openmicroanalysis/pyxray/pull/14>`_ Use dataclasses for descriptors and properties

1.3.4
-----

* Fix descriptors can be copied and pickled.

1.3.3
-----

* Fix method `element_xray_transitions` not to return duplicates.

1.3.2
-----

* Add energy to XrayLine.
* Fix missing energy property for x-ray transition sets from JEOL database.
* Clean up of unit tests.

1.3.1
-----

* Make XrayLine a descriptor and add method to create it from database.

1.2.1
-----

* Fix in build process.

1.2.0
-----

* Add ``XrayLine`` class.

Contributors
============

* `@drix00 <https://github.com/drix00>`_

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
In short, in the *pyxray folder*, run

.. code:: shell

   pip install -e .[develop]
   python3 setup.py build

Build the documentation:

.. code-block:: console

    $ cd docs
    $ make html

Add or modify the API documentation:

.. code-block:: console

    $ cd docs
    $ sphinx-apidoc -o source/api -e -f -P ../pyxray
    $ make html

License
=======

The library is provided under the MIT license.

*pyxray* was partially developed as part of the doctorate thesis project of
Philippe T. Pinard at RWTH Aachen University (Aachen, Germany) under the
supervision of Dr. Silvia Richter.

Copyright (c) 2015-2016/06 Philippe Pinard and Silvia Richter

Copyright (c) 2016/06-2019 Philippe Pinard





