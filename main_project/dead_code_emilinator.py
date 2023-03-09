from .intermediate_representation import IR_One_Operand, IR_OP, IR_Two_Operand, IR

class DE_Eliminator:        

    def __init__(self, remove_only_kill = False):
        if remove_only_kill:
            self.ops = [IR_OP.kill]
        else:
            self.ops = [IR_OP.add, IR_OP.sub, IR_OP.mul, IR_OP.div, IR_OP.kill, IR_OP.phi, IR_OP.const, IR_OP.load, IR_OP.adda]
        self.defs = set()
        self.usage = set()
        self.used_in_phi = {}


    def eliminate(self, graph):
        ordered_blocks = graph.sort_blocks()
        #use_chain = {}

        for block in ordered_blocks:
            for instruction in reversed(block.get_instructions()):
                if instruction.op_code in self.ops:
                    self.defs.add(instruction)

                if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
                    self.usage.add(instruction.operand)
                    '''
                    if instruction.operand not in use_chain:
                        use_chain[instruction.operand] = set()
                    use_chain[instruction.operand].add(instruction)
                    '''
                if isinstance(instruction, IR_Two_Operand):
                    if instruction.op_code == IR_OP.phi:
                        if instruction.operand1 not in self.used_in_phi:
                            self.used_in_phi[instruction.operand1] = []
                        self.used_in_phi[instruction.operand1].append(instruction)
                        if instruction.operand2 not in self.used_in_phi:
                            self.used_in_phi[instruction.operand2] = []
                        self.used_in_phi[instruction.operand2].append(instruction)
                    else:                            
                        if isinstance(instruction.operand1, IR):
                            self.usage.add(instruction.operand1)
                            '''
                            if instruction.operand1 not in use_chain:
                                use_chain[instruction.operand1] = set()
                            use_chain[instruction.operand1].add(instruction)
                            '''
                        if isinstance(instruction.operand2, IR):
                            self.usage.add(instruction.operand2)
                            '''
                            if instruction.operand2 not in use_chain:
                                use_chain[instruction.operand2] = set()
                            use_chain[instruction.operand2].add(instruction)
                            '''
                    
        for instruction in self.defs:
            if instruction not in self.usage:
                if instruction in self.used_in_phi:
                    all_unused = True
                    for phi in self.used_in_phi[instruction]:
                        if phi in self.usage or phi in self.used_in_phi:
                            all_unused = False
                            break
                    instruction.eliminated = all_unused
                else:
                    instruction.eliminated = True


            
    
            
