from .intermediate_representation import IR, IR_One_Operand, IR_Two_Operand, IR_OP as opc
from .cfg import Control_Flow_Graph, Basic_Block as bb

class SSA_Engine:
    # holds objects required in SSA calculations
    def __init__(self):
        self.__initialize_ds()    
        self.__cfg = Control_Flow_Graph()
        self.__root_block = self.__cfg.get_root()
        self.__current_block = self.__root_block

    def __initialize_ds(self):
    # initialized search data structure with None references to supported opcodes
        self.__search_data_structure = {}
        self.__search_data_structure[opc.add] = None
        self.__search_data_structure[opc.sub] = None
        self.__search_data_structure[opc.mul] = None
        self.__search_data_structure[opc.div] = None
        self.__search_data_structure[opc.const] = None

    def get_instruction(self, opcode, operand1 = None, operand2 = None): #, ir_num = 0):
    # check in hierarchy of search data structure
        prev_common_expression = self.__search_data_structure[opcode]
        while prev_common_expression is not None: # and prev_common_expression.instruction_number >= ir_num:
            if isinstance(prev_common_expression, IR_Two_Operand) and prev_common_expression.operand1 == operand1 and prev_common_expression.operand2 == operand2:
                break
            elif isinstance(prev_common_expression, IR_One_Operand) and prev_common_expression.operand == operand1:
                break;
            prev_common_expression = prev_common_expression.prev_search_ds
        return prev_common_expression

    def create_instruction(self, opcode, operand1 = None, operand2 = None):
    # creates new instruction or returns previous common sub expression
        prev_common_expression = None
        prev = None
        if opcode not in [opc.read, opc.write, opc.writeNL]:
            prev_common_expression = self.get_instruction(opcode, operand1, operand2)
            prev = self.__search_data_structure[opcode]
        
        # if not found in search data structure, then create new instruction
        if prev_common_expression is None:
            self.__search_data_structure[opcode] = self.__create_IR(opcode, operand1, operand2)
            if prev is not None:
                self.__search_data_structure[opcode].prev_search_ds = prev
        instruction = prev_common_expression if prev_common_expression is not None else self.__search_data_structure[opcode]
        return instruction

    def __create_IR(self, opcode, operand1, operand2):
        instruction = None
        match opcode:
            case opc.add:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.sub:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.mul:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.div:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.cmp:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.phi:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.end:
                instruction = IR(opcode)
            case opc.bra:
                instruction = IR_One_Operand(opcode, operand1)
            case opc.bne:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.beq:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.ble:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.blt:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.bge:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.bgt:
                instruction = IR_Two_Operand(opcode, operand1, operand2)
            case opc.const:
                instruction = IR_One_Operand(opcode, operand1)
            case opc.read:
                instruction = IR(opcode)
            case opc.write:
                instruction = IR_One_Operand(opcode, operand1)
            case opc.writeNL:
                instruction = IR(opcode)
            case _:
                raise Exception("Unknown command!")
        print(f"{instruction}")
            
        return instruction