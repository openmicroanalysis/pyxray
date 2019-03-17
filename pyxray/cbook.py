"""
Cookbook examples and patterns.
"""

# Standard library modules.

# Third party modules.

# Local modules.

# Globals and constants variables.

class ProgressMixin:

    def update(self, progress):
        """
        Update the progress, a value between 0 and 100.
        """
        assert 0 <= progress <= 100
        self._progress = int(progress)

    @property
    def progress(self):
        """
        Current progress, a value between 0 and 100.
        """
        return getattr(self, '_progress', 0)

class ProgressReportMixin(ProgressMixin):

    def add_reporthook(self, hook):
        assert callable(hook)
        if not hasattr(self, '_reporthooks'):
            self._reporthooks = set()
        self._reporthooks.add(hook)

    def clear_reporthooks(self):
        self._reporthooks = set()

    def update(self, progress):
        super().update(progress)
        for hook in getattr(self, '_reporthooks', []):
            hook(progress)

def formatdoc(*formatargs, **formatkwargs):
    def decorate(func):
        func.__doc__ = func.__doc__.format(*formatargs, **formatkwargs)
        return func
    return decorate
