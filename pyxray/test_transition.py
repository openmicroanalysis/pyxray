""" """

# Standard library modules.
import unittest
import logging
import pickle
import sys

# Third party modules.

# Local modules.
from pyxray.transition import \
    (Transition, get_transitions, transitionset, from_string,
     K_family, L_family, M_family, N_family,
     Ka, Kb, La, Lb, Lg, Ma, Mb, Mg,
     LI, LII, LIII, MI, MII, MIII, MIV, MV,
     iupac2latex, siegbahn2latex, _siegbahn_unicode_to_ascii)
from pyxray.subshell import Subshell

# Globals and constants variables.
from pyxray.transition import _SUBSHELLS, _SIEGBAHNS

class TestTransition(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        for i, shells in enumerate(_SUBSHELLS):
            x = Transition(13, *shells)
            setattr(self, 'x%i' % i, x)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertTrue(True)

    def test__init__subshells(self):
        x = Transition(13, Subshell(13, 4), Subshell(13, 1))
        self.assertEqual(13, x.z)

    def test__init__siegbahn(self):
        x = Transition(13, siegbahn="Ka1")
        self.assertEqual(13, x.z)

    def test__str__(self):
        if sys.version_info > (3, 0):
            for i, siegbahn in enumerate(_SIEGBAHNS):
                x = getattr(self, "x%i" % i)
                self.assertEqual("Al " + siegbahn, str(x))
        else:
            for i, siegbahn in enumerate(_SIEGBAHNS):
                x = getattr(self, "x%i" % i)
                self.assertEqual("Al " + siegbahn, unicode(x)) #@UndefinedVariable

    def test__eq__(self):
        t = Transition(13, 4, 1)
        self.assertEqual(Transition(13, 4, 1), t)
        self.assertNotEqual(1, t)

        s = transitionset(13, '', '', [Transition(13, 4, 1)])
        self.assertEqual(t, s)

    def test__lt__(self):
        self.assertGreater(Transition(13, 4, 1), Transition(6, 4, 1))
        self.assertGreater(Transition(13, 4, 1), Transition(13, 3, 1))
        self.assertLess(Transition(13, 4, 1), Transition(13, 9, 4))

    def test__hash__(self):
        self.assertEqual(hash(Transition(13, 4, 1)), hash(Transition(13, siegbahn='Ka1')))
        self.assertNotEqual(hash(Transition(13, 4, 1)), hash(Transition(6, 4, 1)))

    def testz(self):
        for i in range(len(_SUBSHELLS)):
            x = getattr(self, "x%i" % i)
            self.assertEqual(13, x.z)
            self.assertEqual(13, x.atomicnumber)

    def testsymbol(self):
        for i in range(len(_SUBSHELLS)):
            x = getattr(self, "x%i" % i)
            self.assertEqual('Al', x.symbol)

    def testsrc(self):
        for i, shells in enumerate(_SUBSHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(Subshell(13, shells[0]), x.src)

    def testdest(self):
        for i, shells in enumerate(_SUBSHELLS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(Subshell(13, shells[1]), x.dest)

    def testiupac(self):
        for i, shells in enumerate(_SUBSHELLS):
            x = getattr(self, "x%i" % i)
            src = Subshell(13, shells[0])
            dest = Subshell(13, shells[1])
            self.assertEqual('-'.join([dest.iupac, src.iupac]), x.iupac)

    def testsiegbahn(self):
        for i, siegbahn in enumerate(_SIEGBAHNS):
            x = getattr(self, "x%i" % i)
            self.assertEqual(siegbahn, x.siegbahn)

    def testsiegbahn_nogreek(self):
        for i, siegbahn in enumerate(_SIEGBAHNS):
            siegbahn = _siegbahn_unicode_to_ascii(siegbahn)
            x = getattr(self, "x%i" % i)
            self.assertEqual(siegbahn, x.siegbahn_nogreek)

    def testenergy_eV(self):
        self.assertAlmostEqual(1486.3, self.x1.energy_eV, 4)

    def testprobability(self):
        self.assertAlmostEqual(0.0123699, self.x1.probability, 4)

    def testexists(self):
        self.assertTrue(self.x1.exists())
        self.assertFalse(self.x29.exists())

    def testis_satellite(self):
        self.assertFalse(self.x0.is_satellite())
        self.assertTrue(self.x83.is_satellite())

    def testis_diagram_line(self):
        self.assertTrue(self.x0.is_diagram_line())
        self.assertFalse(self.x83.is_diagram_line())

    def testwidth_eV(self):
        self.assertAlmostEqual(0.424, self.x0.width_eV, 4)
        self.assertAlmostEqual(0.424, self.x1.width_eV, 4)

    def testpickle(self):
        s = pickle.dumps(self.x0)
        x0 = pickle.loads(s)
        self.assertEqual(x0, self.x0)

class Testtransitionset(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        t1 = Transition(13, 4, 1)
        t2 = Transition(13, 3, 1)
        t3 = Transition(13, 3, 1)
        self.set = transitionset(13, u'G\u03b1', 'G1-H(2,3)', [t1, t2, t3])

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testskeleton(self):
        self.assertEqual(13, self.set.z)
        self.assertEqual(2, len(self.set))

    def test__init__(self):
        t1 = Transition(13, 4, 1)
        t2 = Transition(14, 3, 1)
        self.assertRaises(ValueError, transitionset, 13, u'G\u03b1', 'G1-H(2,3)', [t1, t2])

    def test__repr__(self):
        self.assertEqual('<transitionset(Al Ga: Ka2, Ka1)>', repr(self.set))

    def test__str__(self):
        if sys.version_info > (3, 0):
            self.assertEqual(u'Al G\u03b1', str(self.set))
        else:
            self.assertEqual(u'Al G\u03b1', unicode(self.set)) #@UndefinedVariable

    def test__contains__(self):
        self.assertTrue(Transition(13, 4, 1) in self.set)
        self.assertFalse(Transition(13, 7, 1) in self.set)

    def test__eq__(self):
        other = transitionset(13, u'G\u03b1', 'G1-H(2,3)', [Transition(13, 4, 1), Transition(13, 3, 1)])
        self.assertEqual(self.set, other)

    def test__lt__(self):
        other = transitionset(6, u'G\u03b1', 'G1-H(2,3)', [Transition(6, 4, 1)])
        self.assertGreater(self.set, other)

        other = transitionset(13, u'G\u03b1', 'G1-H(2,3)', [Transition(13, 4, 1), Transition(13, 3, 1)])
        self.assertEqual(self.set, other)

        other2 = transitionset(13, u'G\u03b1', 'G1-H(2,3)', [Transition(13, 4, 1)])
        self.assertGreater(other2, other)
        self.assertLess(other, other2)

    def test__hash__(self):
        other = transitionset(13, u'G\u03b1', 'G1-H(2,3)', [Transition(13, 4, 1), Transition(13, 3, 1)])
        self.assertEqual(hash(other), hash(self.set))

        other = transitionset(13, u'G\u03b1', 'G1-H(2,3)', [Transition(13, 4, 1)])
        self.assertNotEqual(hash(other), hash(self.set))

    def testmost_probable(self):
        self.assertEqual(Transition(13, 4, 1), self.set.most_probable)

    def testsiegbahn(self):
        self.assertEqual(u'G\u03b1', self.set.siegbahn)

    def testsiegbahn_nogreek(self):
        self.assertEqual('Ga', self.set.siegbahn_nogreek)

    def testiupac(self):
        self.assertEqual('G1-H(2,3)', self.set.iupac)

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testget_transitions(self):
        transitions = get_transitions(13)
        self.assertEqual(11, len(transitions))

        transitions = get_transitions(13, 1e3, 2e3)
        self.assertEqual(4, len(transitions))

        transitions = get_transitions(13, include_satellite=True)
        self.assertEqual(18, len(transitions))

    def testfrom_string(self):
        self.assertEqual(from_string('Al Ka1'), Transition(13, siegbahn='Ka1'))
        self.assertEqual(from_string('Al K-L3'), Transition(13, siegbahn='Ka1'))
        self.assertEqual(from_string('Al Ka'), Ka(13))
        self.assertEqual(from_string('Al K-L(2,3)'), Ka(13))
        self.assertEqual(from_string('Al K'), K_family(13))

        self.assertRaises(ValueError, from_string, 'Al K a1')
        self.assertRaises(ValueError, from_string, 'Al Kc1')

    def testfamily(self):
        # K
        transitions = K_family(13)
        self.assertEqual(4, len(transitions))
        for transition in transitions:
            self.assertEqual('K', transition.dest.family)

        # L
        transitions = L_family(29)
        self.assertEqual(14, len(transitions))
        for transition in transitions:
            self.assertEqual('L', transition.dest.family)

        # M
        transitions = M_family(79)
        self.assertEqual(22, len(transitions))
        for transition in transitions:
            self.assertEqual('M', transition.dest.family)

        # N
        transitions = N_family(92)
        self.assertEqual(2, len(transitions))
        for transition in transitions:
            self.assertEqual('N', transition.dest.family)

    def testgroup(self):
        # Ka
        transitions = Ka(79)
        self.assertEqual(2, len(transitions))

        # Kb
        transitions = Kb(79)
        self.assertEqual(5, len(transitions))

        # La
        transitions = La(79)
        self.assertEqual(2, len(transitions))

        # Lb
        transitions = Lb(79)
        self.assertEqual(11, len(transitions))

        # Lg
        transitions = Lg(79)
        self.assertEqual(9, len(transitions))

        # Ma
        transitions = Ma(79)
        self.assertEqual(2, len(transitions))

        # Mb
        transitions = Mb(79)
        self.assertEqual(1, len(transitions))

        # Mg
        transitions = Mg(79)
        self.assertEqual(1, len(transitions))

    def testshell(self):
        # L
        transitions = LI(79) | LII(79) | LIII(79)
        self.assertEqual(L_family(79), transitions)

        # M
        transitions = MI(79) | MII(79) | MIII(79) | MIV(79) | MV(79)
        self.assertEqual(M_family(79), transitions)

    def testsiegbahn2latex(self):
        self.assertEqual(r"Al K$\alpha_{1}$", siegbahn2latex(Transition(13, siegbahn='Ka1')))
        self.assertEqual(r"Al K$\beta_{1}$", siegbahn2latex(Transition(13, siegbahn='Kb1')))
        self.assertEqual(r"Al L$\gamma_{1}$", siegbahn2latex(Transition(13, siegbahn='Lg1')))
        self.assertEqual(r"Al M$\zeta_{1}$", siegbahn2latex(Transition(13, siegbahn='Mz1')))

    def testiupac2latex(self):
        self.assertEqual(r"Al K-L$_{3}$", iupac2latex(Transition(13, siegbahn='Ka1')))
        self.assertEqual(r"Al K-M$_{3}$", iupac2latex(Transition(13, siegbahn='Kb1')))
        self.assertEqual(r"Al L$_{2}$-N$_{4}$", iupac2latex(Transition(13, siegbahn='Lg1')))
        self.assertEqual(r"M$_{4,5}$-N$_{2,3}$", iupac2latex('M(4,5)-N(2,3)'))
        self.assertEqual('G$_{1}$-H$_{2,3}$', iupac2latex('G1-H(2,3)'))

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
