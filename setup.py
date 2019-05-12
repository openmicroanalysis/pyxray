#!/usr/bin/env python

# Standard library modules.
import os
import sys
import logging

# Third party modules.
from setuptools import setup, find_packages
import setuptools.command.build_py as _build_py

# Local modules.
import versioneer

# Globals and constants variables.
logger = logging.getLogger(__name__)
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class build_py(_build_py.build_py):

    def run(self):
        # Build SQL database
        import sqlalchemy
        import pyxray.sql.build

        logging.basicConfig()
        logger.setLevel(logging.INFO)

        filepath = os.path.abspath(os.path.join(BASEDIR, 'pyxray', 'data', 'pyxray.db'))
        if os.path.exists(filepath):
            os.remove(filepath)

        engine = sqlalchemy.create_engine('sqlite:///' + filepath)
        builder = pyxray.sql.build.SqlDatabaseBuilder(engine)
        builder.build()

        try:
            del self.data_files # Force reinitialization of files to copy
        except AttributeError:
            pass

        super().run()

with open(os.path.join(BASEDIR, 'README.rst'), 'r') as fp:
    LONG_DESCRIPTION = fp.read()

INSTALL_REQUIRES = ['tabulate', 'sqlalchemy', 'tqdm', 'dataclasses;python_version~="3.6"']
EXTRAS_REQUIRE = {'develop': ['requests', 'requests-cache', 'pytest', 'pytest-cov']
                  }

CMDCLASS = versioneer.get_cmdclass()
CMDCLASS['build_py'] = build_py

ENTRY_POINTS = {
    'pyxray.parser':
      [
        'element symbol = pyxray.parser.notation:ElementSymbolParser',
        'atomic shell notation = pyxray.parser.notation:AtomicShellNotationParser',
        'atomic subshell notation = pyxray.parser.notation:AtomicSubshellNotationParser',
        'generic x-ray transition notation = pyxray.parser.notation:GenericXrayTransitionNotationParser',
        'known x-ray transition notation = pyxray.parser.notation:KnownXrayTransitionNotationParser',
        'series x-ray transition notation = pyxray.parser.notation:SeriesXrayTransitionNotationParser',
        'family x-ray transition notation = pyxray.parser.notation:FamilyXrayTransitionNotationParser',
        'wikipedia element name = pyxray.parser.wikipedia:WikipediaElementNameParser',
        'sargent-welch element atomic weight = pyxray.parser.sargent_welch:SargentWelchElementAtomicWeightParser',
        'sargent-welch element mass density = pyxray.parser.sargent_welch:SargentWelchElementMassDensityParser',
        'perkins1991 = pyxray.parser.perkins1991:Perkins1991Parser',
        'nist atomic weight = pyxray.parser.nist:NISTElementAtomicWeightParser',
        'jeol transition = pyxray.parser.jeol:JEOLTransitionParser',
        'campbell2001 = pyxray.parser.campbell2001:CampbellAtomicSubshellRadiativeWidthParser',
        'dtsa1992 subshell = pyxray.parser.dtsa:DtsaSubshellParser',
        'dtsa1992 transition = pyxray.parser.dtsa:DtsaLineParser',
       ],
      }

setup(name="pyxray",
      version=versioneer.get_version(),
      url='https://github.com/openmicroanalysis/pyxray',
      description="Definitions and properties of X-ray transitions",
      long_description=LONG_DESCRIPTION,
      author="Philippe T. Pinard",
      author_email="philippe.pinard@gmail.com",
      license="MIT",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=find_packages(),
      package_data={'pyxray': ['data/pyxray.db']},

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      cmdclass=CMDCLASS,

      entry_points=ENTRY_POINTS,
)

