# =============================================================================
# Expressions
# =============================================================================

def _parse(expression):
    if isinstance(expression, str):
        from parse import parse
        expression = parse(expression)
    return expression

class Expression:
    def __eq__(self, expression):
        return self.equivalent_to(expression)

    def __len__(self):
        raise NotImplementedError

    def get_names(self):
        raise NotImplementedError

    def evaluate(self, variables):
        raise NotImplementedError

    def equivalent_to(self, expression):
        expression = _parse(expression)
        return Biconditional(self, expression).is_tautology()

    def same(self, expression):
        raise NotImplementedError

    def is_tautology(self):
        return all(TruthTable(self).values)

    def is_contradiction(self):
        return not any(TruthTable(self).values)

class Unconditional(Expression):
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value

    def __len__(self):
        return 0

    def __str__(self):
        return self.symbol

    def get_names(self):
        return []

    def evaluate(self, _=None):
        return self.value

    def same(self, expression):
        return (isinstance(expression, Unconditional) and
                self.symbol == expression.symbol and
                self.value == expression.value)

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

    def same(self, expression):
        return (isinstance(expression, Var) and
                self.name == expression.name)

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

    def same(self, expression):
        return (isinstance(expression, Not) and
                self.term.same(expression.term))

ONE_TERM_EXPRESSIONS = (Unconditional, Var, Not)

def _wrap(expression, operation=()):
    dont_wrap = ONE_TERM_EXPRESSIONS
    if operation not in (Conditional, Biconditional):
        dont_wrap += (operation,)
    if isinstance(expression, dont_wrap):
        return '%s' % expression
    return '(%s)' % expression

class TermError(Exception):
    pass

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

def operator(symbol, rule, two_terms=False):
    class Operation_(Operation):
        def __init__(self, *terms):
            self.terms = terms
            if two_terms and len(terms) != 2:
                raise TermError('Wrong number of terms (must be exactly 2)')
            elif len(terms) < 2:
                raise TermError('Not enough terms (must be at least 2)')

        def __str__(self):
            wrap = lambda term: _wrap(term, Operation_)
            terms = map(wrap, self.terms)
            return (' %s ' % symbol).join(terms)

        def evaluate(self, variables):
            values = map(lambda t: t.evaluate(variables), self.terms)
            return reduce(rule, values)

        def same(self, expression):
            if (not isinstance(expression, Operation_) or
                len(self.terms) != len(expression.terms)):
                return False

            expression_terms = list(expression.terms)
            for term in self.terms:
                if term in expression_terms:
                    expression_terms.remove(term)
                else:
                    return False
            return True

    Operation_.symbol = symbol
    return Operation_

And = operator('^', lambda p, q: p and q)
Or = operator('v', lambda p, q: p or q)
Xor = operator('XOR', lambda p, q: not p is q)
Nand = operator('|', lambda p, q: not (p and q))
Nor = operator('NOR', lambda p, q: not (p or q))
Conditional = operator('->', lambda p, q: not p or q, True)
Biconditional = operator('<->', lambda p, q: p is q)

def get_operation(symbol):
    operations = {
        'AND': And, '^': And,
        'OR': Or, 'V': Or,
        'XOR': Xor,
        'NAND': Nand, '|': Nand,
        'NOR': Nor,
        '->': Conditional,
        '<->': Biconditional
    }
    symbol = symbol.upper()
    if symbol not in operations:
        raise Exception('Invalid symbol')
    return operations[symbol]


# =============================================================================
# Truth table
# =============================================================================

def _bool_permutations(n):
    if n == 1:
        return [[True], [False]]

    if n <= 0:
        return [[]]

    perms = []
    sub_perms = _bool_permutations(n - 1)
    for value in (True, False):
        for perm in sub_perms:
            perms.append([value] + perm)
    return perms

class TruthTable:
    def __init__(self, expression):
        self.expression = _parse(expression)
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

        for perm in _bool_permutations(n_vars):
            variables = dict(zip(names, perm))
            value = self.expression.evaluate(variables)
            self.rows.append((perm, value))
            self.values.append(value)


# =============================================================================
# Arguments
# =============================================================================

class Argument:
    def __init__(self, propositions, implication):
        self.propositions = propositions
        self.implication = implication

    def is_valid(self):
        if len(self.propositions) == 1:
            p = self.propositions[0]
        else:
            p = And(*self.propositions)
        q = self.implication
        return Conditional(p, q).is_tautology()
