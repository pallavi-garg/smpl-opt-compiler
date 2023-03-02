from .intermediate_representation import IR_OP as opc, IR_One_Operand, IR_Two_Operand, IR_Kill, IR_Store

class search_ds:
    
    def __init__(self):
        self.__map = {}
        self.__map[opc.const] = None
        self.__map[opc.add] = None
        self.__map[opc.sub] = None
        self.__map[opc.mul] = None
        self.__map[opc.div] = None
        self.__map[opc.cmp] = None
        self.__map[opc.load] = None

    def add(self, opcode, instruction):
    # adds instruction with opcode in search data structure
        if opcode in self.__map:
            prev = self.__map[opcode]
            self.__map[opcode] = instruction
            instruction.prev_search_ds = prev

    def get(self, opcode, operand1, operand2, container):
    # returns matched instruction in dominance tree
        if opcode not in self.__map:
            return None
        return self.__get_matching(container, self.__map[opcode], opcode, operand1, operand2)

    def get_next(self, instruction):
    # returns next common sub expression matching with given instruction
        op1 = None
        op2 = None
        if isinstance(instruction, IR_Two_Operand):
            op1 = instruction.operand1
            op2 = instruction.operand2
        elif isinstance(instruction, IR_One_Operand):
            op1 = instruction.operand
        return self.__get_matching(instruction.get_container(), instruction.prev_search_ds, instruction.op_code, op1, op2)

    def __get_matching(self, container, match_beginning, opcode, operand1, operand2 = None):
    # returns matched instruction in dominance tree
        matched = None
        if opcode in self.__map:
            matched = match_beginning
            while(matched is not None):
                if isinstance(matched, IR_Two_Operand) and matched.operand1 == operand1 and matched.operand2 == operand2 and self.__is_dominating(container, matched) == True:
                    break
                elif isinstance(matched, IR_One_Operand) and matched.operand == operand1 and self.__is_dominating(container, matched) == True:
                    break
                matched = matched.prev_search_ds
        return matched

    def delete(self, instruction, opcode = None):
        if opcode is None:
            opcode = instruction.op_code
        if opcode in self.__map:
            curr = self.__map[opcode]
            if curr is not None and curr == instruction:
                self.__map[opcode] = curr.prev_search_ds
            elif curr is not None:
                prev = curr
                while curr != instruction and curr is not None:
                    prev = curr
                    curr = curr.prev_search_ds
                if curr is not None and prev is not None:
                    prev.prev_search_ds = curr.prev_search_ds

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

    def get_load(self, opcode, array_instruction, array_address_ptr, index, container, min_ir_num = None):
        matched = None
        kill = None
        if opcode in self.__map:
            matched = self.__map[opcode]
            while(matched is not None):
                if min_ir_num is not None and matched.instruction_number >= min_ir_num:
                    pass
                elif matched.op_code == opc.load and matched.operand.operand1 == array_address_ptr and matched.operand.operand2 == index and self.__is_dominating(container, matched) == True:
                    break
                elif isinstance(matched, IR_Kill) and matched.operand == array_instruction and self.__is_dominating(container, matched) == True:
                    if kill is None:
                        kill = matched
                elif isinstance(matched, IR_Store) and matched.var == array_instruction:
                    matched = None
                    break
                matched = matched.prev_search_ds
        return matched, kill