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

def parse(expression):
    return parse_tokens(tokenize(expression))

def parse_tokens(tokens):
    def read(token_type=None):
        if token_type is None:
            return tokens.pop(0)
        token = read()
        expect(token_type, token)
        return token

    def peek():
        if len(tokens) == 0:
            return
        return tokens[0]

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

    terms = []
    symbol = None

    def next_toks():
        depth = 0
        if peek() == '~':
            read()
            return Not(next_toks())
        elif peek() == '(':
            read()
            toks = []
            depth = 1
            while tokens:
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
                
            return parse_tokens(toks)
        elif isvar(peek()):
            return Var(read())
        
        
    def read_term():
        if peek() == '~':
            read()
            terms.append(Not(next_toks()))
        elif peek() == '(':
            terms.append(next_toks())
        else:
            terms.append(Var(read(VAR)))

    while True:
        read_term()
        if peek() is None:
            break
        new_symbol = read(OPERATION)
        if (symbol == new_symbol == '->' or
            symbol and symbol != new_symbol):
            terms = [get_operation(symbol)(*terms)]
        symbol = new_symbol

    if symbol is None:
        return terms[0]
    return get_operation(symbol)(*terms)
