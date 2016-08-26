#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging


# Third party modules.

# Local modules.
from pyxray.cbook import Immutable, Cachable, Validable

# Globals and constants variables.

class MockImmutable(metaclass=Immutable,
                    attrs=('foo', 'bar')):
    pass

class MockCachable(metaclass=Cachable):

    def __init__(self, foo):
        self.foo = foo

class MockValidable(metaclass=Validable):

    @classmethod
    def validate(cls, foo):
        if foo != 'abc':
            raise ValueError
        return (foo + 'd',)

    def __init__(self, foo):
        self.foo = foo

class CombinedType(Immutable, Cachable, Validable):
    pass

class MockCombined(metaclass=CombinedType, attrs=('foo', 'bar')):

    @classmethod
    def validate(cls, foo, bar):
        if len(foo) != 3:
            raise ValueError
        return (foo + 'd', bar)

class TestImmutable(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockImmutable('abc', 123)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertRaises(TypeError, MockImmutable, 'abc')
        self.assertRaises(TypeError, MockImmutable, 'abc', 'abc', 'abc')

    def test__slots__(self):
        self.assertRaises(AttributeError, setattr, self.obj, 'foo2', 'abc')

    def testfoo(self):
        self.assertEqual('abc', self.obj.foo)
        self.assertRaises(AttributeError, setattr, self.obj, 'foo', 'def')
        self.assertRaises(AttributeError, delattr, self.obj, 'foo')

    def testbar(self):
        self.assertEqual(123, self.obj.bar)
        self.assertRaises(AttributeError, setattr, self.obj, 'bar', 456)
        self.assertRaises(AttributeError, delattr, self.obj, 'bar')

class TestCachable(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockCachable('abc')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual('abc', self.obj.foo)

    def testcache(self):
        obj2 = MockCachable('abc')
        self.assertEqual('abc', obj2.foo)
        self.assertEqual(obj2, self.obj)
        self.assertIs(obj2, self.obj)

        obj3 = MockCachable('def')
        self.assertEqual('def', obj3.foo)
        self.assertNotEqual(obj3, self.obj)
        self.assertIsNot(obj3, self.obj)

class TestValidable(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockValidable('abc')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual('abcd', self.obj.foo)

    def testvalidate(self):
        self.assertRaises(ValueError, MockValidable, 'def')

class TestCombined(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockCombined('abc', 123)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertRaises(TypeError, MockCombined, 'abc')
        self.assertRaises(TypeError, MockCombined, 'abc', 'abc', 'abc')

    def test__slots__(self):
        self.assertRaises(AttributeError, setattr, self.obj, 'foo2', 'abc')

    def testfoo(self):
        self.assertEqual('abcd', self.obj.foo)
        self.assertRaises(AttributeError, setattr, self.obj, 'foo', 'def')
        self.assertRaises(AttributeError, delattr, self.obj, 'foo')

    def testbar(self):
        self.assertEqual(123, self.obj.bar)
        self.assertRaises(AttributeError, setattr, self.obj, 'bar', 456)
        self.assertRaises(AttributeError, delattr, self.obj, 'bar')

    def testcache(self):
        obj2 = MockCombined('abc', 123)
        self.assertEqual('abcd', obj2.foo)
        self.assertEqual(obj2, self.obj)
        self.assertIs(obj2, self.obj)

        obj3 = MockCombined('def', 123)
        self.assertEqual('defd', obj3.foo)
        self.assertNotEqual(obj3, self.obj)
        self.assertIsNot(obj3, self.obj)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
