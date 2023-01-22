import smpl_token

class Token:
    def __init__(self, id, number, token_type):
        #represents identifier in identifier_table held by tokenizer
        self.id = id
        #represents constant value
        self.val = number
        #type is Smpl_Token
        self.type = token_type
        self.next()

class tokenizer:

    # constructor initialization
    def __init__(self, input_string):
        self.input_string = input_string.strip()
        self.position = 0
        self.input_length = len(self.input_string)
        self.reserved_tokens = smpl_token.Keywords.reserved_token_list
        #represents the token just read
        self.token = None

    def next(self):
        consumed_token = self.token
        self.tokenize()
        return consumed_token

    def tokenize(self):
        pass