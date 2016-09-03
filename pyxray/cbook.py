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
            obj._fieldvalues = tuple(args)

            return obj
        methods['__new__'] = __new__

        # Configure __slots__
        methods['__slots__'] = ('__weakref__', '_fieldvalues')

        # Populate a dictionary of field property accessors
        methods.update({name: property(lambda s, n=n: s._fieldvalues[n])
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

    def validate(cls, *args, **kwargs): #@NoSelf
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
            else:
                raise ValueError('Unknown type of return arguments')

        return super().__call__(*args, **kwargs)

def allequal(iterator):
    """
    Returns ``True`` if all elements are equal.
    
    From: http://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
    """
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True