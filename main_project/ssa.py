from .intermediate_representation import IR, IR_One_Operand, IR_Two_Operand, IR_OP as opc, IR_Phi, IR_Memory_Allocation, IR_Kill
from .cfg import Control_Flow_Graph, Basic_Block as bb
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
        self.__int_size = None
        self.__base_address = None
        self.__kills = set()
    
    def get_cfg(self):
    # returns cfg
        self.__cfg.clean_up()
        return self.__cfg       

    def is_indentifier_uninitialized(self, id):
    # returns warnings found by ssa engine
        un_inititalized = False
        val = self.__current_block.symbol_table[id]
        if isinstance(val, IR_Phi):
            return self.__is_undefined(val, [])
        elif self.uninitialized_instruction == val:
            un_inititalized = True
        return un_inititalized

    def __is_undefined(self, operand, already_looked_instructions):
    # returns true if operand is undefined variable value
        if self.uninitialized_instruction == operand:
            already_looked_instructions.append(operand)
            return True
        elif isinstance(operand, IR_One_Operand):
            already_looked_instructions.append(operand)
            return operand.op_code == opc.undefined
        elif operand not in already_looked_instructions and isinstance(operand, IR_Two_Operand):
            already_looked_instructions.append(operand)
            val = self.__is_undefined(operand.operand1, already_looked_instructions) or self.__is_undefined(operand.operand2, already_looked_instructions)
            return val
        else:
            already_looked_instructions.append(operand)
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

    def get_array_value(self, id, indices):
        return self.create_compound_instruction(opc.load, id, indices)   

    def set_array_value(self, id, indices, value):  
        return self.create_compound_instruction(opc.store, id, indices, value) 
    
    def split_block(self):
        if len(self.__current_block.get_instructions()) > 0:
            prev = self.__current_block
            self.__current_block = self.__cfg.get_new_block()
            self.__current_block.set_dominator_block(prev)
            prev.fall_through_block = self.__current_block

    def update_join_block(self):
        for id in self.__current_block.symbol_table:
            val = self.__current_block.symbol_table[id]
            if isinstance(val, IR_Memory_Allocation) == False:
                phi = IR_Phi(val, None)
                self.__current_block.add_instruction(phi)
                self.__current_block.symbol_table[id] = phi
                if isinstance(phi.operand1, IR):
                    phi.operand1.use_chain.append(phi)

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
            if left_block.fall_through_block is None:
                left_block = left_block.branch_block.branch_block
            else:
                left_block = left_block.fall_through_block
        while(right_block.fall_through_block != join_block):
            if right_block.fall_through_block is None:
                right_block = right_block.branch_block.branch_block
            else:
                right_block = right_block.fall_through_block
        
        self.__propagate_phi(left_block, right_block, join_block, True)
    
    def cleanup_phi(self, join_block):
        to_delete = []
        modified = []
        for phi_instruction in join_block.get_instructions():
            if isinstance(phi_instruction, IR_Phi):
                if phi_instruction.instruction_number == phi_instruction.operand2.instruction_number:
                    for instruction in phi_instruction.use_chain:
                        if isinstance(instruction, IR_One_Operand) and instruction.operand == phi_instruction:
                            instruction.operand = phi_instruction.operand1
                            modified.append(instruction)
                        elif isinstance(instruction, IR_Two_Operand):
                            if instruction.operand1 == phi_instruction:
                                instruction.operand1 = phi_instruction.operand1
                                modified.append(instruction)
                            if instruction.operand2 == phi_instruction:
                                instruction.operand2 = phi_instruction.operand1
                                modified.append(instruction)
                    to_delete.append(phi_instruction)
        for id in join_block.symbol_table:
            if join_block.symbol_table[id] in to_delete:
                join_block.symbol_table[id] = join_block.symbol_table[id].operand1
        
        for phi in to_delete:
            join_block.remove_instruction(phi)
        
        self.__update_modified(modified)

    def __update_modified(self, modified_instructions):
        while(len(modified_instructions) != 0):
            instruction = modified_instructions.pop()
            original_instruction = self.__search_ds.get_next(instruction)
            block = instruction.get_container()
            if original_instruction is not None:
                self.__search_ds.delete(instruction)
                block.remove_instruction(instruction)
                for used in instruction.use_chain:
                    if isinstance(used, IR_One_Operand) and used.operand == instruction:
                        used.operand = original_instruction
                        modified_instructions.append(used)
                    if isinstance(used, IR_Two_Operand):
                        if used.operand1 == instruction:
                            used.operand1 = original_instruction
                            modified_instructions.append(used)
                        if used.operand2 == instruction:
                            used.operand2 = original_instruction
                            modified_instructions.append(used)
        
    def __propagate_phi(self, left_block, right_block, join_block, create_new = False):
        for kill in self.__kills:
            new_kill = IR_Kill(kill.operand, join_block)
            join_block.add_instruction(new_kill, 0)
            self.__search_ds.add(opc.load, new_kill)        
        self.__kills.clear()
        
        for id in join_block.symbol_table:
            existing_val = join_block.symbol_table[id]
            if isinstance(existing_val, IR_Memory_Allocation) == False and (existing_val is None or create_new or isinstance(existing_val, IR_Phi) == False):
                if left_block.symbol_table[id] != right_block.symbol_table[id]:
                    phi = IR_Phi(left_block.symbol_table[id], right_block.symbol_table[id])
                    join_block.add_instruction(phi, 0)
                    join_block.symbol_table[id] = phi
                    if isinstance(phi.operand1, IR):
                        phi.operand1.use_chain.append(phi)
                    if isinstance(phi.operand2, IR):
                        phi.operand2.use_chain.append(phi)
                else:
                    join_block.symbol_table[id] = left_block.symbol_table[id]
            elif isinstance(existing_val, IR_Phi):
                #in case of loop, left block is the main while header block
                if join_block != left_block:
                    existing_val.operand1 = left_block.symbol_table[id]
                existing_val.operand2 = right_block.symbol_table[id]
                if existing_val.operand2:
                    existing_val.operand2.use_chain.append(existing_val)

    def end_loop_control_flow(self, right, join_block):
        self.__control_flow_main_blocks.pop()
        self.__current_block.branch_block = join_block

        self.__propagate_phi(join_block, self.__current_block, join_block)
        self.cleanup_phi(join_block)

        self.__current_block = right
        self.__current_block.symbol_table = join_block.symbol_table

    def create_instruction(self, opcode, operand1 = None, operand2 = None):
    # creates new instruction or returns previous common sub expression
        created_new = False
        instruction = self.__search_ds.get(opcode, operand1, operand2, self.__current_block)
                
        # if not found in search data structure, then create new instruction
        if instruction is None:
            created_new = True
            if opcode in [opc.add, opc.sub, opc.mul, opc.div, opc.cmp, opc.bne, opc.beq, opc.ble, opc.blt, opc.bge, opc.bgt]:
                instruction = IR_Two_Operand(opcode, operand1, operand2, self.__current_block)
                self.__current_block.add_instruction(instruction)
            elif opcode in [opc.end, opc.read, opc.writeNL]:
                instruction = IR(opcode, self.__current_block)
                self.__current_block.add_instruction(instruction)
            elif opcode in [opc.bra, opc.write]:
                instruction = IR_One_Operand(opcode, operand1, self.__current_block)
                self.__current_block.add_instruction(instruction)
            elif opcode == opc.const:
                instruction = IR_One_Operand(opcode, operand1, self.__root_block)
                self.__root_block.add_instruction(instruction)
            elif opcode == opc.malloc:
                instruction = IR_Memory_Allocation(operand1, self.__root_block)
                self.__root_block.add_instruction(instruction)
            else:
                raise Exception(f"Unknown command '{opcode}'!")
            self.__search_ds.add(opcode, instruction)

            if isinstance(operand1, IR):
                operand1.use_chain.append(instruction)         
            if isinstance(operand2, IR):
                operand2.use_chain.append(instruction)

        return instruction, created_new      

    def __get_location(self, id, indices):
        val = self.__current_block.symbol_table[id]
        mul = None
        add = None
        location_instructions = []
        
        for index in range(0, len(indices)):
            if isinstance(indices[index], IR):
                index_offset = indices[index]  
            else:
                index_offset, _ = self.create_instruction(opc.const, indices[index])
            size_offset, _ = self.create_instruction(opc.const, val.indexers[index])
            mul, created_new = self.create_instruction(opc.mul, index_offset, size_offset)
            location_instructions.append((mul, created_new))
            if add is not None:
                add, created_new = self.create_instruction(opc.add, add, mul)
                location_instructions.append((add, created_new))
            else:
                add = mul

        if self.__int_size is None:
            self.__int_size, _ = self.create_instruction(opc.const, IR_Memory_Allocation.Integer_Size)
        mul, created_new = self.create_instruction(opc.mul, add, self.__int_size)
        location_instructions.append((mul, created_new))
        return location_instructions
    
    def create_compound_instruction(self, opcode, id, indices, value = None):  
        temp_instructions = self.__get_location(id, indices)      
        index, _ = temp_instructions[-1]
        if self.__base_address is None:
            self.__base_address, _ = self.create_instruction(opc.const, IR_Memory_Allocation.Base_Address)
        
        array_address_ptr, created_new = self.create_instruction(opc.add, self.__base_address, self.__current_block.symbol_table[id])
        temp_instructions.append((array_address_ptr, created_new))

        array_location = IR_Two_Operand(opc.adda, array_address_ptr, index, self.__current_block)        
        instruction = self.__search_ds.get_load(opcode, array_address_ptr, index, self.__current_block)

        if instruction is not None:
            for temp_instruction in temp_instructions:
                if temp_instruction[1] == True:
                    self.__current_block.remove_instruction(temp_instruction)
                    self.__search_ds.delete(temp_instruction)
        else:
            if opcode == opc.load:
                instruction = IR_One_Operand(opc.load, array_location, self.__current_block)
            else:
                instruction = IR_Two_Operand(opc.store, value, array_location, self.__current_block)
            self.__current_block.add_instruction(array_location)
            self.__current_block.add_instruction(instruction)
            self.__search_ds.add(opcode, instruction)

            if opcode == opc.store:
                kill = IR_Kill(array_location, self.__current_block)
                self.__current_block.add_instruction(kill)
                self.__search_ds.add(opc.load, kill)
                if len(self.__control_flow_main_blocks) > 0:
                    self.__kills.add(kill)

        return instruction

        