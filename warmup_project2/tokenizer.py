from .token_types import Token_Type
import re

class Token:
    def __init__(self, val, token_type):
    # represents identifier in identifier_table held by tokenizer
        self.id = None
        # represents constant value
        self.val = None
        # type is Token_Type
        self.type = token_type
        match token_type:
            case Token_Type.Identifier:
                self.id = val
            case Token_Type.Number:
                self.val = int(val)
    
    def get_length(self):
        # returns length of token string
        match self.type:
            case Token_Type.Identifier:
                return len(self.id)
            case Token_Type.Number:
                return len(str(self.val))
            case _:
                return len(self.type)
        

class Tokenizer:

    def __init__(self, input_string):
    # constructor initialization
        self.input_string = input_string.strip()
        self.position = 0
        self.input_length = len(self.input_string)
        self.reserved_tokens = Token_Type().get_tokens()
        # represents the token just read
        self.token = None
        self.next()

    def next(self):
    # return current token and tokenize the next token
        token = self.token
        if token != None:
            self.position += token.get_length()
        self.tokenize()
        return token

    def tokenize(self):
    # updates self.token
        while self.position < self.input_length and self.input_string[self.position].isspace():
            self.position += 1
            
        curr_input_str = self.input_string[self.position:]
        biggest_match_str = ''
        matched_token_type = None
        biggest_match_str_len = 0
        for keyword in self.reserved_tokens:
            if isinstance(keyword, re.Pattern):
                temp_match = keyword.match(curr_input_str)
                if temp_match and len(temp_match.group(0)) > biggest_match_str_len:
                    biggest_match_str = temp_match.group(0)
                    biggest_match_str_len = len(biggest_match_str)
                    matched_token_type = keyword
            elif curr_input_str.startswith(keyword) and len(keyword) > biggest_match_str_len:
                biggest_match_str = keyword
                biggest_match_str_len = len(biggest_match_str)
                matched_token_type = keyword

        if matched_token_type:
            self.token = Token(val = biggest_match_str, token_type = matched_token_type)
        else:
            self.token = None
        




