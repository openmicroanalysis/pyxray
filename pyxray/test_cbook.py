#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging


# Third party modules.

# Local modules.
from pyxray.cbook import \
    Immutable, Cachable, Validable, ProgressMixin, ProgressReportMixin

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

class MockValidable2(metaclass=Validable):

    @classmethod
    def validate(cls, foo):
        pass

    def __init__(self, foo):
        self.foo = foo

class MockValidable3(metaclass=Validable):

    @classmethod
    def validate(cls, foo):
        return (), {'foo': foo + 'd'}

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

class MockProgress(ProgressMixin):
    pass

class MockProgressReport(ProgressReportMixin):
    pass

class TestImmutable(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockImmutable('abc', 123)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual('abc', self.obj.foo)
        self.assertEqual(123, self.obj.bar)

        self.assertRaises(TypeError, MockImmutable, 'abc')
        self.assertRaises(TypeError, MockImmutable, 'abc', 'abc', 'abc')

        obj = MockImmutable('abc', bar=123)
        self.assertEqual('abc', obj.foo)
        self.assertEqual(123, obj.bar)

        obj = MockImmutable(foo='abc', bar=123)
        self.assertEqual('abc', obj.foo)
        self.assertEqual(123, obj.bar)

        self.assertRaises(TypeError, MockImmutable, 'abc', abc='def')

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
        self.obj2 = MockValidable2('abc')
        self.obj3 = MockValidable3('abc')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test__init__(self):
        self.assertEqual('abcd', self.obj.foo)
        self.assertEqual('abc', self.obj2.foo)
        self.assertEqual('abcd', self.obj3.foo)

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

class TestProgressMixin(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockProgress()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testupdate(self):
        self.obj.update(50)
        self.assertEqual(50, self.obj.progress)

class TestProgressReportMixin(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.obj = MockProgressReport()
        self.obj.add_reporthook(self._hook)
        self.progress = 0

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def _hook(self, progress):
        self.progress = progress

    def testupdate(self):
        self.assertEqual(0, self.progress)
        self.obj.update(50)
        self.assertEqual(50, self.obj.progress)
        self.assertEqual(50, self.progress)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
