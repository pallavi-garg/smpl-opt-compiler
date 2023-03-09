from .intermediate_representation import IR_One_Operand, IR_OP, IR_Two_Operand, IR

class DE_Eliminator:        

    def __init__(self):
        self.ops = [IR_OP.add, IR_OP.sub, IR_OP.mul, IR_OP.div, IR_OP.phi, IR_OP.const, IR_OP.load, IR_OP.adda]
        


    def eliminate(self, graph, noshow = False):
        ordered_blocks = graph.sort_blocks()

        use_chain = {}
        defs = set()
        usage = set()
        used_in_phi = {}

        for block in ordered_blocks:
            for instruction in reversed(block.get_instructions()):
                if instruction.op_code in self.ops:
                    defs.add(instruction)

                if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
                    usage.add(instruction.operand)
                    
                    if instruction.operand not in use_chain:
                        use_chain[instruction.operand] = set()
                    use_chain[instruction.operand].add(instruction)
                    
                if isinstance(instruction, IR_Two_Operand):
                    if instruction.op_code == IR_OP.phi:
                        if instruction.operand1 not in used_in_phi:
                            used_in_phi[instruction.operand1] = []
                        used_in_phi[instruction.operand1].append(instruction)
                        if instruction.operand2 not in used_in_phi:
                            used_in_phi[instruction.operand2] = []
                        used_in_phi[instruction.operand2].append(instruction)
                    else:                            
                        if isinstance(instruction.operand1, IR):
                            usage.add(instruction.operand1)
                            
                            if instruction.operand1 not in use_chain:
                                use_chain[instruction.operand1] = set()
                            use_chain[instruction.operand1].add(instruction)
                            
                        if isinstance(instruction.operand2, IR):
                            usage.add(instruction.operand2)
                            
                            if instruction.operand2 not in use_chain:
                                use_chain[instruction.operand2] = set()
                            use_chain[instruction.operand2].add(instruction)
                            
                    
        for instruction in defs:
            if instruction not in usage:
                if instruction in used_in_phi:
                    all_unused = True
                    for phi in used_in_phi[instruction]:
                        if phi in usage or phi in used_in_phi:
                            all_unused = False
                            break
                    instruction.eliminated = all_unused
                else:
                    instruction.eliminated = True
                if noshow and instruction.eliminated:
                    instruction.get_container().remove_instruction(instruction)

        for load in defs:
            if load.op_code == IR_OP.load:
                if load in use_chain:
                    all_unused = len(use_chain[load]) > 0
                    for use in use_chain[load]:
                        if use.eliminated == False:
                            all_unused = False
                            break
                    if all_unused and load not in used_in_phi:
                        load.eliminated = all_unused
                        if noshow and load.eliminated:
                            load.get_container().remove_instruction(load)
                        if all_unused:
                            load.operand.eliminated = True
                            if noshow and load.operand.eliminated:
                                load.operand.get_container().remove_instruction(load.operand)
                            if load.operand.operand1 in use_chain:
                                all_unused = len(use_chain[load.operand.operand1]) > 0
                                for use in use_chain[load.operand.operand1]:
                                    if use.eliminated == False:
                                        all_unused = False
                                        break
                                load.operand.operand1.eliminated = all_unused
                                if noshow and load.operand.operand1.eliminated:
                                    load.operand.operand1.get_container().remove_instruction(load.operand.operand1)
                    
        for instruction in defs:
            if instruction in use_chain:
                if instruction in use_chain:
                    all_unused = len(use_chain[instruction]) > 0
                    for use in use_chain[instruction]:
                        if use.eliminated == False:
                            all_unused = False
                            break
                    instruction.eliminated = all_unused
                    if noshow and instruction.eliminated:
                        instruction.get_container().remove_instruction(instruction)

            
    
            
