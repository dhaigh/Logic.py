#!/usr/bin/env python

import unittest2
from logic import *

p, q, r = Var('p'), Var('q'), Var('r')

Np = Not(p)
Apq = And(p, q)
Opq = Or(p, q)
Jpq = Xor(p, q)
Dpq = Nand(p, q)
Xpq = Nor(p, q)
Cpq = Conditional(p, q)
Epq = Biconditional(p, q)

tt = {'p': True, 'q': True}
tf = {'p': True, 'q': False}
ft = {'p': False, 'q': True}
ff = {'p': False, 'q': False}

def test_operation(t, class_, symbol):
    Xpq = class_(p, q)
    Xpqr = class_(Xpq, r)
    Xrpq = class_(r, Xpq)

    t.assertIs(Xpq.p, p)
    t.assertIs(Xpq.q, q)
    t.assertEquals(str(Xpq), 'p %s q' % symbol)
    t.assertEquals(str(Xpqr), 'p %s q %s r' % (symbol, symbol))
    t.assertEquals(str(Xrpq), 'r %s p %s q' % (symbol, symbol))
    t.assertEquals(Xpq.get_names(), ['p', 'q'])

class TestExpressions(unittest2.TestCase):
    def test_unconditionals(self):
        self.assertTrue(T.evaluate())
        self.assertFalse(F.evaluate())

    def test_var(self):
        self.assertEquals(str(p), 'p')
        self.assertEquals(p.get_names(), ['p'])
        self.assertEquals(p.evaluate({'p': True}), True)
        self.assertEquals(p.evaluate({'p': False}), False)

    def test_not(self):
        self.assertIs(Np.p, p)
        self.assertEquals(str(Np), '~p')
        self.assertEquals(str(Not(Np)), '~~p')
        self.assertEquals(Np.get_names(), ['p'])
        self.assertEquals(Np.evaluate({'p': True}), False)

    def test_and(self):
        test_operation(self, And, '^')
        self.assertEquals(Apq.evaluate(tt), True)
        self.assertEquals(Apq.evaluate(tf), False)
        self.assertEquals(Apq.evaluate(ft), False)
        self.assertEquals(Apq.evaluate(ff), False)

    def test_or(self):
        test_operation(self, Or, 'v')
        self.assertEquals(Opq.evaluate(tt), True)
        self.assertEquals(Opq.evaluate(tf), True)
        self.assertEquals(Opq.evaluate(ft), True)
        self.assertEquals(Opq.evaluate(ff), False)

    def test_xor(self):
        test_operation(self, Xor, 'XOR')
        self.assertEquals(Jpq.evaluate(tt), False)
        self.assertEquals(Jpq.evaluate(tf), True)
        self.assertEquals(Jpq.evaluate(ft), True)
        self.assertEquals(Jpq.evaluate(ff), False)

    def test_nand(self):
        test_operation(self, Nand, '|')
        self.assertEquals(Dpq.evaluate(tt), False)
        self.assertEquals(Dpq.evaluate(tf), True)
        self.assertEquals(Dpq.evaluate(ft), True)
        self.assertEquals(Dpq.evaluate(ff), True)

    def test_nor(self):
        test_operation(self, Nor, 'NOR')
        self.assertEquals(Xpq.evaluate(tt), False)
        self.assertEquals(Xpq.evaluate(tf), False)
        self.assertEquals(Xpq.evaluate(ft), False)
        self.assertEquals(Xpq.evaluate(ff), True)

    def test_conditional(self):
        test_operation(self, Conditional, '->')
        self.assertEquals(Cpq.evaluate(tt), True)
        self.assertEquals(Cpq.evaluate(tf), False)
        self.assertEquals(Cpq.evaluate(ft), True)
        self.assertEquals(Cpq.evaluate(ff), True)

    def test_biconditional(self):
        test_operation(self, Biconditional, '<->')
        self.assertEquals(Epq.evaluate(tt), True)
        self.assertEquals(Epq.evaluate(tf), False)
        self.assertEquals(Epq.evaluate(ft), False)
        self.assertEquals(Epq.evaluate(ff), True)

    def test_complex(self):
        # A=and  O=or  J=xor  D=nand  X=nor  C=cond  E=bicond
        self.assertEquals(str(And(Opq, Jpq)), '(p v q) ^ (p XOR q)')
        self.assertEquals(str(And(Not(Cpq), Or(Not(Dpq), Xpq))),
                '~(p -> q) ^ (~(p | q) v (p NOR q))')
        self.assertEquals(str(
                And(
                  Or(
                    Xor(
                      Nand(
                        Nor(
                          Conditional(
                            Biconditional(p, p),
                            p),
                          p),
                        p),
                      p),
                    p),
                  p)),
                '((((((p <-> p) -> p) NOR p) | p) XOR p) v p) ^ p')
        self.assertEquals(str(And(p, And(q, And(r, And(Nor(p, Nor(q, r)), Not(q)))))),
                'p ^ q ^ r ^ (p NOR q NOR r) ^ ~q')

    # TBC.

if __name__ == '__main__':
    unittest2.main()
