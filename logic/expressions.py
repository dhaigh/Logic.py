from truthtable import *

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
        from parse import parse
        expression = parse(expression)
        return Biconditional(self, expression).is_tautology()

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
