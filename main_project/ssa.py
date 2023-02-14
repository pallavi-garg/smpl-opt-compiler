from .intermediate_representation import IR, IR_One_Operand, IR_Two_Operand, IR_OP as opc
from .cfg import Control_Flow_Graph, Basic_Block as bb
import copy
from .search_data_structure import search_ds

class SSA_Engine:
    # holds objects required in SSA calculations
    def __init__(self):
        self.uninitialized_instruction = IR_One_Operand(opc.undefined, 0) # 0 is default value of all numbers
        self.__cfg = Control_Flow_Graph()
        self.__root_block = self.__cfg.get_root()
        self.__current_block = self.__cfg.get_new_block()
        self.__current_block.set_dominator_block(self.__root_block)
        self.__root_block.fall_through_block = self.__current_block
        self.__nesting_stage = 0
        self.__control_flow_main_blocks = []
        self.__search_ds = search_ds()  
    
    def get_cfg(self):
    # returns cfg
        return self.__cfg

    def is_indentifier_uninitialized(self, id):
    # returns warnings found by ssa engine
        un_inititalized = False
        val = self.__current_block.symbol_table[id]
        if isinstance(val, IR_Two_Operand) and val.op_code == opc.phi:
            return self.__is_undefined(val, [])
        elif self.uninitialized_instruction == val:
            un_inititalized = True
        return un_inititalized

    def __is_undefined(self, operand, already_looked_instructions):
    # returns true if operand is undefined variable value
        if self.uninitialized_instruction == operand:
            return True
        elif isinstance(operand, IR_One_Operand):
            return operand.op_code == opc.undefined
        elif operand not in already_looked_instructions and isinstance(operand, IR_Two_Operand):
            val = self.__is_undefined(operand.operand1, already_looked_instructions) or self.__is_undefined(operand.operand2, already_looked_instructions)
            already_looked_instructions.append(operand)
            return val
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
    
    def split_block(self):
        if len(self.__current_block.instructions) > 0:
            prev = self.__current_block
            self.__current_block = self.__cfg.get_new_block()
            self.__current_block.set_dominator_block(prev)
            prev.fall_through_block = self.__current_block

    def create_control_flow(self, instruction, opcode, use_current_as_join):
    # updates current block based on use_current_as_join
        # adds branch, fallthrough and join block
        self.__control_flow_main_blocks.append(self.__current_block)
        
        self.__current_block.fall_through_block = self.__cfg.get_new_block()
        self.__current_block.fall_through_block.set_dominator_block(self.__current_block)

        self.__current_block.branch_block = self.__cfg.get_new_block()
        self.__current_block.branch_block.set_dominator_block(self.__current_block)

        join_block = self.__current_block
        if use_current_as_join == False:
            join_block = self.__cfg.get_new_block()
            join_block.set_dominator_block(self.__current_block)
            self.__current_block.branch_block.join_block = join_block
            join_block.join_block = None
            self.__current_block.branch_block.fall_through_block = join_block
            self.__current_block.fall_through_block.fall_through_block = join_block
        
        self.__current_block.fall_through_block.join_block = join_block
        self.create_instruction(opcode, instruction, self.__current_block.branch_block)
        return self.__current_block.fall_through_block, self.__current_block.branch_block, join_block

    def processing_fall_through(self):
    # sets current working block to fall through block
        self.__current_block = self.__current_block.fall_through_block        
        self.__current_block.set_dominator_block(self.__current_block.get_dominator_block())
        self.__nesting_stage += 1

    def end_fall_through(self):
    # adds branch instruction if current block is a fall through block. This is done to prevent branch block instructions
        join_block = self.__current_block.join_block
        if join_block is None:
            main_block = self.__control_flow_main_blocks.pop()
            self.__control_flow_main_blocks.append(main_block) #append main_block as it has not ended yet
            join_block = main_block.fall_through_block.join_block

        self.create_instruction(opc.bra, join_block)
        
    def processing_branch(self):
    # sets current working block to branch block
        prev_current = self.__current_block
        main_block = self.__control_flow_main_blocks.pop()
        self.__control_flow_main_blocks.append(main_block) #append main_block as it has not ended yet

        self.__current_block = main_block.branch_block

        if prev_current != self.__current_block.get_dominator_block().fall_through_block:
            prev_current.fall_through_block = self.__current_block.join_block
        self.__current_block.set_dominator_block(self.__current_block.get_dominator_block())
    
    def end_branch(self):
        join_block = self.__current_block.join_block

        if join_block is None:
            main_block = self.__control_flow_main_blocks.pop()
            self.__control_flow_main_blocks.append(main_block) #append main_block as it has not ended yet
            join_block = main_block.fall_through_block.join_block
            self.__current_block.fall_through_block = join_block
        self.__current_block = join_block

    def end_control_flow(self, left, right, join_block):
        self.__control_flow_main_blocks.pop()
        left_block = left
        right_block = right
        while(left_block.fall_through_block != join_block):
            left_block = left_block.fall_through_block
        while(right_block.fall_through_block != join_block):
            right_block = right_block.fall_through_block
        self.__propagate_phi(left_block, right_block, join_block)

    def __propagate_phi(self, left_block, right_block, join_block):
        modified_variables = {}
        for id in join_block.symbol_table:
            existing_val = join_block.symbol_table[id]
            if existing_val is None or existing_val.op_code != opc.phi:
                if left_block.symbol_table[id] != right_block.symbol_table[id]:
                    phi = IR_Two_Operand(opc.phi, left_block.symbol_table[id], right_block.symbol_table[id])
                    join_block.instructions.insert(0, phi)
                    old_val = join_block.symbol_table[id]
                    join_block.symbol_table[id] = phi
                    modified_variables[old_val.instruction_number] = join_block.symbol_table[id]
                else:
                    join_block.symbol_table[id] = left_block.symbol_table[id]
            elif existing_val.op_code == opc.phi:
                #in case of loop, left block is the main while header block
                if join_block != left_block:
                    existing_val.operand1 = left_block.symbol_table[id]
                existing_val.operand2 = right_block.symbol_table[id]
        return modified_variables

    def end_loop_control_flow(self, left, right, join_block):
        self.__control_flow_main_blocks.pop()
        left.fall_through_block = join_block

        modified_variables = self.__propagate_phi(join_block, left, join_block)
        self.__move_new_values_down(left, join_block, modified_variables)
        self.__current_block = right
        #TODO: self.__current_block.symbol_table = join_block.symbol_table

    def __move_new_values_down(self, loop_body, join_block, modified_variables):
        all_instructions = join_block.instructions + loop_body.instructions
        for instruction in all_instructions:
            if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR) and instruction.operand.instruction_number in modified_variables:
                if instruction.instruction_number < modified_variables[instruction.operand.instruction_number].instruction_number:
                    instruction.operand = modified_variables[instruction.operand.instruction_number]
            elif isinstance(instruction, IR_Two_Operand):
                if instruction.operand1 and isinstance(instruction.operand1, IR) and instruction.operand1.instruction_number in modified_variables:
                    if instruction.instruction_number < modified_variables[instruction.operand1.instruction_number].instruction_number:
                        instruction.operand1 = modified_variables[instruction.operand1.instruction_number]
                if instruction.operand2 and isinstance(instruction.operand2, IR) and instruction.operand2.instruction_number in modified_variables:
                    if instruction.instruction_number < modified_variables[instruction.operand2.instruction_number].instruction_number:
                        instruction.operand2 = modified_variables[instruction.operand2.instruction_number]
            #TODO: Add new instruction when instruction is updated but was also used for some other variable

    def create_instruction(self, opcode, operand1 = None, operand2 = None):
    # creates new instruction or returns previous common sub expression
        instruction = self.__search_ds.get(opcode, operand1, operand2, self.__current_block)
                
        # if not found in search data structure, then create new instruction
        if instruction is None:
            if opcode in [opc.add, opc.sub, opc.mul, opc.div, opc.cmp, opc.bne, opc.beq, opc.ble, opc.blt, opc.bge, opc.bgt]:
                instruction = IR_Two_Operand(opcode, operand1, operand2, self.__current_block)
                self.__current_block.instructions.append(instruction)
            elif opcode in [opc.end, opc.read, opc.writeNL]:
                instruction = IR(opcode, self.__current_block)
                self.__current_block.instructions.append(instruction)
            elif opcode in [opc.bra, opc.write]:
                instruction = IR_One_Operand(opcode, operand1, self.__current_block)
                self.__current_block.instructions.append(instruction)
            elif opcode == opc.const:
                instruction = IR_One_Operand(opcode, operand1, self.__root_block)
                self.__root_block.instructions.append(instruction)
            else:
                raise Exception(f"Unknown command '{opcode}'!")
            self.__search_ds.add(opcode, instruction)

        return instruction
        