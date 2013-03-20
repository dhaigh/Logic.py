import re

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

def expected(expected, saw=None):
    saw = 'EOE' if saw is None else '`%s`' % saw
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
        self.i = 0
        self.terms = []

    def read(self):
        if self.i < len(self.tokens):
            self.i += 1
            return self.tokens[self.i-1]
        return None

    def parse(self, final_op=None):
        op = None

        while True:
            term = self.next_term()
            token = self.read()

            if term is None or token is None:
                if op is None:
                    return term
                if term:self.terms.append(term)
                return op(*self.terms)

            if not isoperation(token):
                expected('an operation or EOE', token)

            next_op = get_operation(token)

            if final_op and next_op.precedence >= final_op.precedence:
                return 1

            if op:
                if op is next_op:
                    self.terms.append(term)
                    op = next_op
                elif next_op.precedence < op.precedence:
                    ghost = Parser(self.tokens)
                    ghost.i = self.i - 2
                    self.terms.append(next_op(*ghost.parse(op)))
                    self.i = ghost.i
                else:
                    self.terms.append(term)
                    self.terms = [op(*self.terms)]
                    op = next_op
            else:
                self.terms.append(term)
                op = next_op


    def next_term(self):
        token = self.read()

        if token is None:
            return None

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

        expected('a variable, `~`, or `(`', token)

# =============================================================================
# Expressions
# =============================================================================

class Expression(object):
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

    def equivalent_to(self, expression):
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
        if not isinstance(expression, Var):
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
    symbol = '~'

    def __init__(self, term):
        term = parse(term)
        self.term = term

    def __len__(self):
        return 1

    def __str__(self):
        return '~%s' % wrap(self.term)

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
        self.terms.append(term)

    def get_names(self):
        names = []
        for term in self.terms:
            for name in term.get_names():
                if name not in names:
                    names.append(name)
        return sorted(names)

def operator(name, symbol, rule, associative=False, precedence=1):
    class BinaryOp(BinaryOperation):
        def __init__(self, *terms):
            self.terms = list(terms) #map(parse, terms)
            if len(terms) < 2:
                raise TypeError('binary operators take at least 2 ' +
                        'arguments (%d given)' % len(terms))
            if not associative and len(terms) > 2:
                raise TypeError(('the %s operator only takes 2 ' +
                        'arguments (%d given) because it is not ' +
                        'associative') % (name, len(terms)))

        def __str__(self):
            wrap_ = lambda term: wrap(term, BinaryOp)
            terms = map(wrap_, self.terms)
            return (' %s ' % symbol).join(terms)

        def evaluate(self, variables):
            values = map(lambda t: t.evaluate(variables), self.terms)
            return reduce(rule, values)

        def identical(self, expression):
            expression = parse(expression)
            if (not isinstance(expression, BinaryOp) or
                len(self) != len(expression)):
                return False
            for i, term in enumerate(self):
                if not term.identical(expression[i]):
                    return False
            return True

    BinaryOp.__name__ = name
    BinaryOp.associative = associative
    BinaryOp.precedence = precedence
    BinaryOp.symbol = symbol
    return BinaryOp

And = operator('And', '^', lambda p, q: p and q, True)
Or = operator('Or', 'v', lambda p, q: p or q, True)
Xor = operator('Xor', 'XOR', lambda p, q: p is not q, True)
Nand = operator('Nand', 'NAND', lambda p, q: not (p and q))
Nor = operator('Nor', 'NOR', lambda p, q: not (p or q))
Conditional = operator('Conditional', '->', lambda p, q: not p or q, False, 2)
Biconditional = operator('Biconditional', '<->', lambda p, q: p is q, True, 2)

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

class TruthTable(object):
    def __init__(self, expression):
        self.expression = parse(expression)
        self.names = self.expression.get_names()
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
        for perm in bool_permutations(len(self.names)):
            variables = dict(zip(self.names, perm))
            value = self.expression.evaluate(variables)
            self.rows.append((perm, value))
            self.values.append(value)

