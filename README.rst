pyxray
======

.. image:: https://badge.fury.io/py/pyxray.svg
   :target: http://badge.fury.io/py/pyxray

.. image:: https://readthedocs.org/projects/pyxray/badge/?version=latest
   :target: https://readthedocs.org/projects/pyxray/

.. image:: https://travis-ci.org/ppinard/pyxray.svg?branch=master
   :target: https://travis-ci.org/ppinard/pyxray
   
.. image:: https://codecov.io/github/ppinard/pyxray/coverage.svg?branch=master
   :target: https://codecov.io/github/ppinard/pyxray?branch=master

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
------------

Easiest way to install using ``pip``::

    $ pip install pyxray
    
For development installation from the git repository::

    $ git clone git@github.com:ppinard/pyxray.git
    $ cd pyxray
    $ pip install -e .
    $ python3 setup.py build
    
The last instruction will build the SQL database and will take several minutes.
The database is not provide in the source code, only in the distributed version.

Examples
--------




