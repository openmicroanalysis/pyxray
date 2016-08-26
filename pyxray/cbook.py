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
        
    .. note:: Keyword arguments are not accepted
    """

    def __new__(cls, name, bases, methods, *, attrs=None):
        # Make a __new__ function and add to the class dict
        def __new__(cls, *args):
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

    def __call__(self, *args):
        if args in self.__cache:
            return self.__cache[args]

        # Create object
        obj = super().__call__(*args)

        # Cached
        self.__cache[args] = obj

        return obj

class Validable(type):
    """
    Validates the object before it is created using the arguments from the
    :meth:`__init__`.
    The class method :class:`validate` should be overwritten.
    The method should always return the arguments.
    """

    def validate(cls, *args): #@NoSelf
        return args

    def __call__(self, *args):
        args = self.validate(*args)
        return super().__call__(*args)
