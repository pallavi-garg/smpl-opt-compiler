"""
Parser for grammar defined in ../grammars/arithmetic_grammar_with_variables.txt

"""

from .tokenizer import Tokenizer
from .smpl_token import Smpl_Token

class Parser:
    
    # constructor initialization
    def __init__(self, input_string):
        self.tokenizer = Tokenizer(input_string)
        self.symbol_table = {}

    def __look_up(self, id):
        return self.symbol_table[id]

    #tokenType - Smpl_Token
    def __consume(self, tokenType):
        consumed_token = self.tokenizer.next()
        if(consumed_token == None or consumed_token.type != tokenType):
            print(tokenType + " not found!")
        return consumed_token
    
    # entry point for this parser
    def computation(self):
        self.__consume(Smpl_Token.Computation)
        while self.tokenizer.token and self.tokenizer.token.type == Smpl_Token.Var:
            self.__variable_declaration()
        print(self.__expression())
        while self.tokenizer.token and self.tokenizer.token.type == Smpl_Token.SemiColon:
            self.__consume(Smpl_Token.SemiColon)
            print(self.__expression())
        self.__consume(Smpl_Token.Period)
        
    def __variable_declaration(self):
        self.__consume(Smpl_Token.Var)
        if self.tokenizer.token and self.tokenizer.token.type == Smpl_Token.Identifier:
            id = self.tokenizer.token.id
            self.__consume(Smpl_Token.Identifier)
            self.__consume(Smpl_Token.Assignment)
            self.symbol_table[id] = self.__expression()
            self.__consume(Smpl_Token.SemiColon)
        else:
             print("Expected identifier but not found")

    # calculates expression
    def __expression(self):
        val = self.__term()
        while self.tokenizer.token and (self.tokenizer.token.type == Smpl_Token.Plus or self.tokenizer.token.type == Smpl_Token.Minus):
            token_type = self.tokenizer.token.type
            self.__consume(token_type)
            val = self.__perform_operation(token_type, val, self.__term())
        return val

    # calculates term
    def __term(self):
        val = self.__factor()
        while self.tokenizer.token and (self.tokenizer.token.type == Smpl_Token.Mul or self.tokenizer.token.type == Smpl_Token.Div):
            token_type = self.tokenizer.token.type
            self.__consume(token_type)
            val = self.__perform_operation(token_type, val, self.__factor())
        return val

    # calculates factor
    def __factor(self):
        val = 0
        if self.tokenizer.token:
            if self.tokenizer.token.type == Smpl_Token.OpenParanthesis:
                self.__consume(Smpl_Token.OpenParanthesis)
                val = self.__expression()
                if self.tokenizer.token and self.tokenizer.token.type == Smpl_Token.CloseParanthesis:
                    self.__consume(Smpl_Token.CloseParanthesis)
                else:
                    print("Expected ) but not found")
            elif self.tokenizer.token.type == Smpl_Token.Number:
                val = self.tokenizer.token.val
                self.__consume(Smpl_Token.Number)
            elif self.tokenizer.token.type == Smpl_Token.Identifier:
                val = self.__look_up(self.tokenizer.token.id)
                self.__consume(Smpl_Token.Identifier)
        else:
            print("Syntax error in factor")
        return val

    def __perform_operation(self, token_type, first_operand, second_operand):
        match token_type:
            case Smpl_Token.Plus:
                return first_operand + second_operand
            case Smpl_Token.Minus:
                return first_operand - second_operand
            case Smpl_Token.Mul:
                return first_operand * second_operand
            case Smpl_Token.Div:
                return first_operand / second_operand



    
    

