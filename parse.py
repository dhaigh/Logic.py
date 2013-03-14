from classes import *
import re

lexer_re = re.compile(r'[a-zA-Z]\w*|[~\^()\|]|->|<->|[^\s]+?')
variable_re = re.compile(r'^[a-zA-Z]\w*$')
op_re = re.compile(r'^(?:[\^v\|]|AND|OR|XOR|NAND|NOR|->|<->)$', re.I)

def tokenize(expression):
	return lexer_re.findall(expression)		

def isvar(token):
    if token is None:
        return None
    return variable_re.match(token)

def isop(token):
    if token is None:
        return None
    return op_re.match(token)

def expected(expected, saw):
    if saw is None:
        saw = 'EOE'
    else:
        saw = '`%s`' % saw
    raise SyntaxError('Expected %s, saw %s' % (expected, saw))

def parse(expression):
    return Parser(tokenize(expression)).parse()

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.terms = []
        self.operation = None

    def read(self):
        if len(self.tokens) == 0:
            return None
        return self.tokens.pop(0)

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
            if not isop(token):
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

        expected('a term', token)
