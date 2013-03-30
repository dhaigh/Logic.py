#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

Np, Nq, Nr, Ns   = N(p), N(q), N(r), N(s)
Apq, Apqr, Apqrs = A(p, q), A(p, q, r), A(p, q, r, s)
Opq, Opqr, Opqrs = O(p, q), O(p, q, r), O(p, q, r, s)
Jpq, Jpqr, Jpqrs = J(p, q), J(p, q, r), J(p, q, r, s)
Dpq              = D(p, q)
Xpq              = X(p, q)
Cpq              = C(p, q)
Epq, Epqr, Epqrs = E(p, q), E(p, q, r), E(p, q, r, s)

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
        self.assertEqual(len(Jpqrs), 4)
        self.assertEqual(len(Epqrs), 4)

    def test_stringification(self):
        self.assertEqual(str(p), 'p')
        self.assertEqual(str(T), 'T')
        self.assertEqual(str(F), 'F')
        self.assertEqual(str(Np), '¬p')
        self.assertEqual(str(Apq), 'p ∧ q')
        self.assertEqual(str(Opq), 'p ∨ q')
        self.assertEqual(str(Jpq), 'p ⊕ q')
        self.assertEqual(str(Dpq), 'p ↑ q')
        self.assertEqual(str(Xpq), 'p ↓ q')
        self.assertEqual(str(Cpq), 'p → q')
        self.assertEqual(str(Epq), 'p ↔ q')
        self.assertEqual(str(Apqr), 'p ∧ q ∧ r')
        self.assertEqual(str(Opqr), 'p ∨ q ∨ r')
        self.assertEqual(str(Jpqr), 'p ⊕ q ⊕ r')
        self.assertEqual(str(Epqr), 'p ↔ q ↔ r')
        self.assertEqual(str(A(Opq, Jpq)), '(p ∨ q) ∧ (p ⊕ q)')
        self.assertEqual(str(A(N(Cpq), Cpq)), '¬(p → q) ∧ (p → q)')
        self.assertEqual(str(J(Np, O(Epqr, Xpq))),
						 '¬p ⊕ ((p ↔ q ↔ r) ∨ (p ↓ q))')
        self.assertEqual(str(C(Apq, Opqr)), 'p ∧ q → p ∨ q ∨ r')
        self.assertEqual(str(O(C(Apq, p), q, r)), '(p ∧ q → p) ∨ q ∨ r')
        self.assertEqual(str(E(A(p, q, r), Opq)), 'p ∧ q ∧ r ↔ p ∨ q')
        self.assertEqual(str(E(A(Apq, r), Opq)), 'p ∧ q ∧ r ↔ p ∨ q')
        self.assertEqual(str(E(A(Apq, r), Cpq)), 'p ∧ q ∧ r ↔ (p → q)')
        self.assertEqual(str(E(A(Apq, r), O(Cpq, q))), 'p ∧ q ∧ r ↔ (p → q) ∨ q')

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

    def test_equivalence(self):
        self.assertTrue(p.equivalent(p))
        self.assertTrue(T.equivalent(O(p, Np)))
        self.assertTrue(F.equivalent(A(p, Np)))
        self.assertTrue(p.equivalent(N(Np)))
        self.assertTrue(Np.equivalent(N(N(Np))))
        self.assertTrue(p.equivalent(O(p, F)))
        self.assertTrue(p.equivalent(A(p, T)))
        self.assertTrue(T.equivalent(O(p, T)))
        self.assertTrue(F.equivalent(A(p, F)))
        self.assertTrue(Cpq.equivalent(O(Np, q)))
        self.assertTrue(p.equivalent(A(p, Opq)))
        self.assertTrue(p.equivalent(O(p, Apq)))
        self.assertTrue(Apq.equivalent(A(Apq, Apq)))
        self.assertTrue(N(Apq).equivalent(O(Np, Nq)))
        self.assertTrue(Apqr.equivalent(A(r, q, p)))
        self.assertTrue(Opqr.equivalent(O(r, q, p)))
        self.assertTrue(Jpqr.equivalent(J(r, q, p)))
        self.assertTrue(Epqr.equivalent(E(r, q, p)))
        self.assertTrue(A(Apq, r).equivalent(A(p, A(q, r))))
        self.assertTrue(O(Opq, r).equivalent(O(p, O(q, r))))
        self.assertTrue(J(Jpq, r).equivalent(J(p, J(q, r))))
        self.assertFalse(D(Dpq, r).equivalent(D(p, D(q, r))))
        self.assertFalse(X(Xpq, r).equivalent(X(p, X(q, r))))
        self.assertFalse(Cpq.equivalent(C(q, p)))
        self.assertFalse(p.equivalent(q))
        self.assertFalse(Cpq.equivalent(C(r, s)))
        self.assertFalse(Apq.equivalent(Opq))
        self.assertTrue(p != q)
        self.assertTrue(p == N(Np))
        self.assertTrue(p == p == p)
        self.assertTrue(A(p, q) == A(p, q) == Apq)
        self.assertFalse(p == q)

    def test_evaluate(self):
        tt = {'p': True, 'q': True}
        tf = {'p': True, 'q': False}
        ft = {'p': False, 'q': True}
        ff = {'p': False, 'q': False}
        ttt = {'p': True, 'q': True, 'r': True}
        ttf = {'p': True, 'q': True, 'r': False}
        tft = {'p': True, 'q': False, 'r': True}
        tff = {'p': True, 'q': False, 'r': False}
        ftt = {'p': False, 'q': True, 'r': True}
        ftf = {'p': False, 'q': True, 'r': False}
        fft = {'p': False, 'q': False, 'r': True}
        fff = {'p': False, 'q': False, 'r': False}
        # not
        self.assertEqual(Np.evaluate({'p': True}), False)
        self.assertEqual(Np.evaluate({'p': False}), True)
        # and
        self.assertEqual(Apq.evaluate(tt), True)
        self.assertEqual(Apq.evaluate(tf), False)
        self.assertEqual(Apq.evaluate(ft), False)
        self.assertEqual(Apq.evaluate(ff), False)
        self.assertEqual(Apqr.evaluate(ttt), True)
        self.assertEqual(Apqr.evaluate(ttf), False)
        self.assertEqual(Apqr.evaluate(tft), False)
        self.assertEqual(Apqr.evaluate(tff), False)
        self.assertEqual(Apqr.evaluate(ftt), False)
        self.assertEqual(Apqr.evaluate(ftf), False)
        self.assertEqual(Apqr.evaluate(fft), False)
        self.assertEqual(Apqr.evaluate(fff), False)
        # or
        self.assertEqual(Opq.evaluate(tt), True)
        self.assertEqual(Opq.evaluate(tf), True)
        self.assertEqual(Opq.evaluate(ft), True)
        self.assertEqual(Opq.evaluate(ff), False)
        self.assertEqual(Opqr.evaluate(ttt), True)
        self.assertEqual(Opqr.evaluate(ttf), True)
        self.assertEqual(Opqr.evaluate(tft), True)
        self.assertEqual(Opqr.evaluate(tff), True)
        self.assertEqual(Opqr.evaluate(ftt), True)
        self.assertEqual(Opqr.evaluate(ftf), True)
        self.assertEqual(Opqr.evaluate(fft), True)
        self.assertEqual(Opqr.evaluate(fff), False)
        # xor
        self.assertEqual(Jpq.evaluate(tt), False)
        self.assertEqual(Jpq.evaluate(tf), True)
        self.assertEqual(Jpq.evaluate(ft), True)
        self.assertEqual(Jpq.evaluate(ff), False)
        self.assertEqual(Jpqr.evaluate(ttt), True)
        self.assertEqual(Jpqr.evaluate(ttf), False)
        self.assertEqual(Jpqr.evaluate(tft), False)
        self.assertEqual(Jpqr.evaluate(tff), True)
        self.assertEqual(Jpqr.evaluate(ftt), False)
        self.assertEqual(Jpqr.evaluate(ftf), True)
        self.assertEqual(Jpqr.evaluate(fft), True)
        self.assertEqual(Jpqr.evaluate(fff), False)
        # nand
        self.assertEqual(Dpq.evaluate(tt), False)
        self.assertEqual(Dpq.evaluate(tf), True)
        self.assertEqual(Dpq.evaluate(ft), True)
        self.assertEqual(Dpq.evaluate(ff), True)
        # nor
        self.assertEqual(Xpq.evaluate(tt), False)
        self.assertEqual(Xpq.evaluate(tf), False)
        self.assertEqual(Xpq.evaluate(ft), False)
        self.assertEqual(Xpq.evaluate(ff), True)
        # conditional
        self.assertEqual(Cpq.evaluate(tt), True)
        self.assertEqual(Cpq.evaluate(tf), False)
        self.assertEqual(Cpq.evaluate(ft), True)
        self.assertEqual(Cpq.evaluate(ff), True)
        # biconditional
        self.assertEqual(Epq.evaluate(tt), True)
        self.assertEqual(Epq.evaluate(tf), False)
        self.assertEqual(Epq.evaluate(ft), False)
        self.assertEqual(Epq.evaluate(ff), True)
        self.assertEqual(Epqr.evaluate(ttt), True)
        self.assertEqual(Epqr.evaluate(ttf), False)
        self.assertEqual(Epqr.evaluate(tft), False)
        self.assertEqual(Epqr.evaluate(tff), True)
        self.assertEqual(Epqr.evaluate(ftt), False)
        self.assertEqual(Epqr.evaluate(ftf), True)
        self.assertEqual(Epqr.evaluate(fft), True)
        self.assertEqual(Epqr.evaluate(fff), False)
        # multiple
        self.assertEqual(A(p, Opq).evaluate(tt), True)
        self.assertEqual(A(p, Opq).evaluate(tf), True)
        self.assertEqual(A(p, Opq).evaluate(ft), False)
        self.assertEqual(A(p, Opq).evaluate(ff), False)
        self.assertEqual(O(p, Apq).evaluate(tt), True)
        self.assertEqual(O(p, Apq).evaluate(tf), True)
        self.assertEqual(O(p, Apq).evaluate(ft), False)
        self.assertEqual(O(p, Apq).evaluate(ff), False)
        self.assertEqual(C(A(Cpq, p), q).evaluate(tt), True)
        self.assertEqual(C(A(Cpq, p), q).evaluate(tf), True)
        self.assertEqual(C(A(Cpq, p), q).evaluate(ft), True)
        self.assertEqual(C(A(Cpq, p), q).evaluate(ff), True)

    def test_identical(self):
        self.assertTrue(T.identical(T))
        self.assertTrue(F.identical(F))
        self.assertTrue(Apq.identical(Apq))
        self.assertTrue(Apq.identical(A(p, q)))
        self.assertTrue(Opqrs.identical(O(p, q, r, s)))
        self.assertFalse(T.identical(O(p, Np)))
        self.assertFalse(Apqr.identical(A(Apq, r)))
        self.assertFalse(C(p, Opq).identical(C(Opq, p)))
        self.assertFalse(Opq.identical(O(q, p)))
        self.assertFalse(p.identical(Opq))

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
    def test_init(self):
        self.assertEqual(Apq.terms, (p, q))
        self.assertEqual(Opqr.terms, (p, q, r))

    def test_getitem(self):
        self.assertIs(Apq[0], p)
        self.assertIs(Apq[1], q)
        self.assertIs(Apq[-1], q)
        self.assertIs(Apqr[1], q)
        self.assertIs(Apqr[2], r)
        self.assertIs(Apqr[-1], r)
        self.assertIs(Apqr[-2], q)
        self.assertIs(Apqr[-3], p)
        self.assertIs(Dpq[0], p)
        self.assertIs(Dpq[1], q)

    def test_iter(self):
        exprs = [Apq, Jpqr, And(Xpq, Jpqr), And(p, q, r, s, Var('a'))]
        for expr in exprs:
            terms = []
            for term in expr:
                terms.append(term)
            self.assertEqual(tuple(terms), expr.terms)

    def test_append(self):
        exprs = [A(p, q, r, s), J(p, q), X(p, q), C(J(p, q), X(p, s))]
        for expr in exprs:
            x = Var('x')
            expr.append(x)
            self.assertIs(expr.terms[-1], x)

# =============================================================================
# Truth Tables
# =============================================================================

class TestTruthTable(unittest.TestCase):
    def test_values(self):
        tt_p = TruthTable(p)
        tt_Apq = TruthTable(Apq)
        tt_Apqr = TruthTable('p ^ q ^ r')
        tt_Cpq = TruthTable('p -> q')
        t, f = True, False

        self.assertIs(tt_p.expression, p)
        self.assertIs(tt_Apq.expression, Apq)
        self.assertEqual(tt_p.rows, [([t], t), ([f], f)])
        self.assertEqual(tt_Apq.rows, [
            ([t,t], t),
            ([t,f], f),
            ([f,t], f),
            ([f,f], f)
        ])
        self.assertEqual(tt_Apqr.rows, [
            ([t,t,t], t),
            ([t,t,f], f),
            ([t,f,t], f),
            ([t,f,f], f),
            ([f,t,t], f),
            ([f,t,f], f),
            ([f,f,t], f),
            ([f,f,f], f)
        ])
        self.assertEqual(tt_Cpq.rows, [
            ([t,t], t),
            ([t,f], f),
            ([f,t], t),
            ([f,f], t)
        ])
        self.assertEqual(TruthTable(T).rows, [([], t)])
        self.assertEqual(TruthTable(F).rows, [([], f)])
        self.assertEqual(tt_p.values, [t, f])
        self.assertEqual(tt_Apq.values, [t, f, f, f])
        self.assertEqual(tt_Apqr.values, [t, f, f, f, f, f, f, f])
        self.assertEqual(tt_Cpq.values, [t, f, t, t])

# =============================================================================
# Parser
# =============================================================================

class TestParser(unittest.TestCase):
    def test_simple(self):
        self.assertTrue(parse('p').identical(p))
        self.assertTrue(parse('~p').identical(Np))
        self.assertFalse(parse('p').identical(Np))
        self.assertTrue(parse('p AND q').identical(Apq))
        self.assertTrue(parse('p ^ q').identical(Apq))
        self.assertTrue(parse('p OR q').identical(Opq))
        self.assertTrue(parse('p v q').identical(Opq))
        self.assertTrue(parse('p XOR q').identical(Jpq))
        self.assertTrue(parse('p NAND q').identical(Dpq))
        self.assertTrue(parse('p | q').identical(Dpq))
        self.assertTrue(parse('p NOR q').identical(Xpq))
        self.assertTrue(parse('p -> q').identical(Cpq))
        self.assertTrue(parse('p <-> q').identical(Epq))
        self.assertTrue(parse('p ^ q ^ r').identical(Apqr))
        self.assertTrue(parse('p v q v r').identical(Opqr))
        self.assertTrue(parse('p XOR q XOR r').identical(Jpqr))
        self.assertTrue(parse('p <-> q <-> r').identical(Epqr))
        self.assertTrue(parse('p ^ q ^ r ^ s').identical(Apqrs))
        self.assertTrue(parse('p v q v r v s').identical(Opqrs))
        self.assertTrue(parse('p XOR q XOR r XOR s').identical(Jpqrs))
        self.assertTrue(parse('p <-> q <-> r <-> s').identical(Epqrs))

    def test_names(self):
        self.assertTrue(parse('abc').identical(Var('abc')))
        self.assertTrue(parse('Abc').identical(Var('Abc')))
        self.assertFalse(parse('Abc').identical(Var('abc')))
        self.assertTrue(parse('a_b').identical(Var('a_b')))
        self.assertTrue(parse('a1').identical(Var('a1')))

    def test_spacing(self):
        self.assertTrue(parse('       p').identical(p))
        self.assertTrue(parse('p ').identical(p))
        self.assertTrue(parse('     p ').identical(p))
        self.assertTrue(parse(' ~    p ').identical(Np))
        self.assertTrue(parse(' ~p ').identical(Np))
        self.assertTrue(parse('p^q^r').identical(Apqr))
        self.assertTrue(parse('p|q').identical(Dpq))
        self.assertTrue(parse('p->q').identical(Cpq))
        self.assertTrue(parse('p    ->q').identical(Cpq))
        self.assertTrue(parse('p->    q   ').identical(Cpq))
        self.assertTrue(parse(' p   ^q^ r').identical(Apqr))
        self.assertTrue(parse(' p   <->q<-> r').identical(Epqr))
        self.assertTrue(parse('p->~q').identical(C(p, Nq)))
        self.assertTrue(parse('~p->~q').identical(C(Np, Nq)))
        self.assertTrue(parse('~p|~q').identical(D(Np, Nq)))
        self.assertTrue(parse('p->(q)').identical(Cpq))
        self.assertTrue(parse('p->~(q)').identical(C(p, Nq)))
        self.assertTrue(parse('p^~q').identical(A(p, Nq)))
        self.assertTrue(parse('p^~(q)').identical(A(p, Nq)))
        self.assertTrue(parse('(~p)^~q').identical(A(Np, Nq)))
        self.assertTrue(parse('(~p)^~q^(r)').identical(A(Np, Nq, r)))
        self.assertTrue(parse('(p)^~q^(r)').identical(A(p, Nq, r)))
        self.assertTrue(parse('(p)<->~q->(r)').identical(C(E(p, Nq), r)))
        self.assertTrue(parse('~(p)<->~q->~~(r)').identical(C(E(Np, Nq), N(Nr))))

    def test_unconditionals(self):
        self.assertTrue(parse('T').identical(T))
        self.assertTrue(parse('F').identical(F))

    def test_symbol_combination(self):
        self.assertTrue(parse('p^q AND r').identical(Apqr))
        self.assertTrue(parse('p v q OR r').identical(Opqr))
        self.assertTrue(parse('p OR q OR r v s').identical(Opqrs))

    def test_case(self):
        self.assertTrue(parse('p or q Or r oR s').identical(Opqrs))
        self.assertTrue(parse('p aNd q aND r and s').identical(Apqrs))
        self.assertTrue(parse('p XoR q').identical(Jpq))

    def test_combination(self):
        self.assertTrue(parse('p OR q AND r').identical(A(Opq, r)))
        self.assertTrue(parse('p OR q OR r AND s').identical(A(Opqr, s)))
        self.assertTrue(parse('p AND q OR r').identical(O(Apq, r)))

    def test_brackets(self):
        self.assertTrue(parse('(p) v (q) v (r)').identical(Opqr))
        self.assertTrue(parse('((p) v (q) v (r))').identical(Opqr))
        self.assertTrue(parse('((p) v (q)) v (r)').identical(O(Opq, r)))
        self.assertFalse(parse('((p) v (q)) v (r)').identical(Opqr))
        self.assertTrue(parse('(p v q) v r').identical(O(Opq, r)))
        self.assertTrue(parse('((p v q)) v r').identical(O(Opq, r)))
        self.assertFalse(parse('(p v q) v r').identical(Opqr))
        self.assertTrue(parse('(p v q) ^ r').identical(A(Opq, r)))
        self.assertTrue(parse('p v (q ^ r)').identical(O(p, A(q, r))))
        self.assertTrue(parse('(((p)) v (q ^ (r)))').identical(O(p, A(q, r))))
        self.assertTrue(parse('(~(p))').identical(Np))
        self.assertTrue(parse('~(p) v ~(((q) v (r)))').identical(O(Np, N(O(q, r)))))

    def test_precedence(self):
        self.assertTrue(parse('p -> q ^ r').identical(C(p, A(q, r))))
        self.assertTrue(parse('p -> p v q').identical(C(p, O(p, q))))
        self.assertTrue(parse('p -> (q ^ r)').identical(C(p, A(q, r))))
        self.assertTrue(parse('(p -> q) ^ r').identical(A(Cpq, r)))
        self.assertTrue(parse('(p -> q) ^ r ^ s').identical(A(Cpq, r, s)))
        self.assertTrue(parse('(p -> q ^ r) ^ r ^ s').identical(A(C(p, A(q, r)), r, s)))
        self.assertTrue(parse('p v (q -> r ^ s)').identical(O(p, C(q, A(r, s)))))
        self.assertTrue(parse('p -> q <-> r').identical(E(C(p, q), r)))
        self.assertTrue(parse('p <-> q -> r').identical(C(E(p, q), r)))
        self.assertTrue(parse('p -> q <-> r -> s').identical(C(E(C(p, q), r), s)))
        self.assertTrue(parse('p -> q <-> r XOR s XOR p -> s').identical(C(E(C(p, q), J(r, s, p)), s)))
        self.assertTrue(parse('p v q <-> q ^ r <-> s v r v q')
                             .identical(E(O(p, q), A(q, r), O(s, r, q))))
        self.assertTrue(parse('p <-> q ^ r <-> s v r -> r')
                              .identical(C(E(p, A(q, r), O(s, r)), r)))

    def test_nested(self):
        self.assertTrue(parse('((p -> q) -> r) -> s')
                              .identical(
                                  C(
                                    C(
                                      C(p, q),
                                      r
                                    ),
                                    s)))
        self.assertTrue(parse('p -> ((q -> r) -> s)')
                              .identical(
                                  C(
                                    p,
                                    C(
                                      C(q, r),
                                      s))))
        self.assertTrue(parse('p v q | r -> ((q -> r) -> s)')
                              .identical(
                                  C(
                                    D(
                                      O(p, q),
                                      r
                                    ),
                                    C(
                                      C(q, r),
                                      s))))

    def test_ridiculous(self):
        self.assertTrue(parse(
            'p v q v r -> (p <-> r) xor q xor (r ^ (r|p and s)) <-> ~(s v r -> (s <-> r))')
            .identical(
                E(
                  C(
                    O(p, q, r),
                    J(
                      E(p, r),
                      q,
                      A(
                        r,
                        A(
                          D(r, p),
                          s))),
                  ),
                  N(
                    C(
                      O(s, r),
                      E(s, r))))))



# and expecting exceptions?












if __name__ == '__main__':
    unittest.main()
