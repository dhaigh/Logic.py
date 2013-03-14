#!/usr/bin/env python2

import unittest
from logic.argument import *
from logic.expressions import *
from logic.parse import *

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

# =============================================================================
# Operations
# =============================================================================

def test_operation(t, operation, two_terms=False):
    try:
        operation(p)
    except(TypeError):
        pass
    else:
        t.fail('`TypeError` not raised')

    symbol = operation.symbol
    Xpq = operation(p, q)
    Xpqr = operation(Xpq, r)
    Xrpq = operation(r, Xpq)

    t.assertIs(Xpq[0], p)
    t.assertIs(Xpq[1], q)
    t.assertEquals(str(Xpq), 'p %s q' % symbol)
    if not two_terms:
        t.assertEquals(str(Xpqr), 'p %s q %s r' % (symbol, symbol))
        t.assertEquals(str(Xrpq), 'r %s p %s q' % (symbol, symbol))
    t.assertEquals(Xpq.get_names(), ['p', 'q'])

class TestExpressions(unittest.TestCase):
    def test_tautology(self):
        self.assertTrue(Conditional(And(Conditional(p, q), p), p).is_tautology())
        self.assertTrue(Or(p, Np).is_tautology())
        self.assertTrue(T.is_tautology())

    def test_contradiction(self):
        self.assertTrue(And(p, Np).is_contradiction())
        self.assertTrue(F.is_contradiction())

    def test_equivalence(self):
        self.assertTrue(p.equivalent_to(p))
        self.assertTrue(T.equivalent_to(Or(p, Np)))
        self.assertTrue(F.equivalent_to(And(p, Np)))
        self.assertTrue(parse('p -> q').equivalent_to('~p v q'))
        self.assertTrue(p.equivalent_to('p ^ (p v q)'))
        self.assertTrue(p.equivalent_to('p v (p ^ q)'))
        self.assertTrue(Apq.equivalent_to('p ^ q'))
        self.assertTrue(Apq.equivalent_to('q ^ p'))
        self.assertTrue(Apq.equivalent_to('p ^ p ^ q ^ q'))
        self.assertTrue(p == p == p)
        self.assertTrue(And(p, q) == And(p, q) == Apq)
        self.assertTrue(parse('~(p ^ q)').equivalent_to('~p v ~q'))
        self.assertTrue(parse('~(p ^ q)') == parse('~p v ~q'))
        self.assertFalse(p.equivalent_to(q))
        self.assertFalse(parse('p -> q').equivalent_to('a -> b'))
        self.assertFalse(parse('a ^ b').equivalent_to('a v b'))

    def test_unconditionals(self):
        self.assertTrue(T.evaluate())
        self.assertFalse(F.evaluate())

    def test_var(self):
        self.assertEquals(str(p), 'p')
        self.assertEquals(p.get_names(), ['p'])
        self.assertEquals(p.evaluate({'p': True}), True)
        self.assertEquals(p.evaluate({'p': False}), False)

    def test_not(self):
        symbol = Not.symbol
        self.assertIs(Np.term, p)
        self.assertEquals(str(Np), '~p')
        self.assertEquals(str(Not(Np)), '~~p')
        self.assertEquals(Np.get_names(), ['p'])
        self.assertEquals(Np.evaluate({'p': True}), False)

    def test_and(self):
        test_operation(self, And)
        self.assertEquals(Apq.evaluate(tt), True)
        self.assertEquals(Apq.evaluate(tf), False)
        self.assertEquals(Apq.evaluate(ft), False)
        self.assertEquals(Apq.evaluate(ff), False)

    def test_or(self):
        test_operation(self, Or)
        self.assertEquals(Opq.evaluate(tt), True)
        self.assertEquals(Opq.evaluate(tf), True)
        self.assertEquals(Opq.evaluate(ft), True)
        self.assertEquals(Opq.evaluate(ff), False)

    def test_xor(self):
        test_operation(self, Xor)
        self.assertEquals(Jpq.evaluate(tt), False)
        self.assertEquals(Jpq.evaluate(tf), True)
        self.assertEquals(Jpq.evaluate(ft), True)
        self.assertEquals(Jpq.evaluate(ff), False)

    def test_nand(self):
        try: Nand(p, q, r)
        except(TypeError): pass
        else: self.fail('`TypeError` not raised')
        test_operation(self, Nand)
        self.assertEquals(Dpq.evaluate(tt), False)
        self.assertEquals(Dpq.evaluate(tf), True)
        self.assertEquals(Dpq.evaluate(ft), True)
        self.assertEquals(Dpq.evaluate(ff), True)

    def test_nor(self):
        try: Nor(p, q, r)
        except(TypeError): pass
        else: self.fail('`TypeError` not raised')
        test_operation(self, Nor)
        self.assertEquals(Xpq.evaluate(tt), False)
        self.assertEquals(Xpq.evaluate(tf), False)
        self.assertEquals(Xpq.evaluate(ft), False)
        self.assertEquals(Xpq.evaluate(ff), True)

    def test_conditional(self):
        try: Conditional(p, q, r)
        except(TypeError): pass
        else: self.fail('`TypeError` not raised')
        test_operation(self, Conditional, True)
        self.assertEquals(Cpq.evaluate(tt), True)
        self.assertEquals(Cpq.evaluate(tf), False)
        self.assertEquals(Cpq.evaluate(ft), True)
        self.assertEquals(Cpq.evaluate(ff), True)

    def test_biconditional(self):
        test_operation(self, Biconditional, True)
        self.assertEquals(Epq.evaluate(tt), True)
        self.assertEquals(Epq.evaluate(tf), False)
        self.assertEquals(Epq.evaluate(ft), False)
        self.assertEquals(Epq.evaluate(ff), True)

    def test_stringification(self):
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

# =============================================================================
# Parser
# =============================================================================

def test_parse_exception(t, expression):
    try:
        parse(expression)
    except(SyntaxError):
        pass
    else:
        self.fail('`SyntaxError` not raised')

def test_parse(t, expected, *inputs):
    inputs = map(parse, inputs)
    return t.assertTrue(all(map(expected.equivalent_to, inputs)))

def test_parse_false(t, expected, *inputs):
    inputs = map(parse, inputs)
    return t.assertFalse(any(map(expected.equivalent_to, inputs)))

class TestParser(unittest.TestCase):
    def test_simple(self):
        test_parse(self, p, 'p')
        test_parse(self, Np, '~p')
        test_parse(self, Apq, 'p ^ q', 'p^q', 'p AND q')
        test_parse(self, Opq, 'p v q', 'p OR q')
        test_parse(self, Jpq, 'p XOR q')
        test_parse(self, Dpq, 'p | q', 'p|q', 'p NAND q')
        test_parse(self, Xpq, 'p NOR q')
        test_parse(self, Cpq, 'p -> q', 'p->q')
        test_parse(self, Epq, 'p <-> q', 'p<->q')

    def test_variables(self):
        test_parse(self, Var('Abc'), 'Abc')
        test_parse(self, Var('a1'), 'a1')
        test_parse(self, Var('a_a'), 'a_a')
        test_parse(self, Var('a__10F_'), 'a__10F_')
        test_parse_false(self, Var('a__10F_'), 'a__10F')
        test_parse_false(self, Var('Abc'), 'abc')

    def test_spacing(self):
        test_parse(self, p, '      p',  ' p', '   p    ')
        test_parse(self, Np, '  ~  p  ', ' ~p ', '~   p')
        test_parse(self, Apq, 'p ^q', ' p^  q', ' p ^   q')
        test_parse(self, Nand(Apq, p),
            'p^q|p', '(p^q)NAND p', '  (p  ^q)|p ')

    def test_many_terms(self):
        test_parse(self, And(p, q ,r),
            'p ^ q ^ r', 'p ^ q AND r', 'p AND q AND r',
            '(p ^ q) AND r', '(p ^ q) AND r', 'p ^ (r^q)')

    def test_different_order(self):
        test_parse(self, Or(p, q, r),
            'p v q v r', 'p v r v q', 'q v p v r', 'q v r v p', 'r v p v q', 'r v q v p')
        test_parse(self, And(p, q, r),
            'p ^ q ^ r', 'p ^ r ^ q', 'q ^ p ^ r', 'q ^ r ^ p', 'r ^ p ^ q', 'r ^ q ^ p')
        test_parse(self, Xor(p, q, r),
            'p XOR q XOR r', 'p XOR r XOR q', 'q XOR p XOR r', 'q XOR r XOR p', 'r XOR p XOR q', 'r XOR q XOR p')
        test_parse(self, Biconditional(p, q, r),
            'p <-> q <-> r', 'p <-> r <-> q', 'q <-> p <-> r', 'q <-> r <-> p', 'r <-> p <-> q', 'r <-> q <-> p')

    def test_brackets(self):
        test_parse(self, p, '(p)', '((((p))))')
        test_parse(self, Np, '~(p)', '~(((p)))', '(~(p))')

    def test_nesting(self):
        test_parse(self, Or(p, Apq), 'p v (p ^ q)')
        test_parse(self, Nand(And(Var('p'), Var('q')), Var('p')),
                   'p ^ q | p', '(p ^ q) | p', '(p ^ q) NAND p')
        test_parse(self, Conditional(And(Cpq, p), q),
                   '((p -> q) ^ p) -> q', '((p -> q) AND p) -> q')

    def test_invalid(self):
        test_parse_exception(self, 'a ->')
        test_parse_exception(self, 'a -> b)')
        test_parse_exception(self, 'a -> %')
        test_parse_exception(self, 'a -> % b')
        test_parse_exception(self, 'a % b')
        test_parse_exception(self, 'a ~ b')

# =============================================================================
# Truth Tables
# =============================================================================

tt_p = TruthTable(p)
tt_Apq = TruthTable(Apq)
tt_Apqr = TruthTable(And(Apq, r))

class TestTruthTable(unittest.TestCase):
    def test_init(self):
        self.assertIs(tt_p.expression, p)
        self.assertIs(tt_Apq.expression, Apq)

    def test_values(self):
        t, f = True, False
        self.assertEquals(tt_p.rows, [([t], t), ([f], f)])
        self.assertEquals(tt_Apq.rows, [
            ([t,t], t),
            ([t,f], f),
            ([f,t], f),
            ([f,f], f)
        ])
        self.assertEquals(tt_Apqr.rows, [
            ([t,t,t], t),
            ([t,t,f], f),
            ([t,f,t], f),
            ([t,f,f], f),
            ([f,t,t], f),
            ([f,t,f], f),
            ([f,f,t], f),
            ([f,f,f], f)
        ])
        self.assertEquals(TruthTable(T).rows, [([], t)])
        self.assertEquals(TruthTable(F).rows, [([], f)])

# =============================================================================
# Arguments
# =============================================================================

class TestArguments(unittest.TestCase):
    def test_init(self):
        arg = Argument([p, q, r], r)
        self.assertEquals(arg.propositions, [p, q, r])
        self.assertIs(arg.implication, r)

    def test_validation(self):
        arg1 = Argument([p, q], p)
        arg2 = Argument([p, q, Conditional(Apq, r)], r)
        self.assertIs(arg1.is_valid(), True)
        self.assertIs(arg2.is_valid(), True)
        arg3 = Argument([p], q)
        self.assertIs(arg3.is_valid(), False)

if __name__ == '__main__':
    unittest.main()
