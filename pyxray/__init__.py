"""
pyxray - Definitions and properties of X-ray transitions
"""

from pyxray._version import get_versions
__version__ = get_versions()['version']
del get_versions

from pyxray.base import NotFound
from pyxray.descriptor import *
from pyxray.data import *
from pyxray.composition import *
