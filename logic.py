#!/usr/bin/env python

import prettytable
import re
import sys

# =============================================================================
# Parser
# =============================================================================

lexer_re = re.compile(r'[a-zA-Z]\w*|[~()]|[^~()\w\s]+')
var_re = re.compile(r'^[a-zA-Z]\w*$')

def tokenize(expr):
    return lexer_re.findall(expr)

def isvar(token):
    if token is None:
        return False
    if var_re.match(token):
        return True
    return False

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
        # wrap brackets around inner nots
        (type(term) is Not and op is not Not) or
        # operations with higher precedence
        (issubclass(op, BinaryOperation) and op.precedence > type(term).precedence)):
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
               'OR', 'v', associative=True)

Xor = operation('Xor', lambda p, q: p is not q, u'\u2295',
                'XOR', associative=True)

Nand = operation('Nand', lambda p, q: not (p and q), u'\u2191',
                 'NAND', '|')

Nor = operation('Nor', lambda p, q: not (p or q), u'\u2193',
                'NOR')

Conditional = operation('Conditional', lambda p, q: not p or q, u'\u2192',
                        '->', '-->', '=>', '==>', precedence=2)

Biconditional = operation('Biconditional', lambda p, q: p is q, u'\u2194',
                          '<->', '<-->', '<=>', '<==>', '=', 'eq', 'XNOR',
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

class TooManyVariablesError(Exception):
    pass

def truth_table(expr):
    expr = parse(expr)
    MAX_VARIABLES = 4
    num_variables = len(expr.get_names())
    if num_variables > MAX_VARIABLES:
        raise TooManyVariablesError(
            '%s variables in expression, maximum of %d allowed'
                % (num_variables, MAX_VARIABLES))
    return TruthTable(expr)

# =============================================================================
# Sample REPL
# =============================================================================

def repl(expr=None):
    if expr is None:
        expr = raw_input('Enter an expression: ')

    print

    try:
        expr = parse(expr)
    except Exception as e:
        print 'Error:', e
    else:
        try:
            tt = truth_table(expr)
        except TooManyVariablesError as e:
            print 'Cannot generate truth table:', e
            print
        else:
            print 'Truth table:'
            print tt

    print '-' * 80

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for expr in sys.argv[1:]:
            repl(expr)

    while 1:
        repl()
