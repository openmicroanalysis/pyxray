#!/usr/bin/env python

# Standard library modules.

# Third party modules.
from setuptools import setup

# Local modules.

# Globals and constants variables.

setup(name="pyxray",
      version='0.1',
      url='http://pyxray.bitbucket.org',
      description="Definitions and properties of x-ray transitions",
      author="Hendrix Demers and Philippe T. Pinard",
      author_email="hendrix.demers@mail.mcgill.ca and philippe.pinard@gmail.com",
      license="MIT",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=['pyxray'],
      package_data={'pyxray': ['data/*']},

      install_requires=['pyparsing'],

      test_suite='pyxray.tests.test_all',
)

