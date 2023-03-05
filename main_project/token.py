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
                self.len = len(val)
            case Token_Type.Number:
                self.val = int(val)
                self.len = len(val)
            case _:
                self.len = len(token_type)
    
    def get_length(self):
        # returns length of token string
        return self.len