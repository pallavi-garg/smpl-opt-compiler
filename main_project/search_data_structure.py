from .intermediate_representation import IR_OP as opc, IR_One_Operand, IR_Two_Operand

class search_ds:
    
    def __init__(self):
        self.__map = {}
        self.__map[opc.const] = None
        self.__map[opc.add] = None
        self.__map[opc.sub] = None
        self.__map[opc.mul] = None
        self.__map[opc.div] = None
        self.__map[opc.cmp] = None

    def add(self, opcode, instruction):
    # adds instruction with opcode in search data structure
        if opcode in self.__map:
            prev = self.__map[opcode]
            self.__map[opcode] = instruction
            instruction.prev_search_ds = prev

    def get(self, opcode, operand1, operand2, container):
    # returns matched instruction in dominance tree
        matched = None
        if opcode in self.__map:
            matched = self.__map[opcode]
            while(matched is not None):
                if isinstance(matched, IR_Two_Operand) and matched.operand1 == operand1 and matched.operand2 == operand2 and self.__is_dominating(container, matched) == True:
                    break
                elif isinstance(matched, IR_One_Operand) and matched.operand == operand1 and self.__is_dominating(container, matched) == True:
                    break
                matched = matched.prev_search_ds
        return matched

    def __is_dominating(self, container, instruction):
        if container == instruction.get_container():
            return True
        else:
            dom = container.get_dominator_block()
            while dom is not None:
                if dom == instruction.get_container():
                    return True
                dom = dom.get_dominator_block()
        return False