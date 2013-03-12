from classes import *
import re

lexer_re = re.compile(r'[a-zA-Z]+|[~\^()\|]|->|<->')
variable_re = re.compile(r'^[a-zA-Z]+$')
op_re = re.compile(r'^(?:[\^v\|]|AND|OR|XOR|NAND|NOR|->|<->)$', re.I)
VAR, OPERATION = range(2)

def tokenize(expression):
    return lexer_re.findall(expression)

def isvar(token):
    return variable_re.match(token)

def isop(token):
    return op_re.match(token)

def error(expected, saw):
    if saw is None:
        saw = 'nothing (end of expression)'
    raise SyntaxError('Expected %s, saw %s' % (expected, saw))

def expect(token_type, token):
    types = {
        OPERATION: (isop, 'an operation'),
        VAR: (isvar, 'a variable')
    }
    type_check, expected = types[token_type]

    if token is None:
        error(expected, None)
    if type_check(token) is None:
        error(expected, token)

def parse(expression):
    return Parser(tokenize(expression)).parse()

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.terms = []
        self.operation = None

    def parse(self):
        read = self.read
        read_term = self.read_term
        next_toks = self.next_toks
        peek = self.peek

        while True:
            read_term()
            if peek() is None:
                break

            symbol = read(OPERATION)
            new_operation = get_operation(symbol)
            if (new_operation is self.operation is Conditional or
                self.operation and self.operation is not new_operation):
                self.terms = [self.operation(*self.terms)]
            self.operation = new_operation

        if self.operation is None:
            return self.terms[0]
        return self.operation(*self.terms)

    def read(self, token_type=None):
        if token_type is None:
            return self.tokens.pop(0)
        token = self.read()
        expect(token_type, token)
        return token

    def peek(self):
        if len(self.tokens) == 0:
            return
        return self.tokens[0]

    def next_toks(self):
        read = self.read
        peek = self.peek
        next_toks = self.next_toks

        depth = 0
        if peek() == '~':
            read()
            return Not(next_toks())
        elif peek() == '(':
            read()
            toks = []
            depth = 1
            while self.tokens:
                tok = read()
                if tok == '(':
                    depth += 1
                elif tok == ')':
                    depth -= 1
                    if depth == 0:
                        break
                toks.append(tok)
            else:
                error('`)`', None)
                
            return Parser(toks).parse()
        elif isvar(peek()):
            return Var(read())
        
    def read_term(self):
        read = self.read
        peek = self.peek
        next_toks = self.next_toks

        if peek() == '~':
            read()
            self.terms.append(Not(next_toks()))
        elif peek() == '(':
            nex = next_toks()
            if isinstance(nex, ONE_TERM_EXPRESSIONS):
                self.terms.append(nex)
            elif self.operation is None or isinstance(nex, self.operation):
                self.terms.extend(nex.terms)
                self.operation = nex.__class__
            else:
                self.terms.append(nex)
        else:
            self.terms.append(Var(read(VAR)))
