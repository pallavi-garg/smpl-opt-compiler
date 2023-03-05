from .intermediate_representation import IR_One_Operand, IR_OP, IR_Two_Operand, IR, IR_Kill

class DE_Eliminator:        

    def __init__(self, remove_only_kill = False):
        if remove_only_kill:
            self.ops = [IR_OP.kill]
        else:
            self.ops = [IR_OP.add, IR_OP.sub, IR_OP.mul, IR_OP.div, IR_OP.kill, IR_OP.phi, IR_OP.const]

    def __can_elimintate(self, instruction):
        return isinstance(instruction, IR) and (instruction.op_code in self.ops)
             

    def eliminate(self, graph):
        ordered_blocks = graph.sort_blocks()
        iteration = 10

        while iteration > 0:
            iteration -= 1
            to_delete = set()
            usage = set()
            for block in ordered_blocks:
                for instruction in reversed(block.get_instructions()):
                    if instruction.eliminated == False:
                        if self.__can_elimintate(instruction) and instruction not in usage:
                            to_delete.add(instruction)

                        if isinstance(instruction, IR_Kill) == False:
                            if instruction in usage and instruction in to_delete:
                                to_delete.remove(instruction)
                            if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR) and instruction.operand.eliminated == False:
                                usage.add(instruction.operand)
                                if instruction.operand in to_delete:
                                        to_delete.remove(instruction.operand)
                            elif isinstance(instruction, IR_Two_Operand):
                                if isinstance(instruction.operand1, IR) and instruction.operand1.eliminated == False:
                                    if instruction.op_code != IR_OP.phi or instruction.operand1 in usage:
                                        usage.add(instruction.operand1)
                                        if instruction.operand1 in to_delete:
                                            to_delete.remove(instruction.operand1)
                                if isinstance(instruction.operand2, IR) and instruction.operand2.eliminated == False:
                                    if instruction.op_code != IR_OP.phi or instruction.operand2 in usage:
                                        usage.add(instruction.operand2)
                                        if instruction.operand2 in to_delete:
                                            to_delete.remove(instruction.operand2)
            if len(to_delete) == 0:
                break
            else:
                for instruction in to_delete:
                    if instruction not in usage:
                        instruction.eliminated = True
                        #instruction.get_container().remove_instruction(instruction)
            
            
