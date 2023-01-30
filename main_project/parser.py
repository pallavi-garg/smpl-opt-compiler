"""
Parser for grammar defined in ../grammars/smpl_grammar.txt

"""

from .tokenizer import Tokenizer
from .token_types import Token_Type

class Parser:
    
    statement_starter = [Token_Type.Let, Token_Type.If, Token_Type.While, Token_Type.Return, Token_Type.Call]

    def __init__(self, input_string):
    # constructor initialization
        self.tokenizer = Tokenizer(input_string)
        self.symbol_table = {}
        self.uninitialized_variables = {}
        self.results = []
        self.warnings = []

    def parse(self):
    # entry point for this parser
        self.__consume(Token_Type.Main)
        self.__consume_type_declaration()
        self.__consume_fn_declarations()
        self.__consume(Token_Type.Begin)
        self.__consume_sequence_statements()
        self.__consume(Token_Type.End)
        self.__consume(Token_Type.Period)
        return self.results

    def __syntax_error(self, error):
    # throws exception
        raise Exception(f"Syntax Error at line:{self.tokenizer.line_number} -> {error}")

    def __look_up(self, id):
    # returns value of variable with id
        if(id not in self.symbol_table):
           self.__syntax_error("Undefined identifier - '" + id + "'")
        if(self.uninitialized_variables[id]):
            self.warnings.append(f"Warning at line:{self.tokenizer.line_number} -> Using uninitialized variable")
        return self.symbol_table[id]
    
    def __insert_identifier(self, id, value = 0):
    # inserts identifier in symbol table
        self.symbol_table[id] = value
    
    def __consume(self, tokenType):
    # tokenType - Token_Type
        consumed_token = self.tokenizer.next()
        if(consumed_token == None or consumed_token.type != tokenType):
            self.__syntax_error(f"Expected '{tokenType}' but not found")
        return consumed_token

    def __consume_type_declaration(self):
    # consumes type declaration
        while self.tokenizer.token and self.tokenizer.token.type == Token_Type.Var:
            while self.tokenizer.token and self.tokenizer.token.type in [Token_Type.Var, Token_Type.Comma]:
                self.__consume(self.tokenizer.token.type)
                self.__variable_declaration()
            # if there are multiple semi colons, consume them
            while(self.tokenizer.token and self.tokenizer.token.type == Token_Type.SemiColon):
                self.__consume(Token_Type.SemiColon)

    def __consume_fn_declarations(self):
    # consumes function declaration
        pass

    def __consume_sequence_statements(self):
    # consumes multiple statement declarations
        while self.tokenizer.token and self.tokenizer.token.type in self.statement_starter:
            statement_type = self.tokenizer.token.type
            self.__consume(statement_type)
            match statement_type:
                case Token_Type.Let:
                    self.__handle_assignment()
                case Token_Type.Call:
                    self.__handle_function_call()
                case _:
                    self.__syntax_error("Undefined statement")
            if self.tokenizer.token and self.tokenizer.token.type == Token_Type.SemiColon:
                self.__consume(Token_Type.SemiColon)
            elif (self.tokenizer.token and self.tokenizer.token.type in self.statement_starter):
                    self.__syntax_error("Expected statement separator - " + Token_Type.SemiColon + "'")

    def __handle_function_call(self):
    # handles predefined function call
        while self.tokenizer.token and self.tokenizer.token.type == Token_Type.Fn_OutputNum:
            self.__consume(self.tokenizer.token.type)
            self.__consume(Token_Type.OpenParanthesis)
            self.results.append(self.__expression())
            self.__consume(Token_Type.CloseParanthesis)
        
    def __handle_assignment(self):
    # handles assignment to identifier
        if self.tokenizer.token and self.tokenizer.token.type == Token_Type.Identifier:
            id = self.tokenizer.token.id
            self.__consume(Token_Type.Identifier)
            self.__consume(Token_Type.Assignment)
            self.__insert_identifier(id, self.__expression())
            self.uninitialized_variables[id] = False
        else:
            self.__syntax_error("Expected identifier assignment")

    def __variable_declaration(self):
    # handle variable declaration
        if self.tokenizer.token and self.tokenizer.token.type == Token_Type.Identifier:
            self.uninitialized_variables[self.tokenizer.token.id] = True
            self.__insert_identifier(self.tokenizer.token.id)
            self.__consume(Token_Type.Identifier)
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