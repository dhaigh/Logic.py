# =============================================================================
# Expressions
# =============================================================================

class Expression:
    def __eq__(self, expr):
        return self.same(expr)

    def get_names(self):
        raise NotImplementedError

    def evaluate(self, var_map):
        raise NotImplementedError

    def equivalent(self, expression):
        names = [n for n in self.get_names() if n in expression.get_names()]

        for row in TruthTable(self).rows_with_map:
            print row
        return True

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

    def __str__(self):
        return self.name

    def get_names(self):
        return [self.name]

    def evaluate(self, var_map):
        return var_map[self.name]

    def same(self, expression):
        return (isinstance(expression, Var) and
                self.name == expression.name)

class Not(Expression):
    symbol = '~'

    def __init__(self, term):
        self.term = term

    def __str__(self):
        return '~%s' % _wrap(self.term)

    def get_names(self):
        return self.term.get_names()

    def evaluate(self, var_map):
        term = self.term.evaluate(var_map)
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

def operator(symbol, rule, two_terms=False):
    class Operation(Expression):
        def __init__(self, *terms):
            self.terms = terms
            if two_terms and len(terms) != 2:
                raise TermError('Wrong number of terms (must be exactly 2)')
            elif len(terms) < 2:
                raise TermError('Not enough terms (must be at least 2)')

        def __str__(self):
            wrap = lambda term: _wrap(term, Operation)
            terms = map(wrap, self.terms)
            return (' %s ' % symbol).join(terms)

        def __getitem__(self, index):
            return self.terms[index]

        def get_names(self):
            names = []
            for term in self.terms:
                for name in term.get_names():
                    if name not in names:
                        names.append(name)
            return sorted(names)

        def evaluate(self, var_map):
            terms = self.terms
            p = terms[0]
            if len(terms) == 2:
                q = terms[1]
            else:
                q = Operation(*terms[1:])

            p = p.evaluate(var_map)
            q = q.evaluate(var_map)
            return rule(p, q)

        def same(self, expression):
            if (not isinstance(expression, Operation) or
                len(self.terms) != len(expression.terms)):
                return False

            expression_terms = list(expression.terms)
            for term in self.terms:
                if term in expression_terms:
                    expression_terms.remove(term)
                else:
                    return False
            return True

    Operation.symbol = symbol
    return Operation

And = operator('^', lambda p, q: p and q)
Or = operator('v', lambda p, q: p or q)
Xor = operator('XOR', lambda p, q: not p is q)
Nand = operator('|', lambda p, q: not (p and q))
Nor = operator('NOR', lambda p, q: not (p or q))
Conditional = operator('->', lambda p, q: not p or q, True)
Biconditional = operator('<->', lambda p, q: p is q, True)

Not.order = 1
And.order = Or.order = Xor.order = Nand.order = Nor.order = 2
Conditional.order = Biconditional.order = 3

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
        if isinstance(expression, str):
            from parse import parse
            expression = parse(expression)
        self.expression = expression
        self.rows = []
        self.rows_with_map = []
        self.values = []
        self.build()

    def __str__(self):
        def row_str(cells):
            tf = {True: 'T', False: 'F'}
            cells = map(lambda x: tf.get(x, x), cells)
            return ' | '.join(cells) + '\n'

        names = self.expression.get_names()
        rows = map(lambda r: r[0] + [r[1]], self.rows)
        output = row_str(names + [str(self.expression)])
        output += ''.join(map(row_str, rows))
        return output

    def build(self):
        names = self.expression.get_names()
        n_vars = len(names)

        for perm in _bool_permutations(n_vars):
            var_map = dict(zip(names, perm))
            value = self.expression.evaluate(var_map)
            self.rows.append((perm, value))
            self.rows_with_map.append((var_map, value))
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


# =============================================================================
# Todo:
# - two expressions equal (truth table), should this or .same be __eq__ ?
# - parser to recognise order of ops
# - better parser exceptions (expected x or y, unexpected `)`, etc)
# - more parser tests
# - more tests for other new properties (.rows_with_map) / methods (same) /
#   exceptions (e.g. TermError)

# FUTURE:
# - show working steps?
# - CLI + GUI
# - simplifier
# - circuit diagram
# - configuration e.g. default symbol, new operations

