from .intermediate_representation import IR, IR_One_Operand, IR_Two_Operand, IR_OP as opc
from .cfg import Control_Flow_Graph, Basic_Block as bb
from .token_types import Token_Type

class SSA_Engine:
    # holds objects required in SSA calculations
    def __init__(self):
        self.__initialize_ds()    
        self.__cfg = Control_Flow_Graph()
        self.__root_block = self.__cfg.get_root()
        self.__current_block = self.__cfg.get_new_block()
        self.__current_block.set_dominator_block(self.__root_block)
        self.__stack = []

    def __initialize_ds(self):
    # initialized search data structure with None references to supported opcodes
        self.__search_data_structure = {}
        self.__search_data_structure[opc.add] = None
        self.__search_data_structure[opc.sub] = None
        self.__search_data_structure[opc.mul] = None
        self.__search_data_structure[opc.div] = None
        self.__search_data_structure[opc.const] = None
        self.__search_data_structure[opc.beq] = None
        self.__search_data_structure[opc.bne] = None
        self.__search_data_structure[opc.blt] = None
        self.__search_data_structure[opc.ble] = None
        self.__search_data_structure[opc.bge] = None
        self.__search_data_structure[opc.bgt] = None
        self.__search_data_structure[opc.cmp] = None
    
    def get_cfg(self):
    # returns cfg
        return self.__cfg
    
    def is_identifier_defined(self, id):
    # returns true if id is present in symbol table
        return id in self.__current_block.symbol_table

    def get_identifier_val(self, id):
    # returns value of id from symbol table
        return self.__current_block.symbol_table[id]

    def set_identifier_val(self, id, value):
    # inserts value of id in symbol table
        self.__current_block.symbol_table[id] = value

    def get_instruction(self, opcode, operand1 = None, operand2 = None): #, ir_num = 0):
    # check in hierarchy of search data structure
        prev_common_expression = self.__search_data_structure[opcode]
        while prev_common_expression is not None: # and prev_common_expression.instruction_number >= ir_num:
            if isinstance(prev_common_expression, IR_Two_Operand) and prev_common_expression.operand1 == operand1 and prev_common_expression.operand2 == operand2:
                break
            elif isinstance(prev_common_expression, IR_One_Operand) and prev_common_expression.operand == operand1:
                break;
            prev_common_expression = prev_common_expression.prev_search_ds
        return prev_common_expression

    def create_branch(self, instruction, opcode):
    # updates current block based on consumed token
        self.__split_block_after_instruction()
        self.create_instruction(opcode, instruction, self.__current_block.branch_block)
    
    def processing_fall_through(self):
    # sets current working block to fall through block
        self.__stack.append(self.__current_block)
        self.__current_block = self.__current_block.fall_through_block
        
    def processing_branch(self):
    # sets current working block to branch block
            main_block = self.__stack.pop()
            self.__stack.append(main_block)
            self.__current_block = main_block.branch_block

    def commit_join(self):
    # sets current working block to join block
        self.__stack.pop()
        self.__current_block = self.__current_block.join_block

    def create_instruction(self, opcode, operand1 = None, operand2 = None):
    # creates new instruction or returns previous common sub expression
        prev_common_expression = None
        prev = None
        if opcode not in [opc.read, opc.write, opc.writeNL]:
            prev_common_expression = self.get_instruction(opcode, operand1, operand2)
            prev = self.__search_data_structure[opcode]
        
        # if not found in search data structure, then create new instruction
        if prev_common_expression is None:
            self.__search_data_structure[opcode] = self.__create_IR(opcode, operand1, operand2)
            if prev is not None:
                self.__search_data_structure[opcode].prev_search_ds = prev
        
        instruction = prev_common_expression if prev_common_expression is not None else self.__search_data_structure[opcode]
        self.__current_block.instructions.append(instruction)

        return instruction

    def added_assignment(self, id):
    # adds phi instruction in join block
        if self.__current_block.join_block != None:
            phi = None
            previous_phi = self.__current_block.join_block.symbol_table[id]
            if previous_phi is not None and (isinstance(previous_phi, IR) == False or previous_phi.op_code != opc.phi) :
                previous_phi = None
            # left block
            if self.__current_block.dominant_block.fall_through_block == self.__current_block:
                if previous_phi is None:
                    phi = IR_Two_Operand(opc.phi, self.get_identifier_val(id), self.__current_block.dominant_block.symbol_table[id])
                else:
                    previous_phi.operand1 = self.get_identifier_val(id)
                    phi = previous_phi
            else:
                if previous_phi is None:
                    phi = IR_Two_Operand(opc.phi, self.__current_block.dominant_block.symbol_table[id], self.get_identifier_val(id))
                else:
                    previous_phi.operand2 = self.get_identifier_val(id)
                    phi = previous_phi

            print(phi)
            self.__current_block.join_block.symbol_table[id] = (phi)

    def __split_block_after_instruction(self):
    # adds branch, fallthrough and join block
        self.__current_block.fall_through_block = self.__cfg.get_new_block()
        self.__current_block.fall_through_block.set_dominator_block(self.__current_block)

        self.__current_block.branch_block = self.__cfg.get_new_block()
        self.__current_block.branch_block.set_dominator_block(self.__current_block)

        join_block = self.__cfg.get_new_block()
        self.__current_block.branch_block.join_block = join_block
        self.__current_block.fall_through_block.join_block = join_block
        join_block.join_block = None
        join_block.set_dominator_block(self.__current_block)

    def __create_IR(self, opcode, operand1, operand2):
        instruction = None
        match opcode:
            case opc.add:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.sub:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.mul:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.div:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.cmp:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.end:
                instruction = IR(opcode)
            case opc.bra:
                instruction = IR_One_Operand(opcode, operand1)
            case opc.bne:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.beq:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.ble:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.blt:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.bge:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.bgt:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.const:
                instruction = IR_One_Operand(opcode, operand1)
            case opc.read:
                instruction = IR(opcode)
            case opc.write:
                instruction = IR_One_Operand(opcode, operand1)
            case opc.writeNL:
                instruction = IR(opcode)
            case _:
                raise Exception("Unknown command!")

        match opcode:
            case opc.const:
                self.__root_block.instructions.append(instruction)
            case _:
                self.__current_block.instructions.append(instruction)
        
        print(f"{instruction}")
            
        return instruction