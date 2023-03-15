from .intermediate_representation import IR_One_Operand, IR_OP, IR_Two_Operand, IR
from .cfg import Basic_Block

class DE_Eliminator2:        

    def __init__(self):
        self.notes = {}

    def eliminate(self, graph, noshow = False):
        usage = set()
        ops = [IR_OP.add, IR_OP.sub, IR_OP.mul, IR_OP.div, IR_OP.const, IR_OP.load, IR_OP.adda, IR_OP.phi]

        defs = set()
        phi_chains = {}

        for block in reversed(graph.ordered_blocks):
            if block not in self.notes:
                self.notes[block] = []
            for instruction in reversed(block.get_instructions()):
                defs.add(instruction)
                if instruction in usage or instruction.op_code not in ops:
                    if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
                        usage.add(instruction.operand)
                    elif isinstance(instruction, IR_Two_Operand):
                        if isinstance(instruction.operand1, IR):
                            usage.add(instruction.operand1)
                        if isinstance(instruction.operand2, IR):
                            usage.add(instruction.operand2)
                elif instruction.op_code in ops:
                    if instruction.op_code == IR_OP.phi and instruction.instruction_number < instruction.operand2.instruction_number: #while loop phi
                        if instruction not in phi_chains:
                            phi_chains[instruction] = set()
                            phi_chains[instruction].add(instruction.operand1)
                            phi_chains[instruction].add(instruction.operand2)
                        else:
                            pass
                    else:
                        for phi in phi_chains:
                            if instruction in phi_chains[phi]:
                                if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
                                    phi_chains[phi].add(instruction.operand)
                                elif isinstance(instruction, IR_Two_Operand):
                                    if isinstance(instruction.operand1, IR):
                                        phi_chains[phi].add(instruction.operand1)
                                    if isinstance(instruction.operand2, IR):
                                        phi_chains[phi].add(instruction.operand2)

        for phi in phi_chains:
            if phi in usage:
                usage = usage.union(phi_chains[phi])

        #ops.append(IR_OP.kill)
                
        for instruction in defs:
            if instruction.op_code in ops and instruction not in usage:
                instruction.eliminated = True
                if noshow == True:
                    block = instruction.get_container()
                    block.remove_instruction(instruction)
                    self.notes[block].append(instruction)

        if noshow == True:
            graph.clean_up()
        
        for instruction in defs:
            if isinstance(instruction, IR_One_Operand) and  isinstance(instruction.operand, Basic_Block):
                instruction.operand = self.__get_instruction(instruction.operand)
            elif isinstance(instruction, IR_Two_Operand) and  isinstance(instruction.operand2, Basic_Block):
                instruction.operand2 = self.__get_instruction(instruction.operand2)

    def __get_instruction(self, block):
        instruction = block
        for i in block.get_instructions():
            if i.eliminated == False:
                instruction = i
                break
        return instruction

            
    
            
