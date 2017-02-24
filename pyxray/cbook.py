"""
Cookbook examples and patterns.
"""

# Standard library modules.
import weakref

# Third party modules.

# Local modules.

# Globals and constants variables.

class Immutable(type):
    """
    Make a class immutable. 
    The attribute cannot be added or modified.
    The attributes should be defined by the argument ``attrs`` in the class
    definition::
    
        class Foo(metaclass=Immutable, attrs=('bar',)):
            pass
            
    The constructor of the class then takes the same number of arguments::
    
        foo = Foo('abc')
        foo.bar # returns 'abc'
    """

    def __new__(cls, name, bases, methods, *, attrs=None):
        # Make a __new__ function and add to the class dict
        def __new__(cls, *args, **kwargs):
            args = list(args)

            for key, value in kwargs.items():
                try:
                    index = attrs.index(key)
                except ValueError:
                    raise TypeError('Unknown argument: {0}'.format(key))
                args.insert(index, value)

            if len(args) != len(attrs):
                raise TypeError('Expected {} arguments'.format(len(attrs)))

            obj = object.__new__(cls)
            obj._values = tuple(args)
            obj._attrs = tuple(attrs)

            return obj
        methods['__new__'] = __new__

        # Configure __slots__
        methods['__slots__'] = ('__weakref__', '_values', '_attrs')

        # Populate a dictionary of field property accessors
        methods.update({name: property(lambda s, n=n: s._values[n])
                        for n, name in enumerate(attrs)})

        cls = super().__new__(cls, name, bases, methods)

        return cls

    def __init__(self, name, bases, methods, *, attrs=None):
        super().__init__(name, bases, methods)

class Cachable(type):
    """
    From Beazley, D. & Jones, B. K. (2013) Python Cookbook, O'Reilly.
    
    Creates a cache using the arguments of :meth:`__init__`.
    """

    def __init__(self, name, bases, methods):
        super().__init__(name, bases, methods)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args, **kwargs):
        cachekey = args + tuple(sorted(kwargs.items()))
        if cachekey in self.__cache:
            return self.__cache[cachekey]

        # Create object
        obj = super().__call__(*args, **kwargs)

        # Cached
        self.__cache[cachekey] = obj

        return obj

class Validable(type):
    """
    Validates the object before it is created using the arguments from the
    :meth:`__init__`.
    The class method :meth:`validate` should be overwritten.
    There are three options for the return values of the :meth:`validate`:
    
        1. return ``None`` or no return at all: the same arguments and 
            keyword arguments are passed to the constructor
        2. return a :class:`tuple` and a :class:`dict`: the tuple contains
            updated arguments and the dict, updated keyword-arguments
        3. return a :class:`tuple`: the tuple contains updated arguments.
            No keyword-arguments is passed to the constructor.
    
    In all other cases, a :exc:`ValueError` is raised.
    """

    def validate(cls, *args, **kwargs): #@NoSelf #pragma: no cover
        return args

    def __call__(self, *args, **kwargs):
        out = self.validate(*args, **kwargs)
        if out is not None:
            if len(out) == 2 and \
                    isinstance(out[0], tuple) and \
                    isinstance(out[1], dict):
                args, kwargs = out
            elif isinstance(out, tuple):
                args = out
                kwargs = {}
            else: #pragma: no cover
                raise ValueError('Unknown type of return arguments')

        return super().__call__(*args, **kwargs)

class Reprable(type):
    """
    Construct the __repr__ of an object based on the :meth:`_repr_inner` method
    if it is defined.
    """

    def __new__(cls, name, bases, methods, *args, **kwargs):
        def __repr__(self):
            s = '{0}('.format(self.__class__.__name__)

            if hasattr(self, '_repr_inner'):
                s += self._repr_inner()

            else:
                inner = []
                for attr, value in zip(self._attrs, self._values):
                    if hasattr(value, '_repr_inner'):
                        inner.append(value._repr_inner())
                    elif '_' in attr:
                        _, unit = attr.rsplit('_', 1)
                        inner.append('{0:.4e}{1}'.format(value, unit))
                    else:
                        inner.append('{0}={1}'.format(attr, value))
                s += ', '.join(inner)

            s += ')'
            return s
        methods['__repr__'] = __repr__

        return super().__new__(cls, name, bases, methods, *args, **kwargs)

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