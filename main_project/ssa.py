from .intermediate_representation import IR, IR_One_Operand, IR_Two_Operand, IR_OP as opc
from .cfg import Control_Flow_Graph, Basic_Block as bb
from .token_types import Token_Type
import copy

class SSA_Engine:
    # holds objects required in SSA calculations
    def __init__(self):
        self.__initialize_ds()    
        self.uninitialized_instruction = IR_One_Operand(opc.undefined, 0) # 0 is default value of all numbers
        self.__cfg = Control_Flow_Graph()
        self.__root_block = self.__cfg.get_root()
        self.__current_block = self.__cfg.get_new_block()
        self.__current_block.set_dominator_block(self.__root_block)
        self.__root_block.fall_through_block = self.__current_block
        self.__nesting_stage = 0
        #join block of block where nesting started
        self.__next_joining_phi = None
        self.create_instruction(opc.const, 0)

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
        self.__dom_search_ds = self.__search_data_structure
    
    def get_cfg(self):
    # returns cfg
        for k,v in self.__current_block.symbol_table.items():
            print(f"{k}: {v}")
        return self.__cfg

    def is_indentifier_uninitialized(self, id):
    # returns warnings found by ssa engine
        un_inititalized = False
        val = self.__current_block.symbol_table[id]
        if isinstance(val, IR_Two_Operand) and val.op_code == opc.phi:
            return self.__is_undefined(val)
        elif self.uninitialized_instruction == val:
            un_inititalized = True
        return un_inititalized

    def __is_undefined(self, operand):
        if self.uninitialized_instruction == operand:
            return True
        elif isinstance(operand, IR_One_Operand):
            return operand.op_code == opc.undefined
        elif isinstance(operand, IR_Two_Operand):
            return self.__is_undefined(operand.operand1) or self.__is_undefined(operand.operand2)
        else:
            return False
    
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
        self.__current_block = self.__current_block.fall_through_block
        self.__search_data_structure = copy.deepcopy(self.__dom_search_ds)
        self.__nesting_stage += 1
        if self.__next_joining_phi is None:
            self.__next_joining_phi = self.__current_block.join_block

    def end_fall_through(self):
    # adds branch instruction if current block is a fall through block. This is done to prevent branch block instructions
        if self.__current_block.get_dominator_block() is not None and self.__current_block == self.__current_block.get_dominator_block().fall_through_block:
            self.create_instruction(opc.bra, self.__current_block.join_block)
        
    def processing_branch(self):
    # sets current working block to branch block
        if self.__current_block == self.__current_block.get_dominator_block().fall_through_block:
            self.__current_block = self.__current_block.get_dominator_block().branch_block
            self.__search_data_structure = copy.deepcopy(self.__dom_search_ds)

    def end_if(self):
        self.__nesting_stage -= 1
        if self.__nesting_stage == 0:
            from_phi = self.__current_block
            self.__current_block.fall_through_block = self.__next_joining_phi
            self.__current_block = self.__next_joining_phi
            self.__next_joining_phi = None
            self.__propagate_phi(from_phi, self.__current_block)
        else:
            self.__current_block = self.__current_block.join_block
        self.__search_data_structure = copy.deepcopy(self.__dom_search_ds)

    def __propagate_phi(self, from_block, to_block):
    # adds phi instructions from from_block to given to_block
        if from_block and to_block:
            for instruction in from_block.instructions:
                if isinstance(instruction, IR_Two_Operand) and instruction.op_code == opc.phi:
                    id = None
                    for key, val in from_block.symbol_table.items():
                        if val == instruction:
                            id = key
                            break
                    # TODO: remove use_previous and previously_value, and create a use_chain to impelement this
                    use_previous = False
                    previously_value = to_block.symbol_table[id]
                    if isinstance(previously_value, IR_Two_Operand) and previously_value.op_code == opc.phi:
                        use_previous = True

                    # By default all phi is added as if from_block is coming from right
                    operand1 = to_block.symbol_table[id] if use_previous == False else previously_value.operand1
                    operand2 = instruction

                    if self.__is_left_block(to_block.get_dominator_block(), from_block):
                        operand1 = instruction
                        operand2 = to_block.symbol_table[id] if use_previous == False else previously_value.operand2

                    if use_previous:
                        previously_value.operand1 = operand1
                        previously_value.operand2 = operand2
                    elif operand1 == operand2 and operand1 == to_block.symbol_table[id]:
                        #if everything is already same, then no need to add phi
                        pass
                    else:
                        new_phi = IR_Two_Operand(opc.phi, operand1, operand2)
                        to_block.instructions.insert(0, new_phi)
                        to_block.symbol_table[id] = new_phi

    def create_instruction(self, opcode, operand1 = None, operand2 = None):
    # creates new instruction or returns previous common sub expression
        prev_common_expression = None
        prev = None
        if opcode not in [opc.read, opc.write, opc.writeNL, opc.bra, opc.end]:
            prev_common_expression = self.get_instruction(opcode, operand1, operand2)
            prev = self.__search_data_structure[opcode]
        
        # if not found in search data structure, then create new instruction
        if prev_common_expression is None:
            self.__search_data_structure[opcode] = self.__create_IR(opcode, operand1, operand2)
            if prev is not None:
                self.__search_data_structure[opcode].prev_search_ds = prev
        
        instruction = prev_common_expression if prev_common_expression is not None else self.__search_data_structure[opcode]

        return instruction

    def added_assignment(self, id):
    # adds phi instruction in join block
        join_block = self.__current_block.join_block
        desired_bom = self.__current_block.get_dominator_block()
        # case when current block is actually join block of some if else. 
        # If we don't set this then phis are not added in this when this is the fallthrough of previous nested if statement
        if join_block is None:
            join_block = self.__next_joining_phi

        if join_block != None:
            desired_bom = join_block.get_dominator_block()
            phi = None
            previous_phi = join_block.symbol_table[id]
            if previous_phi is not None and (isinstance(previous_phi, IR) == False or previous_phi.op_code != opc.phi) :
                previous_phi = None
            # left block
            if self.__is_left_block(desired_bom, self.__current_block) == True:
                if previous_phi is None or previous_phi not in join_block.instructions:
                    op1 = self.get_identifier_val(id)
                    op2 = self.__current_block.get_dominator_block().symbol_table[id] 
                    if op1 == op2 and join_block.symbol_table[id] == op1:
                        # if everything is already same, no need to add new phi
                        return
                    phi = IR_Two_Operand(opc.phi, op1, op2)
                    join_block.instructions.insert(0,phi)
                else:
                    previous_phi.operand1 = self.get_identifier_val(id)
                    phi = previous_phi
            else:
                if previous_phi is None or previous_phi not in join_block.instructions:
                    op1 = self.__current_block.get_dominator_block().symbol_table[id]
                    op2 = self.get_identifier_val(id)
                    if op1 == op2 and join_block.symbol_table[id] == op1:
                        #if everything is already same, no need to add new phi
                        return
                    phi = IR_Two_Operand(opc.phi, op1, op2)
                    join_block.instructions.insert(0,phi)
                else:
                    previous_phi.operand2 = self.get_identifier_val(id)
                    phi = previous_phi

            join_block.symbol_table[id] = phi

    def __is_left_block(self, desired_dom, block):
        left_block = False

        curr_dom = block
        next_dom = block.get_dominator_block()
        while(next_dom != desired_dom):
            curr_dom = next_dom
            next_dom = curr_dom.get_dominator_block()

        if(curr_dom == desired_dom.fall_through_block):
            left_block = True

        return left_block

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

        self.__current_block.branch_block.fall_through_block = join_block
        self.__current_block.fall_through_block.fall_through_block = join_block

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
                instruction.prev_search_ds = self.__dom_search_ds[opc.const]
                self.__dom_search_ds[opc.const] = instruction
            case _:
                self.__current_block.instructions.append(instruction)
        
        return instruction