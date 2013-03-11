from classes import *
import re

lexer_re = re.compile(r'[a-zA-Z]+|[~\^()\|]|->|<->')
variable_re = re.compile(r'[a-zA-Z]+')
op_re = re.compile(r'\^|v|XOR|\||NOR|->|<->')

def tokenize(expression):
    return lexer_re.findall(expression)

def isvar(token):
    return variable_re.match(token)

def isop(token):
    return op_re.match(token)

VAR, OPERATION = range(2)

def error(expected, saw):
    raise SyntaxError('Expected %s, saw %s' % (expected, saw))

def parse(expression):
    return parse_tokens(tokenize(expression))

def parse_tokens(tokens):
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
        types = {
            OPERATION: (isop, 'an operation'),
            VAR: (isvar, 'a variable')
        }
        type_check, noun = types[token_type]

        if token is None:
            error(noun, 'nothing (end of expression)')

        if not type_check(token):
            error(noun, token)

    terms = []
    symbol = None

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

        new_symbol = read(OPERATION)
        if symbol and symbol != new_symbol:
            terms = [get_operation(symbol)(*terms)]
        symbol = new_symbol

    if symbol is None:
        return terms[0]
    return get_operation(symbol)(*terms)
