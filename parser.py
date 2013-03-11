from classes import *
import re

lexer_re = re.compile(r'[a-z]+|[~\^()\|]|->|<->|(?<= )(?:v|xor|nor)(?= )')
variable_re = re.compile(r'[a-zA-Z]+')
op_re = re.compile(r'\^|v|XOR|\||NOR|->|<->')

def tokenize(statement):
    return lexer_re.findall(statement)

def isvar(token):
    return variable_re.match(token)

def isop(token):
    return op_re.match(token)

def parsey(expression):
    tokens = tokenize(expression)
    return parse(tokens)

VAR, OPERATION = range(2)

class UnexpectedTokenError(Exception):
    def __init__(self, expected, saw):
        self.expected = expected
        self.saw = saw

    def __str__(self):
        return 'expected %s saw `%s`' % (self.expected, self.saw)

def parse(tokens):
    def read(token_type=None):
        if token_type is not None:
            token = read()
            expect(token_type, token)
            return token

        if len(tokens) == 0:
            return
        return tokens.pop(0)

    def peek():
        if len(tokens) == 0:
            return
        return tokens[0]

    def expect(token_type, token):
        if token is None:
            return
        if token_type == OPERATION:
            if not isop(token):
                raise UnexpectedTokenError('an operation', token)
        elif token_type == VAR:
            if not isvar(token):
                raise UnexpectedTokenError('a variable', token)

    terms = []
    op_symbol = None

    def read_term():
        if peek() == '~':
            read()
            terms.append(Not(Var(read(VAR))))
        else:
            terms.append(Var(read(VAR)))

    while True:
        read_term()

        if peek() is None:
            break

        new_op_symbol = read(OPERATION)
        if op_symbol and op_symbol != new_op_symbol:
            terms = [get_operation(op_symbol)(*terms)]
            op_symbol = new_op_symbol

    return get_operation(op_symbol)(*terms)
