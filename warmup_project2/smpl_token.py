import re
from enum import StrEnum

class Keywords:
    def __init__(self):
        self.reserved_token_list = []
        self.__initialize_keywords()

    def __initialize_keywords(self):
        self.reserved_token_list.append(Smpl_Token.Identifier)
        self.reserved_token_list.append(Smpl_Token.Computation)
        self.reserved_token_list.append(Smpl_Token.Var)
        self.reserved_token_list.append(Smpl_Token.Number)
        self.reserved_token_list.append(Smpl_Token.Assignment)
        self.reserved_token_list.append(Smpl_Token.OpenParanthesis)
        self.reserved_token_list.append(Smpl_Token.CloseParanthesis)
        self.reserved_token_list.append(Smpl_Token.Minus)
        self.reserved_token_list.append(Smpl_Token.Plus)
        self.reserved_token_list.append(Smpl_Token.Mul)
        self.reserved_token_list.append(Smpl_Token.Div)
        self.reserved_token_list.append(Smpl_Token.Period)
        self.reserved_token_list.append(Smpl_Token.SemiColon)

class Smpl_Token(StrEnum):
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
