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
    Begin = '{'
    End = '}'
    OpenBracket = '['
    CloseBracket = ']'
    Number = re.compile(r"[0-9]+")
    Identifier = re.compile(r"[a-zA-Z]([a-zA-Z0-9]+)?")
    Comma = ','
    SemiColon = ';'
    Main = 'main'
    Var = 'var'
    Let = 'let'
    Equals = '=='
    NotEquals = '!='
    LessThan = '<'
    LessThanEqualTo = '<='
    GreaterThan = '>'
    GreaterThanEqualTo = '>='
    Then = 'then'
    If = 'if'
    Fi = 'fi'
    Else = 'else'
    While = 'while'
    Do = 'do'
    Od = 'od'
    Return = 'return'
    Call = 'call'
    Fn_OutputNum = re.compile(r"OutputNum( )*\(")
    Fn_InputNum = re.compile(r"InputNum( )*\(")
    Fn_OutputNewLine = re.compile(r"OutputNewLine( )*\(")
    Array = 'array'


    def __init__(self):
    # Order is the precendence order in which the tokens should be matched
        self.reserved_token_list = []

        #single letter size
        self.reserved_token_list.append(self.OpenParanthesis)
        self.reserved_token_list.append(self.CloseParanthesis)
        self.reserved_token_list.append(self.Begin)
        self.reserved_token_list.append(self.End)
        self.reserved_token_list.append(self.OpenBracket)
        self.reserved_token_list.append(self.CloseBracket)
        self.reserved_token_list.append(self.Minus)
        self.reserved_token_list.append(self.Plus)
        self.reserved_token_list.append(self.Mul)
        self.reserved_token_list.append(self.Div)
        self.reserved_token_list.append(self.Period)
        self.reserved_token_list.append(self.Comma)
        self.reserved_token_list.append(self.SemiColon)
        self.reserved_token_list.append(self.LessThan)
        self.reserved_token_list.append(self.GreaterThan)

        #two letter size
        self.reserved_token_list.append(self.Assignment)
        self.reserved_token_list.append(self.LessThanEqualTo)
        self.reserved_token_list.append(self.GreaterThanEqualTo)
        self.reserved_token_list.append(self.Equals)
        self.reserved_token_list.append(self.NotEquals)
        self.reserved_token_list.append(self.If)
        self.reserved_token_list.append(self.Fi)
        self.reserved_token_list.append(self.Do)
        self.reserved_token_list.append(self.Od)

        #three letter size
        self.reserved_token_list.append(self.Var)
        self.reserved_token_list.append(self.Let)

        #four letter size
        self.reserved_token_list.append(self.Else)
        self.reserved_token_list.append(self.Then)
        self.reserved_token_list.append(self.Call)
        self.reserved_token_list.append(self.Main)

        #bigger
        self.reserved_token_list.append(self.While)
        self.reserved_token_list.append(self.Array)
        self.reserved_token_list.append(self.Return)

        #regex
        self.reserved_token_list.append(self.Number)
        self.reserved_token_list.append(self.Identifier)
        self.reserved_token_list.append(self.Fn_InputNum)
        self.reserved_token_list.append(self.Fn_OutputNum)
        self.reserved_token_list.append(self.Fn_OutputNewLine)

    def get_tokens(self):
    # returns list of tokens that are supported by tokenizer
        return self.reserved_token_list
