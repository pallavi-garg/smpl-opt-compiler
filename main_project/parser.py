"""
Parser for grammar defined in ../grammars/smpl_grammar.txt

"""

from .tokenizer import Tokenizer
from .token_types import Token_Type
from .intermediate_representation import IR_OP as opc
from .ssa import SSA_Engine

class Parser:
    
    statement_starter = [Token_Type.Let, Token_Type.If, Token_Type.While, Token_Type.Return, Token_Type.Call]
    relational_operators = {
                            Token_Type.Equals : opc.bne,
                            Token_Type.NotEquals : opc.beq,
                            Token_Type.LessThan : opc.bgt,
                            Token_Type.LessThanEqualTo : opc.bge,
                            Token_Type.GreaterThan : opc.blt,
                            Token_Type.GreaterThanEqualTo : opc.ble
                            }

    def __init__(self, input_string):
    # constructor initialization
        self.tokenizer = Tokenizer(input_string)
        self.uninitialized_variables = {}
        self.warnings = []
        self.__ssa = SSA_Engine()

    def parse(self):
    # entry point for this parser
        self.__consume(Token_Type.Main)
        self.__consume_type_declaration()
        self.__consume_fn_declarations()
        self.__consume(Token_Type.Begin)
        self.__consume_sequence_statements()
        self.__consume(Token_Type.End)
        self.__consume(Token_Type.Period)
        return self.__ssa.get_cfg()

    def __syntax_error(self, error):
    # throws exception
        raise Exception(f"Syntax Error at line:{self.tokenizer.line_number} -> {error}")

    def __look_up(self, id):
    # returns value of variable with id
        if(self.__ssa.is_identifier_defined(id) == False):
           self.__syntax_error("Undefined identifier - '" + id + "'")
        if(self.uninitialized_variables[id]):
            self.warnings.append(f"Warning at line:{self.tokenizer.line_number} -> Using uninitialized variable")
        return self.__ssa.get_identifier_val(id)
    
    def __insert_identifier(self, id, value = 0):
    # inserts identifier in symbol table
        self.__ssa.set_identifier_val(id, value)
    
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
                case Token_Type.If:
                    self.__handle_if_statement()
                case Token_Type.While:
                    self.__handle_while_statement()
                case Token_Type.Return:
                    self.__handle_return_statement()
                case _:
                    self.__syntax_error("Undefined statement")
            if self.tokenizer.token and self.tokenizer.token.type == Token_Type.SemiColon:
                self.__consume(Token_Type.SemiColon)
            elif (self.tokenizer.token and self.tokenizer.token.type in self.statement_starter):
                    self.__syntax_error("Expected statement separator - " + Token_Type.SemiColon + "'")

    def __handle_function_call(self):
    # handles predefined function call
        while self.tokenizer.token and self.tokenizer.token.type in [Token_Type.Fn_OutputNum, Token_Type.Fn_OutputNewLine]:
            fn_type = self.tokenizer.token.type
            self.__consume(self.tokenizer.token.type)
            if fn_type in [Token_Type.Fn_OutputNum]:
                self.__ssa.create_instruction(opc.write, self.__expression())
            else:
                self.__ssa.create_instruction(opc.writeNL)
            self.__consume(Token_Type.CloseParanthesis)
        
    def __handle_assignment(self):
    # handles assignment to identifier
        if self.tokenizer.token and self.tokenizer.token.type == Token_Type.Identifier:
            id = self.tokenizer.token.id
            self.__consume(Token_Type.Identifier)
            self.__consume(Token_Type.Assignment)
            if self.tokenizer.token and self.tokenizer.token.type == Token_Type.Call:
                self.__consume(Token_Type.Call)
                self.__consume(Token_Type.Fn_InputNum)
                self.__consume(Token_Type.CloseParanthesis)
                self.__insert_identifier(id, self.__ssa.create_instruction(opc.read))
            else:
                self.__insert_identifier(id, self.__expression())
                self.__ssa.added_assignment(id)
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
        instruction = self.__term()

        while self.tokenizer.token and self.tokenizer.token.type in [Token_Type.Plus, Token_Type.Minus]:
            token_type = self.tokenizer.token.type
            self.__consume(token_type)
            opcode = opc.add if token_type == Token_Type.Plus else opc.sub
            instruction = self.__ssa.create_instruction(opcode, instruction, self.__term())
        return instruction

    def __term(self):
    # calculate term
        instruction = self.__factor()
        while self.tokenizer.token and self.tokenizer.token.type in [Token_Type.Mul, Token_Type.Div]:
            token_type = self.tokenizer.token.type
            self.__consume(token_type)
            opcode = opc.div if token_type == Token_Type.Div else opc.mul
            instruction = self.__ssa.create_instruction(opcode, instruction, self.__factor())
        return instruction

    def __factor(self):
    # calculates factor
        instruction = None
        if self.tokenizer.token:
            if self.tokenizer.token.type == Token_Type.OpenParanthesis:
                self.__consume(Token_Type.OpenParanthesis)
                instruction = self.__expression()
                if self.tokenizer.token and self.tokenizer.token.type == Token_Type.CloseParanthesis:
                    self.__consume(Token_Type.CloseParanthesis)
                else:
                    self.__syntax_error("Expected ) but not found")
            elif self.tokenizer.token.type == Token_Type.Number:
                instruction = self.__ssa.create_instruction(opc.const, self.tokenizer.token.val)
                self.__consume(Token_Type.Number)
            elif self.tokenizer.token.type == Token_Type.Identifier:
                instruction = self.__look_up(self.tokenizer.token.id)
                self.__consume(Token_Type.Identifier)
        else:
            self.__syntax_error("Syntax error in factor")
        return instruction

    def __handle_if_statement(self):
        instruction, opcode = self.__handle_relation()
        self.__ssa.create_branch(instruction, self.relational_operators[opcode])
        self.__consume(Token_Type.Then)
        self.__ssa.processing_fall_through()
        self.__consume_sequence_statements()
        self.__ssa.end_block()
        if self.tokenizer.token and self.tokenizer.token.type == Token_Type.Else:
            self.__consume(Token_Type.Else)
            self.__ssa.processing_branch()
            self.__consume_sequence_statements()
        self.__consume(Token_Type.Fi)
        self.__ssa.commit_join()

    def __handle_relation(self):
        op1 = self.__expression()
        opcode = self.tokenizer.token
        if opcode.type not in self.relational_operators:
            self.__syntax_error("Expected a relational operator.")
        self.__consume(opcode.type)
        op2 = self.__expression()
        return self.__ssa.create_instruction(opc.cmp, op1, op2), opcode.type
    
    def __handle_while_statement(self):
        pass

    def __handle_return_statement(self):
        pass