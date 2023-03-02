from .token_types import Token_Type

class Token:
    def __init__(self, val, token_type):
    # represents identifier in identifier_table held by tokenizer
        self.id = None
        # represents constant value
        self.val = None
        # type is Token_Type
        self.type = token_type
        match token_type:
            case Token_Type.Identifier | \
                 Token_Type.Fn_OutputNum | \
                 Token_Type.Fn_InputNum | \
                 Token_Type.Fn_OutputNewLine:
                self.id = val
            case Token_Type.Number:
                self.val = int(val)
    
    def get_length(self):
        # returns length of token string
        match self.type:
            case Token_Type.Identifier | \
                 Token_Type.Fn_OutputNum | \
                 Token_Type.Fn_InputNum | \
                 Token_Type.Fn_OutputNewLine:
                return len(self.id)
            case Token_Type.Number:
                return len(str(self.val))
            case _:
                return len(self.type)