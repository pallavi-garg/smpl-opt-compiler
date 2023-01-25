"""
Parser for grammar defined in ../grammars/arithmetic_grammar_with_variables.txt

"""

from .tokenizer import Tokenizer
from .token_types import Token_Type

class Parser:
    
    def __init__(self, input_string):
    # constructor initialization
        self.tokenizer = Tokenizer(input_string)
        self.symbol_table = {}
    
    def computation(self):
    # entry point for this parser
        self.__consume(Token_Type.Computation)
        while self.tokenizer.token and self.tokenizer.token.type == Token_Type.Var:
            self.__variable_declaration()
        print(self.__expression())
        while self.tokenizer.token and self.tokenizer.token.type == Token_Type.SemiColon:
            self.__consume(Token_Type.SemiColon)
            print(self.__expression())
        self.__consume(Token_Type.Period)

    def __look_up(self, id):
    # returns value of variable with id
        if(id not in self.symbol_table):
           self. __syntax_error("Undefined identifier - " + id)
        return self.symbol_table[id]
    
    def __insert_identifier(self, id):
        self.symbol_table[id] = 0
    
    def __insert_identifier(self, id, value):
        self.symbol_table[id] = value

    def __consume(self, tokenType):
    # tokenType - Token_Type
        consumed_token = self.tokenizer.next()
        if(consumed_token == None or consumed_token.type != tokenType):
            self.__syntax_error(tokenType + " type not found")
        return consumed_token
        
    def __variable_declaration(self):
    # handle variable declaration
        self.__consume(Token_Type.Var)
        if self.tokenizer.token and self.tokenizer.token.type == Token_Type.Identifier:
            id = self.tokenizer.token.id
            self.__consume(Token_Type.Identifier)
            self.__consume(Token_Type.Assignment)
            self.__insert_identifier(id, self.__expression())
            self.__consume(Token_Type.SemiColon)
        else:
             self.__syntax_error("Expected identifier but not found")

    def __expression(self):
    # calculate expression
        val = self.__term()
        while self.tokenizer.token and self.tokenizer.token.type in [Token_Type.Plus, Token_Type.Minus]:
            token_type = self.tokenizer.token.type
            self.__consume(token_type)
            val = self.__perform_operation(token_type, val, self.__term())
        return val

    def __term(self):
    # calculate term
        val = self.__factor()
        while self.tokenizer.token and self.tokenizer.token.type in [Token_Type.Mul, Token_Type.Div]:
            token_type = self.tokenizer.token.type
            self.__consume(token_type)
            val = self.__perform_operation(token_type, val, self.__factor())
        return val

    def __factor(self):
    # calculates factor
        val = 0
        if self.tokenizer.token:
            if self.tokenizer.token.type == Token_Type.OpenParanthesis:
                self.__consume(Token_Type.OpenParanthesis)
                val = self.__expression()
                if self.tokenizer.token and self.tokenizer.token.type == Token_Type.CloseParanthesis:
                    self.__consume(Token_Type.CloseParanthesis)
                else:
                    self.__syntax_error("Expected ) but not found")
            elif self.tokenizer.token.type == Token_Type.Number:
                val = self.tokenizer.token.val
                self.__consume(Token_Type.Number)
            elif self.tokenizer.token.type == Token_Type.Identifier:
                val = self.__look_up(self.tokenizer.token.id)
                self.__consume(Token_Type.Identifier)
        else:
            self.__syntax_error("Syntax error in factor")
        return val

    def __perform_operation(self, token_type, first_operand, second_operand):
    # performs arithmatic operation based on token_type
        match token_type:
            case Token_Type.Plus:
                return first_operand + second_operand
            case Token_Type.Minus:
                return first_operand - second_operand
            case Token_Type.Mul:
                return first_operand * second_operand
            case Token_Type.Div:
                return first_operand / second_operand

    def __syntax_error(self, error):
    # throws exception
        raise Exception("Syntax Error: " + error)



    
    

