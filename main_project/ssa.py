from .intermediate_representation import IR, IR_One_Operand, IR_Two_Operand, IR_OP as opc
from .cfg import Control_Flow_Graph, Basic_Block as bb
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
        self.__control_flow_main_blocks = []
        self.__search_ds = []
        self.__last_const_instruction = None
        self.__last_fall_end = None
        self.__last_branch_end = None

    def __initialize_ds(self):
    # initialized search data structure with None references to supported opcodes
        self.__search_data_structure = {}
        self.__search_data_structure[opc.add] = None
        self.__search_data_structure[opc.sub] = None
        self.__search_data_structure[opc.mul] = None
        self.__search_data_structure[opc.div] = None
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
        if value is IR and value.op_code in [opc.undefined, opc.read]:
            pass
        else:
            pass
            #self.__added_assignment(id)
    
    def split_block(self):
        if len(self.__current_block.instructions) > 0:
            prev = self.__current_block
            self.__current_block = self.__cfg.get_new_block()
            self.__current_block.set_dominator_block(prev)
            prev.fall_through_block = self.__current_block
            self.__search_ds.append(copy.deepcopy(self.__search_data_structure))

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
        self.__search_ds.append(copy.deepcopy(self.__search_data_structure))
        return self.__current_block.fall_through_block, self.__current_block.branch_block, join_block

    def processing_fall_through(self):
    # sets current working block to fall through block
        self.__current_block = self.__current_block.fall_through_block
        
        self.__current_block.set_dominator_block(self.__current_block.get_dominator_block())
        top_search_ds = self.__search_ds.pop()
        self.__search_ds.append(top_search_ds)
        self.__search_data_structure = copy.deepcopy(top_search_ds)
        self.__nesting_stage += 1
        if self.__next_joining_phi is None:
            self.__next_joining_phi = self.__current_block.join_block

    def end_fall_through(self):
    # adds branch instruction if current block is a fall through block. This is done to prevent branch block instructions
        join_block = self.__current_block.join_block
        if join_block is None:
            main_block = self.__control_flow_main_blocks.pop()
            self.__control_flow_main_blocks.append(main_block) #append main_block as it has not ended yet
            join_block = main_block.fall_through_block.join_block

        self.create_instruction(opc.bra, join_block)
        self.__last_fall_end = self.__current_block
        
    def processing_branch(self):
    # sets current working block to branch block
        prev_current = self.__current_block
        main_block = self.__control_flow_main_blocks.pop()
        self.__control_flow_main_blocks.append(main_block) #append main_block as it has not ended yet

        self.__current_block = main_block.branch_block

        if prev_current != self.__current_block.get_dominator_block().fall_through_block:
            prev_current.fall_through_block = self.__current_block.join_block
        self.__current_block.set_dominator_block(self.__current_block.get_dominator_block())

        top_search_ds = self.__search_ds.pop()
        self.__search_ds.append(top_search_ds)
        self.__search_data_structure = copy.deepcopy(top_search_ds)
    
    def end_branch(self):
        self.__last_branch_end = self.__current_block
        join_block = self.__current_block.join_block

        if join_block is None:
            main_block = self.__control_flow_main_blocks.pop()
            self.__control_flow_main_blocks.append(main_block) #append main_block as it has not ended yet
            join_block = main_block.fall_through_block.join_block
            self.__current_block.fall_through_block = join_block
        self.__current_block = join_block

    def end_control_flow(self, left, right, join_block):
        self.__control_flow_main_blocks.pop()
        top_search_ds = self.__search_ds.pop()
        self.__search_data_structure = top_search_ds

        left_block = left
        right_block = right
        while(left_block.fall_through_block != join_block):
            left_block = left_block.fall_through_block
        while(right_block.fall_through_block != join_block):
            right_block = right_block.fall_through_block
        self.__propagate_phi(left_block, right_block, join_block)

    def __propagate_phi(self, left_block, right_block, join_block):
        for id in join_block.symbol_table:
            existing_val = join_block.symbol_table[id]
            if existing_val is None or existing_val.op_code != opc.phi:
                if left_block.symbol_table[id] != right_block.symbol_table[id]:
                    phi = IR_Two_Operand(opc.phi, left_block.symbol_table[id], right_block.symbol_table[id])
                    join_block.instructions.insert(0, phi)
                    join_block.symbol_table[id] = phi
                else:
                    join_block.symbol_table[id] = left_block.symbol_table[id]
            elif existing_val.op_code == opc.phi:
                #in case of loop, left block is the main while header block
                if join_block != left_block:
                    existing_val.operand1 = left_block.symbol_table[id]
                existing_val.operand2 = right_block.symbol_table[id]

    def __get_instruction(self, opcode, operand1 = None, operand2 = None):
    # check in hierarchy of search data structure
        if opcode == opc.const:
            prev_common_expression = self.__last_const_instruction
            while prev_common_expression is not None:
                if prev_common_expression.operand == operand1:
                    break
                prev_common_expression = prev_common_expression.prev_search_ds
        else:
            prev_common_expression = self.__search_data_structure[opcode]
            while prev_common_expression is not None:
                if isinstance(prev_common_expression, IR_Two_Operand) and prev_common_expression.operand1 == operand1 and prev_common_expression.operand2 == operand2:
                    break
                elif isinstance(prev_common_expression, IR_One_Operand) and prev_common_expression.operand == operand1:
                    break
                prev_common_expression = prev_common_expression.prev_search_ds
        return prev_common_expression

    def create_instruction(self, opcode, operand1 = None, operand2 = None):
    # creates new instruction or returns previous common sub expression
        prev_common_expression = None
        prev = None
        if opcode not in [opc.read, opc.write, opc.writeNL, opc.bra, opc.end]:
            prev_common_expression = self.__get_instruction(opcode, operand1, operand2)
            prev = self.__last_const_instruction if opcode == opc.const else self.__search_data_structure[opcode]
        
        # if not found in search data structure, then create new instruction
        if prev_common_expression is None:
            self.__search_data_structure[opcode] = self.__create_IR(opcode, operand1, operand2)
            if prev is not None:
                self.__search_data_structure[opcode].prev_search_ds = prev
        
        instruction = prev_common_expression if prev_common_expression is not None else self.__search_data_structure[opcode]

        return instruction
    
    def __get_blocks_for_adding_phi(self):
        join_block = self.__current_block.join_block
        dominating_block = self.__current_block.get_dominator_block()

        # case when current block is actually join block of some if else. 
        # If we don't set this then phis are not added in this when this is the fallthrough of previous nested if statement
        if join_block is None:
            join_block = self.__next_joining_phi
        
        # join_block != dominating_block is true in case of if else blocks
        if join_block is not None and join_block != dominating_block and self.__is_under_while(join_block, dominating_block) == False:
            dominating_block = join_block.get_dominator_block()

        return join_block, dominating_block

    def __is_under_while(self, join_block, dominating_block):
        dom = dominating_block
        while dom is not None:
            if dom == join_block:
                return True
            dom = dom.get_dominator_block()
        return False

    def __is_left_block(self, dominator_block, block):
    # returns true if block is left block of dominator_block
        left_block = False
        curr_block = block
        curr_dom = block.get_dominator_block()
        while(curr_dom != dominator_block):
            curr_block = curr_dom
            curr_dom = curr_block.get_dominator_block()

        if(curr_block == dominator_block.fall_through_block and curr_block.join_block != dominator_block):
            left_block = True
        return left_block

    def __added_assignment(self, id):
    # adds phi instruction in join block
        join_block, dominating_block = self.__get_blocks_for_adding_phi()
            
        if join_block != None:
            phi = None
            previous_phi = join_block.symbol_table[id]
            if previous_phi is not None and (isinstance(previous_phi, IR) == False or previous_phi.op_code != opc.phi) :
                previous_phi = None
            # left block
            if join_block != dominating_block and self.__is_left_block(dominating_block, self.__current_block) == True:
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
            # right block
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

            prev_val = join_block.symbol_table[id]
            join_block.symbol_table[id] = phi
            if self.__is_under_while(join_block, dominating_block) and prev_val != phi:
                self.__update_instructions_using_variable(id, prev_val, phi, join_block)

    def __get_all_instructions_under_block(self, block, except_block):
        instructions = self.__get_all_instructions_under_block_rec(block, except_block, [])
        return instructions

    def __get_all_instructions_under_block_rec(self, block, except_block, instructions):
        instructions = instructions + block.instructions
        for_join = None
        if block.fall_through_block is not None and except_block != block.fall_through_block:
            instructions = self.__get_all_instructions_under_block_rec(block.fall_through_block, except_block, instructions)
            for_join = block.fall_through_block.join_block
        if block.branch_block is not None and except_block != block.fall_through_block:
            instructions = instructions + block.branch_block.instructions
            for_join = block.branch_block.join_block
        if for_join is not None and for_join != except_block:
            instructions = instructions + for_join.instructions
        return instructions

    def __update_instructions_using_variable(self, variable_id, old_val, new_val, block): 
        all_instructions = self.__get_all_instructions_under_block(block, self.__current_block) + self.__current_block.instructions
        for instruction in all_instructions:
            modified = False
            op1 = None
            op2 = None
            if instruction.instruction_number < new_val.instruction_number:
                if isinstance(instruction, IR_One_Operand) and instruction.operand == old_val:
                    op1 = instruction.operand
                    instruction.operand = new_val
                    modified = True
                elif isinstance(instruction, IR_Two_Operand):
                    # if instruction is phi, then left parameter is not updated as it came from dominating block of join block and not the fall through
                    if instruction.operand1 == old_val and (instruction.op_code != opc.phi or instruction in self.__current_block.instructions):
                        op1 = instruction.operand1
                        op2 = instruction.operand2
                        instruction.operand1 = new_val
                        modified = True
                    elif instruction.operand2 == old_val:
                        op1 = instruction.operand1
                        op2 = instruction.operand2
                        instruction.operand2 = new_val
                        modified = True
                if modified == True:
                    for id in self.__current_block.symbol_table:
                        if id != variable_id and self.__current_block.symbol_table[id].instruction_number == instruction.instruction_number:
                            if isinstance(instruction, IR_One_Operand):
                                replaced_instr = IR_One_Operand(instruction.op_code, op1)
                                self.__current_block.instructions.append(replaced_instr)
                                self.set_identifier_val(id, replaced_instr)
                            elif isinstance(instruction, IR_Two_Operand):
                                replaced_instr = IR_Two_Operand(instruction.op_code, op1, op2)
                                self.__current_block.instructions.append(replaced_instr)
                                self.set_identifier_val(id, replaced_instr)           

    def __create_IR(self, opcode, operand1, operand2):
        instruction = None
        
        if opcode in [opc.add, opc.sub, opc.mul, opc.div, opc.cmp, opc.bne, opc.beq, opc.ble, opc.blt, opc.bge, opc.bgt]:
            instruction = IR_Two_Operand(opcode, operand1, operand2)
        elif opcode in [opc.end, opc.read, opc.writeNL]:
            instruction = IR(opcode)
        elif opcode in [opc.bra, opc.const, opc.write]:
            instruction = IR_One_Operand(opcode, operand1)
        else:
            raise Exception(f"Unknown command '{opcode}'!")

        match opcode:
            case opc.const:
                self.__root_block.instructions.append(instruction)
                instruction.prev_search_ds = self.__last_const_instruction
                self.__last_const_instruction = instruction
            case _:
                self.__current_block.instructions.append(instruction)

        return instruction
        