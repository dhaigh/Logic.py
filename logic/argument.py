from expressions import *

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
