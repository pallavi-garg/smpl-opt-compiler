from .smpl_token import Smpl_Token, Keywords
import re

class Token:
    def __init__(self, id, val, token_type):
        #represents identifier in identifier_table held by tokenizer
        self.id = id
        #represents constant value
        self.val = val
        #type is Smpl_Token
        self.type = token_type
    
    def get_length(self):
        if self.id != None:
            return len(self.id)
        elif self.val != None:
            return len(str(self.val))
        else:
            return len(self.type)
        

class Tokenizer:

    # constructor initialization
    def __init__(self, input_string):
        self.input_string = input_string.strip()
        self.position = 0
        self.input_length = len(self.input_string)
        self.reserved_tokens = Keywords().reserved_token_list
        #represents the token just read
        self.token = None
        self.next()

    def next(self):
        consumed_token = self.token
        if consumed_token != None:
            self.position += consumed_token.get_length()
        if self.position < self.input_length:
            self.tokenize()
        return consumed_token

    #updates self.token
    def tokenize(self):
        while self.position < self.input_length and self.input_string[self.position].isspace():
            self.position += 1
        curr_input_str = self.input_string[self.position:]
        biggest_match_str = ''
        matched_token_type = None
        for keyword in self.reserved_tokens:
            if isinstance(keyword, re.Pattern):
                temp_match = keyword.match(curr_input_str)
                if temp_match and len(temp_match.group(0)) > len(biggest_match_str):
                    biggest_match_str = temp_match.group(0)
                    matched_token_type = keyword
            elif curr_input_str.startswith(keyword) and len(keyword) > len(biggest_match_str):
                biggest_match_str = keyword
                matched_token_type = keyword
        if matched_token_type is None:
            print("Could not tokenize")

        self.token = Token(id=None, val = None, token_type = matched_token_type)
        if matched_token_type == Smpl_Token.Identifier:
            #print("identified " + biggest_match_str)
            self.token.id = biggest_match_str
        elif matched_token_type == Smpl_Token.Number:
            #print("identified number " + biggest_match_str)
            self.token.val = int(biggest_match_str)
        #else:
            #print("identified " + str(matched_token_type))
        




