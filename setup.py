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
            'unattributed transition notation = pyxray.parser.unattributed:TransitionNotationParser',
            'wikipedia element name = pyxray.parser.wikipedia:WikipediaElementNameParser',
            'sargent-welch element atomic weight = pyxray.parser.sargent_welch:SargentWelchElementAtomicWeightParser',
            'sargent-welch element mass density = pyxray.parser.sargent_welch:SargentWelchElementMassDensityParser',
            'jenkins1991 transition notation = pyxray.parser.jenkins1991:Jenkins1991TransitionNotationParser',
            'perkins1991 = pyxray.parser.perkins1991:Perkins1991Parser',
            'nist atomic weight = pyxray.parser.nist:NISTElementAtomicWeightParser',
            'jeol transition = pyxray.parser.jeol:JEOLTransitionParser',
             ],
                      },
)

