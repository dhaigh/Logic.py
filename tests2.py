#!/usr/bin/env python2

from logic import *
import unittest

p, q, r, s = Var('p'), Var('q'), Var('r'), Var('s')

N = Not
A = And
O = Or
J = Xor
D = Nand
X = Nor
C = Conditional
E = Biconditional

Np = N(p)
Apq, Apqr, Apqrs = A(p, q), A(p, q, r), A(p, q, r, s)
Opq, Opqr, Opqrs = O(p, q), O(p, q, r), O(p, q, r, s)
Jpq, Jpqr, Jpqrs = J(p, q), J(p, q, r), J(p, q, r, s)
Dpq              = D(p, q)
Xpq              = X(p, q)
Cpq              = C(p, q)
Epq, Epqr, Epqrs = E(p, q), E(p, q, r), E(p, q, r, s)

t, f = True, False

# =============================================================================
# Expression
# =============================================================================

class TestExpressionMethods(unittest.TestCase):
    def test_len(self):
        self.assertEqual(len(p), 1)
        self.assertEqual(len(T), 1)
        self.assertEqual(len(F), 1)
        self.assertEqual(len(Np), 1)
        self.assertEqual(len(Apq), 2)
        self.assertEqual(len(Apqr), 3)
        self.assertEqual(len(Opq), 2)
        self.assertEqual(len(Opqr), 3)

    def test_stringification(self):
        self.assertEqual(str(p), 'p')
        self.assertEqual(str(T), 'T')
        self.assertEqual(str(F), 'F')
        self.assertEqual(str(Np), '~p')
        self.assertEqual(str(Apq), 'p ^ q')
        self.assertEqual(str(Opq), 'p v q')
        self.assertEqual(str(Jpq), 'p XOR q')
        self.assertEqual(str(Dpq), 'p NAND q')
        self.assertEqual(str(Xpq), 'p NOR q')
        self.assertEqual(str(Cpq), 'p -> q')
        self.assertEqual(str(Epq), 'p <-> q')
        self.assertEqual(str(Apqr), 'p ^ q ^ r')
        self.assertEqual(str(Opqr), 'p v q v r')
        self.assertEqual(str(Jpqr), 'p XOR q XOR r')
        self.assertEqual(str(Epqr), 'p <-> q <-> r')
        self.assertEqual(str(A(Opq, Jpq)), '(p v q) ^ (p XOR q)')
        self.assertEqual(str(A(N(Cpq), Cpq)), '~(p -> q) ^ (p -> q)')
        self.assertEqual(str(J(Np, O(Epqr, Xpq))),
						 '~p XOR ((p <-> q <-> r) v (p NOR q))')
        self.assertEqual(str(C(Apq, Opqr)), 'p ^ q -> p v q v r')
        self.assertEqual(str(O(C(Apq, p), q, r)), '(p ^ q -> p) v q v r')
        self.assertEqual(str(E(A(p, q, r), Opq)), 'p ^ q ^ r <-> p v q')
        self.assertEqual(str(E(A(Apq, r), Opq)), 'p ^ q ^ r <-> p v q')
        self.assertEqual(str(E(A(Apq, r), Cpq)), 'p ^ q ^ r <-> (p -> q)')

    def test_get_names(self):
        self.assertEqual(p.get_names(), ['p'])
        self.assertEqual(q.get_names(), ['q'])
        self.assertEqual(T.get_names(), [])
        self.assertEqual(F.get_names(), [])
        self.assertEqual(Np.get_names(), ['p'])
        self.assertEqual(Apq.get_names(), ['p', 'q'])
        self.assertEqual(Cpq.get_names(), ['p', 'q'])
        self.assertEqual(Epqr.get_names(), ['p', 'q', 'r'])
        self.assertEqual(Epqrs.get_names(), ['p', 'q', 'r', 's'])
        self.assertEqual(A(O(J(p, q), Var('x')), Var('qqq')).get_names(),
					     ['p', 'q', 'qqq', 'x'])
        self.assertEqual(Epqrs.get_names(), ['p', 'q', 'r', 's'])

    # equivalence __eq__, equivalent_to
    # eval

    def test_identical(self):
        self.assertTrue(Apq.identical(Apq))
        self.assertTrue(Apq.identical(A(p, q)))
        self.assertFalse(T.identical(O(p, Np)))
        self.assertFalse(Apqr.identical(A(Apq, r)))
        # do more


    def test_tautology(self):
        self.assertTrue(T.is_tautology())
        self.assertTrue(C(A(Cpq, p), p).is_tautology())
        self.assertTrue(O(p, Np).is_tautology())

    def test_contradiction(self):
        self.assertTrue(F.is_contradiction())
        self.assertTrue(A(p, Np).is_contradiction())
        self.assertFalse(p.is_contradiction())

# =============================================================================
# Binary Operations
# =============================================================================

class TestBinaryOperations(unittest.TestCase):
    def test_properties(self):
        self.assertEqual(Apq.terms, [p, q])
        self.assertEqual(Opqr.terms, [p, q, r])

    def test_getitem(self):
        self.assertIs(Apq[0], p)
        self.assertIs(Apq[1], q)
        self.assertIs(Apqr[1], q)
        self.assertIs(Apqr[2], r)
        self.assertIs(Dpq[0], p)
        self.assertIs(Dpq[1], q)

    def test_iter(self):
        i = 0
        for term in Apq:
            self.assertIs(term, Apq.terms[i])
            i += 1
        i = 0
        for term in Jpqr:
            self.assertIs(term, Jpqr.terms[i])
            i += 1

    def test_append(self):
        expr = And(p, q)
        expr.append(s)
        self.assertIs(expr.terms[2], s)

# =============================================================================
# Truth Tables
# =============================================================================







# =============================================================================
# Parser
# =============================================================================








# and expecting exceptions?












if __name__ == '__main__':
    unittest.main()
