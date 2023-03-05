from .intermediate_representation import IR_One_Operand, IR_OP, IR_Two_Operand, IR, IR_Kill

class DE_Eliminator:        

    def __init__(self, remove_only_kill = False):
        if remove_only_kill:
            self.ops = [IR_OP.kill]
        else:
            self.ops = [IR_OP.add, IR_OP.sub, IR_OP.mul, IR_OP.div, IR_OP.kill, IR_OP.phi, IR_OP.const]
        self.defs = set()
        self.usage = set()


    def eliminate(self, graph):
        ordered_blocks = graph.sort_blocks()

        for block in ordered_blocks:
            for instruction in reversed(block.get_instructions()):
                if instruction.instruction_number == 20:
                    pass
                if instruction.eliminated == False:
                    if instruction.op_code in self.ops:
                        if instruction.op_code != IR_OP.phi or instruction not in self.usage:
                            self.defs.add(instruction)
                            if instruction in self.usage:
                                self.usage.remove(instruction)
                                self.defs.remove(instruction)

                    if isinstance(instruction, IR_One_Operand) and isinstance(instruction.operand, IR):
                        self.usage.add(instruction.operand)
                        #self.__add_usage(instruction.operand)
                    if isinstance(instruction, IR_Two_Operand):                            
                        if isinstance(instruction.operand1, IR):
                            self.usage.add(instruction.operand1)
                            #self.__add_usage(instruction.operand1)
                        if isinstance(instruction.operand2, IR):
                            self.usage.add(instruction.operand2)
                            #self.__add_usage(instruction.operand2)
                    
        for instruction in self.defs:
            if instruction not in self.usage:
                instruction.eliminated = True

        for instruction in self.defs:
            sete = True
            for uses in instruction.use_chain:
                if uses.eliminated == False and uses.isdeleted == False:
                    sete = False
                    break
            instruction.eliminated = sete
            
    def __add_usage(self, operand):
        if operand.op_code == IR_OP.phi:
            if operand.operand1 not in self.usage:
                self.__add_usage(operand.operand1)
            if operand.operand2 not in self.usage:
                self.__add_usage(operand.operand2)
        else:
            self.usage.add(operand)
            
    
            
