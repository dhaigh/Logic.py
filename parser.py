from classes import *
import re

lexer_re = re.compile(r'[a-z]+|[~\^()]|->|<->|(?<= )(?:v|xor)(?= )')
variable_re = re.compile(r'[a-zA-Z]+')

def tokenize(statement):
    return lexer_re.findall(statement)

def isvar(token):
    return variable_re.match(token)

def extract(toks):
    depth = 0
    for i, tok in enumerate(toks):
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
            if depth == 0:
                return toks[1:i]

def parsey(expression):
    tokens = tokenize(expression)
    return parse(tokens)

def parse(tokens):
    tok = tokens[0]

    if isvar(tok):
        p = Var(tok)
        if len(tokens) == 1:
            return p

        #if not isoperation(tok[1]): raise

        op = tokens[1]
        q = parse(tokens[2:])
        return And(p, q)
    elif tok == '~':
        if isvar(tokens[1]):
            return Not(tokens[1])
        return Not(parse(tokens[1:]))
    elif tokens[0] == '(':
        return parse(extract(tokens))
    #else: raise


'''
def nest(tokens):
    tokz = []
    nested = []
    depth = 0

    for tok in tokens:
        if tok == '(':
            depth += 1
        elif tok == ')':
            depth -= 1
            if depth == 0:
                tokz.append(nested)
                nested = []
                continue

        if depth >= 1:
            nested.append(tok)
        else:
            tokz.append(tok)


    print tokz

'''
