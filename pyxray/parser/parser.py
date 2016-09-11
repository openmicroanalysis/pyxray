"""
Definition of parser
"""

# Standard library modules.
import collections.abc
import inspect

# Third party modules.
import pkg_resources

# Local modules.
from pyxray.cbook import ProgressReportMixin

# Globals and constants variables.

ENTRY_POINT = 'pyxray.parser'

class _Parser(collections.abc.Iterable, ProgressReportMixin):
    """
    (abstract) Class to parse X-ray related information from a data source.
    
    A parser is simply an iterable object which returns a new property at each 
    iteration. For example::
    
    class ElementSymbolParser(_Parser):
    
        def __iter__(self):
            yield ElementSymbol(...)
            
    Each parser should be registered in the setup.py under the entry point:
    `pyxray.parser`
    """
    pass

def find_parsers():
    parsers = []
    for entry_point in pkg_resources.iter_entry_points(ENTRY_POINT):
        name = entry_point.name
        parser = entry_point.load()
        if inspect.isclass(parser):
            parser = parser()
        parsers.append((name, parser))
    return parsers
