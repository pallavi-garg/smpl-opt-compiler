import re

class Token_Type:
    Mul = '*'
    Div = '/'
    Plus = '+'
    Minus = '-'
    Period = '.'
    Assignment = '<-'
    CloseParanthesis = ')'
    OpenParanthesis = '('
    Number = re.compile(r"[0-9]+")
    Identifier = re.compile(r"[a-zA-Z]([a-zA-Z0-9]+)?")
    SemiColon = ';'
    Computation = 'computation'
    Var = 'var'

    def __init__(self):
    # Order is the precendence order in which the tokens should be matched
        self.reserved_token_list = []
        self.reserved_token_list.append(self.OpenParanthesis)
        self.reserved_token_list.append(self.CloseParanthesis)
        self.reserved_token_list.append(self.Minus)
        self.reserved_token_list.append(self.Plus)
        self.reserved_token_list.append(self.Mul)
        self.reserved_token_list.append(self.Div)
        self.reserved_token_list.append(self.Period)
        self.reserved_token_list.append(self.SemiColon)
        self.reserved_token_list.append(self.Assignment)
        self.reserved_token_list.append(self.Var)
        self.reserved_token_list.append(self.Computation)
        self.reserved_token_list.append(self.Number)
        self.reserved_token_list.append(self.Identifier)

    def get_tokens(self):
    # returns list of tokens that are supported by tokenizer
        return self.reserved_token_list