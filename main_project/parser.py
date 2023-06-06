"""
Parser for grammar defined in ../grammars/smpl_grammar.txt

"""

from .tokenizer import Tokenizer
from .token_types import Token_Type
from .intermediate_representation import IR_OP as opc, IR_Memory_Allocation
from .ssa import SSA_Engine

class Parser:
    
    statement_starter = [Token_Type.Let, Token_Type.If, Token_Type.While, Token_Type.Return, Token_Type.Call]
    relational_operators = {
                            Token_Type.Equals : opc.bne,
                            Token_Type.NotEquals : opc.beq,
                            Token_Type.LessThan : opc.bge,
                            Token_Type.LessThanEqualTo : opc.bgt,
                            Token_Type.GreaterThan : opc.ble,
                            Token_Type.GreaterThanEqualTo : opc.blt
                            }
    type_declarations = [Token_Type.Array, Token_Type.Var]

    def __init__(self, input_string):
    # constructor initialization
        self.__tokenizer = Tokenizer(input_string)
        self.warnings = []
        self.__ssa = SSA_Engine()
        self.__contexts = {}
        self.__main_ssa = self.__ssa

    def parse(self):
    # entry point for this parser
        self.__consume(Token_Type.Main)
        self.__consume_type_declaration()
        self.__consume_fn_declarations()
        self.__ssa = self.__main_ssa
        self.__consume(Token_Type.Begin)
        self.__consume_sequence_statements()
        self.__consume(Token_Type.End)
        self.__consume(Token_Type.Period)
        self.__ssa.create_instruction(opc.end)
        self.__contexts['main'] = self.__ssa.get_cfg()
        return self.__contexts
    
    def get_cfg(self):
        return self.__ssa.get_cfg()
    
    def __syntax_error(self, error):
    # throws exception
        raise Exception(f"Syntax Error at line:{self.__tokenizer.line_number} -> {error}")

    def __look_up(self, id):
    # returns value of variable with id
        if(self.__ssa.is_identifier_defined(id) == False):
           self.__syntax_error("Undefined identifier - '" + id + "'")
        if(self.__ssa.is_indentifier_uninitialized(id)):
            self.warnings.append(f"Warning at line:{self.__tokenizer.line_number} -> Using uninitialized variable '{id}'")

        value = self.__ssa.get_identifier_val(id)        
        if isinstance(value, IR_Memory_Allocation):
            indices = self.__read_indexing()
            if len(indices) != len(value.dimensions):
                self.__syntax_error("Array not accessed properly!")
            value = self.__ssa.get_array_value(id, indices)
        return value
    
    def __insert_identifier(self, id, value = None, indices = None):
    # inserts identifier in symbol table
        if value is None:
            value = self.__ssa.uninitialized_instruction
        if indices is not None:
            current_val = self.__ssa.get_identifier_val(id)
            if isinstance(current_val, IR_Memory_Allocation) and len(indices) != len(current_val.dimensions):
                self.__syntax_error("Array not accessed properly!")
            self.__ssa.set_array_value(id, indices, value)
        else:
            self.__ssa.set_identifier_val(id, value)
    
    def __consume(self, tokenType):
    # tokenType - Token_Type
        consumed_token = self.__tokenizer.next()
        if(consumed_token == None or consumed_token.type != tokenType):
            self.__syntax_error(f"Expected '{tokenType}' but not found")
        return consumed_token

    def __consume_type_declaration(self):
    # consumes type declaration
        while self.__tokenizer.token and self.__tokenizer.token.type in self.type_declarations:
            declaration_type = self.__tokenizer.token.type
            self.__consume(declaration_type)
            dimensions = []
            if declaration_type == Token_Type.Array:
                dimensions = self.__read_indexing(True)
            while self.__tokenizer.token and self.__tokenizer.token.type in [Token_Type.Identifier, Token_Type.Comma]:
                if self.__tokenizer.token.type == Token_Type.Comma:
                    self.__consume(self.__tokenizer.token.type)
                if declaration_type == Token_Type.Array:
                    self.__array_declaration(dimensions)
                else:
                    self.__variable_declaration()
                
            self.__consume(Token_Type.SemiColon)

    def __read_indexing(self, declaration = False):
        dimensions = []
        while self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.OpenBracket:
            self.__consume(Token_Type.OpenBracket)
            if declaration == True:
                num = self.__tokenizer.token.val
                self.__consume(Token_Type.Number)
            else:
                num = self.__expression()
            dimensions.append(num)
            self.__consume(Token_Type.CloseBracket)
        if declaration and len(dimensions) == 0:
            self.__syntax_error("Indexing missing for array declaration.")
        return dimensions
    
    def __read_formal_parameters(self):
        self.__consume(Token_Type.OpenParanthesis)
        counter = 1
        while self.__tokenizer.token and self.__tokenizer.token.type in [Token_Type.Identifier, Token_Type.Comma]:
            if self.__tokenizer.token.type == Token_Type.Comma:
                self.__consume(self.__tokenizer.token.type)
            self.__variable_declaration(True, counter)
            counter += 1
        self.__consume(Token_Type.CloseParanthesis)

    def __consume_function_definition(self):
        self.__consume_type_declaration()
        self.__consume(Token_Type.Begin)
        self.__consume_sequence_statements()
        self.__consume(Token_Type.End)

    def __consume_fn_declarations(self):
    # consumes function declaration
        need_return = True
        while self.__tokenizer.token and self.__tokenizer.token.type in [Token_Type.Function, Token_Type.Void]:
            if self.__tokenizer.token.type == Token_Type.Void:
                self.__consume(Token_Type.Void)
                need_return = False
            self.__consume(Token_Type.Function)
            if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.Identifier:
                if self.__tokenizer.token.val in self.__contexts:
                    self.__syntax_error("Cannot declare same function twice.")
                else:
                    self.__ssa = SSA_Engine()
                    function_name = self.__tokenizer.token.id
                    self.__consume(Token_Type.Identifier)
                    self.__read_formal_parameters()
                    self.__consume(Token_Type.SemiColon)
                    self.__consume_function_definition()
                    self.__consume(Token_Type.SemiColon)
                    if need_return:
                        self.__ssa.finish_function()
                    self.__contexts[function_name] = self.__ssa.get_cfg()
            else:
                self.__syntax_error("Expected function name but not found")

    def __consume_sequence_statements(self):
    # consumes multiple statement declarations
        if self.__tokenizer.token is None or self.__tokenizer.token.type not in self.statement_starter:
            self.__syntax_error(f"Expected a statement but not found!")
        while self.__tokenizer.token and self.__tokenizer.token.type in self.statement_starter:
            statement_type = self.__tokenizer.token.type
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
            if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.SemiColon:
                self.__consume(Token_Type.SemiColon)
            elif (self.__tokenizer.token and self.__tokenizer.token.type in self.statement_starter):
                    self.__syntax_error("Expected statement separator - " + Token_Type.SemiColon + "'")

    def __handle_function_call(self):
    # handles predefined function call
        if self.__tokenizer.token.type not in [Token_Type.Fn_OutputNum, Token_Type.Fn_OutputNewLine] and self.__tokenizer.token.id not in self.__contexts:
            self.__syntax_error("Invalid function name!")
        while self.__tokenizer.token and (self.__tokenizer.token.type in [Token_Type.Fn_OutputNum, Token_Type.Fn_OutputNewLine] or self.__tokenizer.token.id in self.__contexts):
            fn_type = self.__tokenizer.token.type
            if fn_type in [Token_Type.Fn_OutputNum]:
                self.__consume(fn_type)
                self.__ssa.create_instruction(opc.write, self.__expression())
                self.__consume(Token_Type.CloseParanthesis)
            elif fn_type in [Token_Type.Fn_OutputNewLine]:
                self.__consume(fn_type)
                self.__ssa.create_instruction(opc.writeNL)
                self.__consume(Token_Type.CloseParanthesis)
            else:
                self.__handle_user_defined_function_call()
        
    def __handle_assignment(self):
    # handles assignment to identifier
        if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.Identifier:
            id = self.__tokenizer.token.id
            self.__consume(Token_Type.Identifier)
            indices = None
            if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.OpenBracket:
               indices = self. __read_indexing()
            self.__consume(Token_Type.Assignment)
            self.__insert_identifier(id, self.__expression(), indices)
        else:
            self.__syntax_error("Expected identifier assignment")

    def __variable_declaration(self, isParam = False, counter = 0):
    # handle variable declaration
        if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.Identifier:
            if self.__ssa.is_already_declared(self.__tokenizer.token.id):
                self.__syntax_error("Cannot declare same variable twice.")
            if isParam:
                instruction, _ = self.__ssa.create_instruction(opc.param, counter, isParam)
                self.__insert_identifier(self.__tokenizer.token.id, instruction)
            else: 
                self.__insert_identifier(self.__tokenizer.token.id)
            self.__consume(Token_Type.Identifier)
        else:
             self.__syntax_error("Expected identifier but not found")
    
    def __array_declaration(self, dimensions):
        # handle variable declaration
        if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.Identifier:
            if self.__ssa.is_already_declared(self.__tokenizer.token.id):
                self.__syntax_error("Cannot declare same variable twice.")
            pointer_val, _ = self.__ssa.create_instruction(opc.malloc, dimensions, self.__tokenizer.token.id)
            self.__insert_identifier(self.__tokenizer.token.id, pointer_val)
            self.__consume(Token_Type.Identifier)
        else:
             self.__syntax_error("Expected identifier but not found")

    def __expression(self):
    # calculate expression
        instruction = self.__term()

        while self.__tokenizer.token and self.__tokenizer.token.type in [Token_Type.Plus, Token_Type.Minus]:
            token_type = self.__tokenizer.token.type
            self.__consume(token_type)
            opcode = opc.add if token_type == Token_Type.Plus else opc.sub
            instruction, _ = self.__ssa.create_instruction(opcode, instruction, self.__term())
        
        return instruction

    def __term(self):
    # calculate term
        instruction = self.__factor()

        while self.__tokenizer.token and self.__tokenizer.token.type in [Token_Type.Mul, Token_Type.Div]:
            token_type = self.__tokenizer.token.type
            self.__consume(token_type)
            opcode = opc.div if token_type == Token_Type.Div else opc.mul
            instruction, _ = self.__ssa.create_instruction(opcode, instruction, self.__factor())

        return instruction

    def __factor(self):
    # calculates factor
        instruction = None
        if self.__tokenizer.token:
            if self.__tokenizer.token.type == Token_Type.OpenParanthesis:
                self.__consume(Token_Type.OpenParanthesis)
                instruction = self.__expression()
                if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.CloseParanthesis:
                    self.__consume(Token_Type.CloseParanthesis)
                else:
                    self.__syntax_error("Expected ) but not found")
            elif self.__tokenizer.token.type == Token_Type.Number:
                instruction, _ = self.__ssa.create_instruction(opc.const, self.__tokenizer.token.val)
                self.__consume(Token_Type.Number)
            elif self.__tokenizer.token.type == Token_Type.Identifier:
                id = self.__tokenizer.token.id
                self.__consume(Token_Type.Identifier)
                instruction = self.__look_up(id)
            elif self.__tokenizer.token.type == Token_Type.Call:
                self.__consume(Token_Type.Call)
                if self.__tokenizer.token.type == Token_Type.Fn_InputNum:
                    self.__consume(Token_Type.Fn_InputNum)
                    self.__consume(Token_Type.CloseParanthesis)
                    instruction, _ = self.__ssa.create_instruction(opc.read)
                else:
                    instruction = self.__handle_user_defined_function_call()
        else:
            self.__syntax_error("Syntax error in factor")
        return instruction

    def __handle_if_statement(self):
        instruction, opcode = self.__handle_relation()
        left_block, right_block, join_block = self.__ssa.create_control_flow(instruction, self.relational_operators[opcode], False)
        self.__consume(Token_Type.Then)
        self.__ssa.processing_fall_through()
        self.__consume_sequence_statements()
        self.__ssa.end_fall_through()
        self.__ssa.processing_branch()
        if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.Else:
            self.__consume(Token_Type.Else)
            self.__consume_sequence_statements()
        self.__ssa.end_branch()
        self.__consume(Token_Type.Fi)
        self.__ssa.end_control_flow(left_block, right_block, join_block)
                
    def __handle_relation(self):
        while self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.OpenParanthesis:
            self.__consume(Token_Type.OpenParanthesis)
        op1 = self.__expression()
        while self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.CloseParanthesis:
            self.__consume(Token_Type.CloseParanthesis)

        opcode = self.__tokenizer.token
        if opcode is None:
            self.__syntax_error("Invalid operator used.")
        if opcode.type not in self.relational_operators:
            self.__syntax_error("Expected a relational operator.")
        self.__consume(opcode.type)

        while self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.OpenParanthesis:
            self.__consume(Token_Type.OpenParanthesis)
        op2 = self.__expression()
        while self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.CloseParanthesis:
            self.__consume(Token_Type.CloseParanthesis)
        
        instruction, _ = self.__ssa.create_instruction(opc.cmp, op1, op2)
        return instruction, opcode.type
    
    def __handle_while_statement(self):
        self.__ssa.split_block()
        self.__ssa.update_join_block()
        instruction, opcode = self.__handle_relation()
        _, right_block, join_block = self.__ssa.create_control_flow(instruction, self.relational_operators[opcode], True)
        self.__consume(Token_Type.Do)
        self.__ssa.processing_fall_through()
        self.__consume_sequence_statements()
        self.__ssa.end_fall_through()
        self.__consume(Token_Type.Od)
        self.__ssa.end_loop_control_flow(right_block, join_block)
        
    def __handle_return_statement(self):
        self.__ssa.create_instruction(opc.ret, self.__expression())

    def __handle_user_defined_function_call(self):
        funtion_name = self.__tokenizer.token.id
        self.__consume(Token_Type.Identifier)
        if self.__tokenizer.token.type == Token_Type.OpenParanthesis:
            self.__consume(Token_Type.OpenParanthesis)
            while self.__tokenizer.token and self.__tokenizer.token.type != Token_Type.CloseParanthesis:
                self.__ssa.create_instruction(opc.param, self.__expression())
                if self.__tokenizer.token and self.__tokenizer.token.type == Token_Type.Comma:
                    self.__consume(Token_Type.Comma)
            self.__consume(Token_Type.CloseParanthesis)
        instruction, _ = self.__ssa.create_instruction(opc.call, funtion_name)
        instruction.set_calling_info(funtion_name)

        return instruction
