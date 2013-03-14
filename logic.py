import re

# =============================================================================
# Expressions
# =============================================================================

class Expression:
    def __eq__(self, expression):
        if not isinstance(expression, Expression):
            return False
        return self.equivalent_to(expression)

    def __len__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def get_names(self):
        raise NotImplementedError

    def evaluate(self, variables):
        raise NotImplementedError

    def equivalent_to(self, expression):
        expression = parse(expression)
        return Biconditional(self, expression).is_tautology()

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

class Not(Expression):
    symbol = '~'

    def __init__(self, term):
        self.term = term

    def __len__(self):
        return 1

    def __str__(self):
        return '~%s' % _wrap(self.term)

    def get_names(self):
        return self.term.get_names()

    def evaluate(self, variables):
        term = self.term.evaluate(variables)
        return not term

def _wrap(expression, operation=()):
    dont_wrap = (Unconditional, Var, Not)
    if operation not in (Conditional, Biconditional):
        dont_wrap += (operation,)
    if isinstance(expression, dont_wrap):
        return '%s' % expression
    return '(%s)' % expression

class Operation(Expression):
    def __len__(self):
        return len(self.terms)

    def __getitem__(self, index):
        return self.terms[index]

    def get_names(self):
        names = []
        for term in self.terms:
            for name in term.get_names():
                if name not in names:
                    names.append(name)
        return sorted(names)

def operator(name, symbol, rule, n_terms=False):
    class Operation_(Operation):
        def __init__(self, *terms):
            self.terms = terms
            if not n_terms and len(terms) != 2:
                raise TypeError(('the `%s` operator takes exactly 2 ' +
                        'arguments (%d given)') % (name, len(terms)))
            elif len(terms) < 2:
                raise TypeError('operators take at least 2 ' +
                        'arguments (%d given)' % len(terms))

        def __str__(self):
            wrap = lambda term: _wrap(term, Operation_)
            terms = map(wrap, self.terms)
            return (' %s ' % symbol).join(terms)

        def evaluate(self, variables):
            values = map(lambda t: t.evaluate(variables), self.terms)
            return reduce(rule, values)

    Operation_.__name__ = name.capitalize()
    Operation_.symbol = symbol
    return Operation_

And = operator('and', '^', lambda p, q: p and q, True)
Or = operator('or', 'v', lambda p, q: p or q, True)
Xor = operator('xor', 'XOR', lambda p, q: not p is q, True)
Nand = operator('nand', '|', lambda p, q: not (p and q))
Nor = operator('nor', 'NOR', lambda p, q: not (p or q))
Conditional = operator('conditional', '->', lambda p, q: not p or q)
Biconditional = operator('biconditional', '<->', lambda p, q: p is q, True)

def get_operation(symbol):
    operations = {
        'and': And, '^': And,
        'or': Or, 'v': Or,
        'xor': Xor,
        'nand': Nand, '|': Nand,
        'nor': Nor,
        '->': Conditional,
        '<->': Biconditional
    }
    symbol = symbol.lower()
    if symbol not in operations:
        raise Exception('Invalid symbol')
    return operations[symbol]

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

class TruthTable:
    def __init__(self, expression):
        self.expression = parse(expression)
        self.variables = self.expression.get_names()
        self.rows = []
        self.values = []
        self.build()

    def __str__(self):
        def row_str(cells):
            tf = {True: 'T', False: 'F'}
            cells = map(lambda x: tf.get(x, x), cells)
            return ' | '.join(cells) + '\n'

        rows = map(lambda r: r[0] + [r[1]], self.rows)
        output = row_str(self.variables + [str(self.expression)])
        output += ''.join(map(row_str, rows))
        return output

    def build(self):
        names = self.expression.get_names()
        n_vars = len(names)

        for perm in bool_permutations(n_vars):
            variables = dict(zip(names, perm))
            value = self.expression.evaluate(variables)
            self.rows.append((perm, value))
            self.values.append(value)

# =============================================================================
# Parser
# =============================================================================

lexer_re = re.compile(r'[a-zA-Z]\w*|[~\^()\|]|->|<->|\S+?')
var_re = re.compile(r'^[a-zA-Z]\w*$')
operation_re = re.compile(r'^(?:[\^v\|]|AND|OR|XOR|NAND|NOR|->|<->)$', re.I)

def tokenize(expression):
	return lexer_re.findall(expression)

def isvar(token):
    if token is None:
        return None
    return var_re.match(token)

def isoperation(token):
    if token is None:
        return None
    return operation_re.match(token)

def expected(expected, saw):
    if saw is None:
        saw = 'EOE'
    else:
        saw = '`%s`' % saw
    raise SyntaxError('expected %s, saw %s' % (expected, saw))

def parse(expression):
    if isinstance(expression, Expression):
        return expression
    return Parser(tokenize(expression)).parse()

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.terms = []
        self.operation = None

    def read(self):
        if self.tokens:
            return self.tokens.pop(0)
        return None

    def parse(self):
        while True:
            term = self.next_term()
            op = self.operation
            if ((op is None and isinstance(term, Operation)) or
                (op and isinstance(term, op))):
                self.terms.extend(term.terms)
                self.operation = op = term.__class__
            else:
                self.terms.append(term)

            token = self.read()
            if token is None:
                break
            if not isoperation(token):
                expected('an operation or EOE', token)

            new_op = get_operation(token)
            if ((op is new_op is Conditional) or
                (op and op is not new_op)):
                self.terms = [op(*self.terms)]
            self.operation = new_op

        if self.operation is None:
            return self.terms[0]
        return self.operation(*self.terms)

    def next_term(self):
        token = self.read()

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
            return Parser(toks).parse()

        expected('a term or expression', token)
