#!/usr/bin/env python

import re
import prettytable

# =============================================================================
# Parser
# =============================================================================

lexer_re = re.compile(r'[a-zA-Z]\w*|[~()]|[^~()\w\s]+')
var_re = re.compile(r'^[a-zA-Z]\w*$')

def tokenize(expr):
    return lexer_re.findall(expr)

def isvar(token):
    if token is None:
        return None
    return var_re.match(token)

def expected(expected, saw=None):
    saw = '`%s`' % saw if saw else 'EOE'
    raise SyntaxError('expected %s, saw %s' % (expected, saw))

def parse(expr):
    if isinstance(expr, Expression):
        return expr
    if isinstance(expr, str):
        expr = tokenize(expr)
    return Parser(expr).parse()

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.terms = []

    def read(self):
        if self.tokens:
            return self.tokens.pop(0)
        return None

    def parse(self, max_precedence=None):
        op = None

        while True:
            toks = list(self.tokens)
            term = self.next_term()
            token = self.read()

            if token is None:
                if op is None:
                    return term
                self.terms.append(term)
                return op(*self.terms)

            next_op = get_operation(token)

            if next_op is None:
                expected('an operation or EOE', token)

            if max_precedence and next_op.precedence >= max_precedence:
                self.tokens.insert(0, token)
                self.terms.append(term)
                return op(*self.terms)

            if op and op.precedence > next_op.precedence:
                p = Parser(toks)
                self.terms.append(p.parse(op.precedence))
                self.tokens = p.tokens
                if not self.tokens:
                    return op(*self.terms)
                next_op = get_operation(self.read())
                if op is not next_op:
                    self.terms = [op(*self.terms)]
            else:
                self.terms.append(term)
                if op and op is not next_op:
                    self.terms = [op(*self.terms)]
            op = next_op

    def next_term(self):
        token = self.read()

        if token == 'T':
            return T
        if token == 'F':
            return F

        if isvar(token):
            return Var(token)

        if token == '~' or token == u'\u00ac'.encode('utf-8'):
            return Not(self.next_term())

        if token == '(':
            toks, depth = [], 1
            while self.tokens:
                tok = self.read()
                if tok == '(':
                    depth += 1
                elif tok == ')':
                    if depth == 1:
                        break
                    depth -= 1
                toks.append(tok)
            else:
                expected('an operation or `)`')

            return parse(toks)

        expected('a variable, unconditional, `~`, or `(`', token)

# =============================================================================
# Expression Classes
# =============================================================================

class Expression(object):
    def __eq__(self, expr):
        if not isinstance(expr, Expression):
            return False
        return self.equivalent(expr)

    def __len__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def get_names(self):
        raise NotImplementedError

    def equivalent(self, expr):
        expr = parse(expr)
        return Biconditional(self, expr).is_tautology()

    def evaluate(self, variables):
        raise NotImplementedError

    def identical(self, expr):
        raise NotImplementedError

    def is_contradiction(self):
        return not any(TruthTable(self).values)

    def is_tautology(self):
        return all(TruthTable(self).values)

class Unconditional(Expression):
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def __len__(self):
        return 1

    def __str__(self):
        return self.symbol

    def get_names(self):
        return []

    def evaluate(self, _=None):
        return self.value

    def identical(self, expr):
        expr = parse(expr)
        if not isinstance(expr, Unconditional):
            return False
        return expr.value == self.value

T = Unconditional('T', True)
F = Unconditional('F', False)

class Var(Expression):
    def __init__(self, name):
        self.name = name

    def __len__(self):
        return 1

    def __str__(self):
        return self.name

    def get_names(self):
        return [self.name]

    def evaluate(self, variables):
        return variables[self.name]

    def identical(self, expr):
        expr = parse(expr)
        if not isinstance(expr, Var):
            return False
        return self.name == expr.name

def wrap(term, op):
    if (# never put brackets around T/F or p
        isinstance(term, (Unconditional, Var)) or
        (type(term) is Not and op is not Not) or
        # operations with higher precedence
        (isinstance(op, BinaryOperation) and op.precedence > type(term).precedence)):
        return str(term)
    return '(%s)' % term

class Operation(Expression):
    pass

class Not(Operation):
    def __init__(self, term):
        term = parse(term)
        self.term = term

    def __len__(self):
        return 1

    def __str__(self):
        return '\xc2\xac' + wrap(self.term, Not)

    def get_names(self):
        return self.term.get_names()

    def evaluate(self, variables):
        term = self.term.evaluate(variables)
        return not term

    def identical(self, expr):
        expr = parse(expr)
        if not isinstance(expr, Not):
            return False
        return self.term.identical(expr.term)

class BinaryOperation(Operation):
    def __getitem__(self, index):
        return self.terms[index]

    def __iter__(self):
        for term in self.terms:
            yield term

    def __len__(self):
        return len(self.terms)

    def append(self, term):
        self.terms.append(term)

    def get_names(self):
        names = []
        for term in self:
            for name in term.get_names():
                if name not in names:
                    names.append(name)
        return sorted(names)

operations = {}

def get_operation(symbol):
    symbol = symbol.upper()
    if symbol not in operations:
        return None
    return operations[symbol]

def set_operation(symbol, operation):
    symbol = symbol.upper()
    operations[symbol] = operation

def operation(name, rule, unicode_symbol, *symbols, **kwargs):
    associative = kwargs.get('associative', False)
    precedence = kwargs.get('precedence', 1)
    unicode_symbol = unicode_symbol.encode('utf-8')

    class BinaryOp(BinaryOperation):
        def __init__(self, *terms):
            self.terms = list(terms)
            if len(terms) < 2:
                raise TypeError('binary operators take at least 2 ' +
                        'arguments (%d given)' % len(terms))
            if not associative and len(terms) > 2:
                raise TypeError(('the %s operator only takes 2 ' +
                        'arguments (%d given) because it is not ' +
                        'associative') % (name, len(terms)))

        def __str__(self):
            wrap_ = lambda t: wrap(t, BinaryOp)
            terms = map(wrap_, self.terms)
            separator = ' %s ' % unicode_symbol
            return separator.join(terms)

        def evaluate(self, variables):
            values = map(lambda t: t.evaluate(variables), self.terms)
            return reduce(rule, values)

        def identical(self, expr):
            expr = parse(expr)
            if not isinstance(expr, BinaryOp) or \
               len(self) != len(expr):
                return False
            for i, term in enumerate(self):
                if not term.identical(expr[i]):
                    return False
            return True

    BinaryOp.__name__ = name
    BinaryOp.associative = associative
    BinaryOp.precedence = precedence

    set_operation(unicode_symbol, BinaryOp)
    for symbol in symbols:
        set_operation(symbol, BinaryOp)

    return BinaryOp

And = operation('And', lambda p, q: p and q, u'\u2227',
                'AND', '^', associative=True)

Or = operation('Or', lambda p, q: p or q, u'\u2228',
               'OR', 'v', '||', associative=True)

Xor = operation('Xor', lambda p, q: p is not q, u'\u2295',
                'XOR', associative=True)

Nand = operation('Nand', lambda p, q: not (p and q), u'\u2191',
                 'NAND', '|')

Nor = operation('Nor', lambda p, q: not (p or q), u'\u2193',
                'NOR')

Conditional = operation('Conditional', lambda p, q: not p or q, u'\u2192',
                        '->', '-->', '=>', '==>', precedence=2)

Biconditional = operation('Biconditional', lambda p, q: p is q, u'\u2194',
                          '<->', '<-->', '<=>', '<==>', '=', '==', 'eq',
                          associative=True, precedence=3)

# =============================================================================
# Truth Tables
# =============================================================================

def bool_permutations(n):
    if n == 1:
        return [[True], [False]]

    if n <= 0:
        return [[]]

    perms = []
    sub_perms = bool_permutations(n-1)
    for value in (True, False):
        for perm in sub_perms:
            perms.append([value] + perm)
    return perms

class TruthTable(prettytable.Table):
    def __init__(self, expr):
        expr = parse(expr)
        names = expr.get_names()
        header = names + [str(expr)]
        super(TruthTable, self).__init__(header)

        self.expression = expr
        self.values = []

        for perm in bool_permutations(len(names)):
            variables = dict(zip(names, perm))
            value = expr.evaluate(variables)
            self.append(perm + [value])
            self.values.append(value)

# =============================================================================
# Simplifier
# =============================================================================

def unconditionals(expr):
    if isinstance(expr, And):
        for term in expr:
            if term is F:
                return F
        if T not in expr:
            return expr
        terms = list(expr.terms)
        while T in terms:
            terms.remove(T)
        if len(terms) == 0:
            return T
        if len(terms) == 1:
            return terms[0]
        return And(*terms)
    if isinstance(expr, Or):
        for term in expr:
            if term is T:
                return T
        if F not in expr:
            return expr
        terms = list(expr.terms)
        while F in terms:
            terms.remove(F)
        if len(terms) == 0:
            return F
        if len(terms) == 1:
            return terms[0]
        return Or(*terms)
    return expr

def negate_unconditional(expr):
    if isinstance(expr, Not):
        if expr.term is T:
            return F
        if expr.term is F:
            return T
        return expr
    return expr

def double_negative(expr):
    if isinstance(expr, Not) and \
       isinstance(expr.term, Not):
        return expr.term.term
    return expr

def implication(expr):
    if isinstance(expr, Conditional):
        return Or(Not(expr[0]), expr[1])
    return expr

def double_implication(expr):
    if isinstance(expr, Biconditional):
        if len(expr) == 2:
            return And(Conditional(expr[0], expr[1]),
                       Conditional(expr[1], expr[0]))
        terms = list(expr.terms)
        simple = Biconditional(terms.pop(0), terms.pop(0))
        while terms:
            simple = Biconditional(simple, terms.pop(0))
        return simple
    return expr

def nand_nor(expr):
    if isinstance(expr, Nand):
        return Not(And(*expr.terms))
    if isinstance(expr, Nor):
        return Not(Or(*expr.terms))
    return expr

def not_expand(expr):
    if isinstance(expr, Not) and \
       isinstance(expr.term, (And, Or)):
        terms = list(expr.term.terms)
        terms = map(Not, terms)
        return type(expr.term)(*terms)
    return expr

def distributive(expr):
    if not isinstance(expr, (And, Or)):
        return expr
    # investigate this..
    if len(expr) > 2:
        return expr
    term1, term2 = expr[0], expr[1]
    op_outer = type(expr)
    return expr

rules = [
    unconditionals,
    negate_unconditional,
    double_negative,
    implication,
    double_implication,
    nand_nor,
    not_expand,
    distributive
]

def simplify(expr):
    for rule in rules:
        new = rule(expr)
        if not new.identical(expr):
            return new

    if not isinstance(expr, Operation):
        return expr

    if isinstance(expr, Not):
        term = simplify(expr.term)
        new = Not(term)
        if not new.identical(expr):
            return new
    else:
        terms = list(expr.terms)
        for i, term in enumerate(terms):
            terms[i] = simplify(term)
        new = type(expr)(*terms)
        if not new.identical(expr):
            return new

    return expr

def simplification_steps(expr):
    expr = parse(expr)

    simpler = simplify(expr)
    if simpler is not expr:
        return [expr] + simplification_steps(simpler)

    return [expr]

# =============================================================================
# Sample REPL
# =============================================================================

if __name__ == '__main__':
    while 1:
        expr = raw_input('Enter an expression: ')
        print

        try:
            expr = parse(expr)
        except Exception as e:
            print 'Error:', e
        else:
            print 'Truth table:'
            print TruthTable(expr)
            print 'Simplification steps:'
            for n, simple in enumerate(simplification_steps(expr), 1):
                print n, simple

        print '-' * 80

