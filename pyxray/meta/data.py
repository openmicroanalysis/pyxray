"""
Base database
"""

# Standard library modules.
import abc

# Third party modules.
import six

# Local modules.

# Globals and constants variables.

@six.add_metaclass(abc.ABCMeta)
class _Database(object):

    def __init__(self):
        self.reference_priority = []

    @property
    def reference_priority(self):
        """
        Returns the preferable references to use, in decreasing order of priority.
        
        :rtype: :class:`list` of reference keys
        """
        return list(self._reference_priority)

    @reference_priority.setter
    def reference_priority(self, references):
        """
        Sets the preferable references to use, in decreasing order of priority.
        
        :arg references: :class:`list` of reference keys
        """
        self._reference_priority = list(references)

