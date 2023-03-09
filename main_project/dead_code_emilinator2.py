from .intermediate_representation import IR_One_Operand, IR_OP, IR_Two_Operand, IR

class DE_Eliminator2:        

    def __init__(self):
        self.called_for = None

    def eliminate(self, graph, noshow = False):
        ordered_blocks = graph.sort_blocks()

        to_delete = set()
        usage = set()
        ops = [IR_OP.add, IR_OP.sub, IR_OP.mul, IR_OP.div, IR_OP.const, IR_OP.load, IR_OP.adda]

        for block in ordered_blocks:
            for instruction in reversed(block.get_instructions()):
                if instruction in usage or instruction.op_code not in ops:
                    if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
                        usage.add(instruction.operand)
                    elif isinstance(instruction, IR_Two_Operand):
                        if isinstance(instruction.operand1, IR):
                            usage.add(instruction.operand1)
                        if isinstance(instruction.operand2, IR):
                            usage.add(instruction.operand2)
                elif instruction.op_code in ops:
                    to_delete.add(instruction)
                
                if instruction.op_code == IR_OP.phi:
                    op2 = instruction.operand2
                    if op2 in to_delete:
                        to_delete.remove(op2)
                        self.called_for = op2
                        dependencies = self.__get_dependencies(op2)
                        for d in dependencies:
                            if d in to_delete:
                                to_delete.remove(d)
                                usage.add(d)
                
        for instruction in to_delete:
            if instruction.op_code in ops:
                instruction.eliminated = True
                if noshow == True:
                    instruction.get_container().remove_instruction(instruction)

    def __get_dependencies(self, instruction):
        dependencies = set()

        if isinstance(instruction, IR) == False or instruction in dependencies or instruction.op_code == IR_OP.const or instruction.op_code == IR_OP.undefined:
            return dependencies
        
        if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
            if instruction.operand != self.called_for:
                dependencies = dependencies.union(self.__get_dependencies(instruction.operand))
            dependencies.add(instruction.operand)

        elif isinstance(instruction, IR_Two_Operand):
            if isinstance(instruction.operand1, IR):
                if instruction.operand1 != self.called_for:
                    dependencies = dependencies.union(self.__get_dependencies(instruction.operand1))
                dependencies.add(instruction.operand1)

            if isinstance(instruction.operand2, IR):
                if instruction.operand2 != self.called_for:
                    dependencies = dependencies.union(self.__get_dependencies(instruction.operand2))
                dependencies.add(instruction.operand2)

        return dependencies
            
    
            
