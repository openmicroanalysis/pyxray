#!/usr/bin/env python

# Standard library modules.

# Third party modules.
from setuptools import setup

# Local modules.
import versioneer

# Globals and constants variables.

setup(name="pyxray",
      version=versioneer.get_version(),
      url='http://pyxray.bitbucket.org',
      description="Definitions and properties of X-ray transitions",
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

      test_suite='nose.collector',

      cmdclass=versioneer.get_cmdclass(),

      entry_points={
          'pyxray.parser':
            [
             'unattributed element symbol = pyxray.parser.unattributed:ElementSymbolPropertyParser',
             'unattributed atomic shell notation = pyxray.parser.unattributed:AtomicShellNotationParser',
             'unattributed atomic subshell notation = pyxray.parser.unattributed:AtomicSubshellNotationParser',
             'wikipedia element name = pyxray.parser.wikipedia:WikipediaElementNameParser',
             'sargent-welch element atomic weight = pyxray.parser.sargent_welch:SargentWelchElementAtomicWeightParser',
             'sargent-welch element mass density = pyxray.parser.sargent_welch:SargentWelchElementMassDensityParser',
#             'element = pyxray.sql.mapping.base:mapper_element',
#             'notation type = pyxray.sql.mapping.base:mapper_notation_type',
#             'atomic shell = pyxray.sql.mapping.base:mapper_atomic_shell',
##             'atomic shell notation = pyxray.sql.mapping.base:mapper_atomic_shell_notation',
#             'atomic subshell = pyxray.sql.mapping.base:mapper_atomic_subshell',
#             'atomic subshell notation = pyxray.sql.mapping.base:mapper_atomic_subshell_notation',
#             'transition = pyxray.sql.mapping.base:mapper_transition',
#             'Sargent-Welch element atomic weight = pyxray.sql.mapping.sargent_welch:mapper_atomic_weight',
#             'Sargent-Welch element mass density = pyxray.sql.mapping.sargent_welch:mapper_mass_density',
             #'Wikipedia element name = pyxray.sql.mapping.wikipedia:mapper_name',
             ],
                      },
)

