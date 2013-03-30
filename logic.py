#!/usr/bin/env python

import re

# =============================================================================
# Parser
# =============================================================================

lexer_re = re.compile(r'[a-zA-Z]\w*|[~()]|[^\w\s]+')
var_re = re.compile(r'^[a-zA-Z]\w*$')

def tokenize(expression):
    return lexer_re.findall(expression)

def isvar(token):
    if token is None:
        return None
    return var_re.match(token)

def expected(expected, saw=None):
    saw = '`%s`' % saw if saw else 'EOE'
    raise SyntaxError('expected %s, saw %s' % (expected, saw))

def parse(expression):
    if isinstance(expression, Expression):
        return expression
    if isinstance(expression, str):
        expression = tokenize(expression)
    return Parser(expression).parse()

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

        if token == '~':
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
    def __eq__(self, expression):
        if not isinstance(expression, Expression):
            return False
        return self.equivalent(expression)

    def __len__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def get_names(self):
        raise NotImplementedError

    def equivalent(self, expression):
        expression = parse(expression)
        return Biconditional(self, expression).is_tautology()

    def evaluate(self, variables):
        raise NotImplementedError

    def identical(self, expression):
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

    def identical(self, expression):
        expression = parse(expression)
        if not isinstance(expression, Unconditional):
            return False
        return expression.value == self.value

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

    def identical(self, expression):
        expression = parse(expression)
        if not isinstance(expression, Var):
            return False
        return self.name == expression.name

def wrap(term, op=None):
    if (# never put brackets around T/F, p, or ~p
        not isinstance(term, BinaryOperation) or
        # operations with higher precedence
        (op and op.precedence > type(term).precedence) or
        # associative operations of the same type
        (op and op.associative and isinstance(term, op))):
        return '%s' % term
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
        return '%s%s' % (u'\u00ac'.encode('utf-8'), wrap(self.term))

    def get_names(self):
        return self.term.get_names()

    def evaluate(self, variables):
        term = self.term.evaluate(variables)
        return not term

    def identical(self, expression):
        expression = parse(expression)
        if not isinstance(expression, Not):
            return False
        return self.term.identical(expression.term)

class BinaryOperation(Operation):
    def __getitem__(self, index):
        return self.terms[index]

    def __iter__(self):
        for term in self.terms:
            yield term

    def __len__(self):
        return len(self.terms)

    def append(self, term):
        self.terms = self.terms + (term,)

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

    class BinaryOp(BinaryOperation):
        def __init__(self, *terms):
            self.terms = terms
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
            separator = ' %s ' % unicode_symbol.encode('utf-8')
            return separator.join(terms)

        def evaluate(self, variables):
            values = map(lambda t: t.evaluate(variables), self.terms)
            return reduce(rule, values)

        def identical(self, expression):
            expression = parse(expression)
            if not isinstance(expression, BinaryOp) or \
               len(self) != len(expression):
                return False
            for i, term in enumerate(self):
                if not term.identical(expression[i]):
                    return False
            return True

    BinaryOp.__name__ = name
    BinaryOp.associative = associative
    BinaryOp.precedence = precedence

    set_operation(name, BinaryOp)
    for symbol in symbols:
        set_operation(symbol, BinaryOp)

    return BinaryOp

And = operation('And', lambda p, q: p and q, u'\u2227',
                '^', associative=True)

Or = operation('Or', lambda p, q: p or q, u'\u2228',
               'v', associative=True)

Xor = operation('Xor', lambda p, q: p is not q, u'\u2295',
                associative=True)

Nand = operation('Nand', lambda p, q: not (p and q), u'\u2191',
                 '|')

Nor = operation('Nor', lambda p, q: not (p or q), u'\u2193')

Conditional = operation('Conditional', lambda p, q: not p or q, u'\u2192',
                        '->', '-->', precedence=2)

Biconditional = operation('Biconditional', lambda p, q: p is q, u'\u2194',
                          '<->', '<-->', associative=True, precedence=2)

# =============================================================================
# Truth Tables
# =============================================================================

def bool_permutations(n):
    if n == 1:
        return [[True], [False]]

    if n <= 0:
        return [[]]

    perms = []
    sub_perms = bool_permutations(n - 1)
    for value in (True, False):
        for perm in sub_perms:
            perms.append([value] + perm)
    return perms

class TruthTable(object):
    def __init__(self, expression):
        self.expression = parse(expression)
        self.rows = []
        self.values = []
        self.build()

    def __str__(self):
        def row_str(cells):
            tf = {True: 'T', False: 'F'}
            cells = map(lambda x: tf.get(x, x), cells)
            return ' | '.join(cells) + '\n'

        rows = map(lambda r: r[0] + [r[1]], self.rows)
        output = row_str(self.expression.get_names() + [str(self.expression)])
        output += ''.join(map(row_str, rows))
        return output

    def build(self):
        names = self.expression.get_names()
        for perm in bool_permutations(len(names)):
            variables = dict(zip(names, perm))
            value = self.expression.evaluate(variables)
            self.rows.append((perm, value))
            self.values.append(value)

if __name__ == '__main__':
    while 1:
        expr = raw_input('Enter an expression: ')
        print
        print TruthTable(expr)
        print '-' * 80

