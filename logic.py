import re

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

def wrap(term, op=None):
    if (
        # never put brackets around T/F, p, or ~p
        not isinstance(term, BinaryOperation) or
        # operations with higher precedence
        # (op and op.precedence > type(term).precedence) or
        # associative operations of the same type
        (op and op.associative and
         isinstance(term, op))):
        return '%s' % term
    return '(%s)' % term

class Operation(Expression):
    pass

class Not(Operation):
    symbol = '~'

    def __init__(self, term):
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

class BinaryOperation(Operation):
    def __len__(self):
        return len(self.terms)

    def __getitem__(self, index):
        return self.terms[index]

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
    class Operation_(BinaryOperation):
        def __init__(self, *terms):
            self.terms = list(terms)
            if not associative and len(terms) != 2:
                raise TypeError(('the %s operator only takes 2 ' +
                        'arguments (%d given) because it is not ' +
                        'associative') % (name, len(terms)))
            elif len(terms) < 2:
                raise TypeError('binary operators take at least 2 ' +
                        'arguments (%d given)' % len(terms))

        def __str__(self):
            wrap_ = lambda term: wrap(term, Operation_)
            terms = map(wrap_, self.terms)
            return (' %s ' % symbol).join(terms)

        def evaluate(self, variables):
            values = map(lambda t: t.evaluate(variables), self.terms)
            return reduce(rule, values)

    Operation_.__name__ = name
    Operation_.associative = associative
    Operation_.precedence = precedence
    Operation_.symbol = symbol
    return Operation_

And = operator('And', '^', lambda p, q: p and q, True)
Or = operator('Or', 'v', lambda p, q: p or q, True)
Xor = operator('Xor', 'XOR', lambda p, q: p is not q, True)
Nand = operator('Nand', '|', lambda p, q: not (p and q))
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

class TruthTable(object):
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
        self.terms = []
        self.operation = None

    def read(self):
        if self.tokens:
            return self.tokens.pop(0)
        return None

    def parse(self):
        while True:
            self.terms.append(self.next_term())
            token = self.read()
            if token is None:
                break
            if not isoperation(token):
                expected('an operation or EOE', token)

            op = self.operation
            new_op = get_operation(token)
            if len(self.terms) == 1 and isinstance(self.terms[0], BinaryOperation) and \
                type(self.terms[0]).precedence < new_op.precedence:
                self.terms.append(parse(self.tokens))
                return new_op(*self.terms)
            elif not op:
                self.operation = new_op
            elif new_op.precedence > op.precedence:
                self.terms = [op(*self.terms)]
                self.terms.append(parse(self.tokens))
                return new_op(*self.terms)
            elif op is not new_op:
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
            else:
                expected('an operation or `)`')

            return parse(toks)

        expected('a variable, `~`, or `(`', token)
