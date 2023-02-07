import numbers
from .cfg import Basic_Block

class IR:
# Intermediate Representation
    __next_ir_number = -1

    @staticmethod
    def get_next_ir_number():
        num = IR.__next_ir_number
        IR.__next_ir_number += 1
        return num

    def __init__(self, op_code):
        self.instruction_number = IR.get_next_ir_number()
        self.op_code = op_code
        self.prev_search_ds = None

    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code}"
    
    def format_operand(self, operand):
        if(isinstance(operand, numbers.Number)):
            return f"#{operand}"
        elif(isinstance(operand, IR)):
            if operand.op_code == IR_OP.undefined:
                return f"(0?)"
            else:
                return f"({operand.instruction_number})"
        elif isinstance(operand, Basic_Block) and operand.instructions:
            return f"{operand}{self.format_operand(operand.instructions[0])}"
        else:
            return f"{operand}"

    def __eq__(self, other) -> bool:
        return isinstance(other, IR) and self.instruction_number == other.instruction_number
    
class IR_One_Operand(IR):
# Intermediate Representation with 1 operand
    def __init__(self, op_code, operand):
        super().__init__(op_code)
        self.operand = operand
    
    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand)}"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, IR_One_Operand) and self.instruction_number == other.instruction_number and self.operand == other.operand


class IR_Two_Operand(IR):
# Intermediate Representation with 2 operands
    def __init__(self, op_code, operand1, operand2):
        super().__init__(op_code)
        self.operand1 = operand1
        self.operand2 = operand2
    
    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand1)}, {self.format_operand(self.operand2)}"

    def __eq__(self, other) -> bool:
        return isinstance(other, IR_Two_Operand) and f"{self}" == f"{other}"

class IR_OP:
    add = 'add' # add x y       -> x+y
    sub = 'sub' # sub x y       -> x=y
    mul = 'mul' # mul x y       -> x*y
    div = 'div' # div x y       -> x/y
    cmp = 'cmp' # cmp x y       -> comparison
    phi = 'phi' # phi x y       -> compute phi(x,y)
    end = 'end' # end           -> end of program
    bra = 'bra' # bra y         -> branch to y
    bne = 'bne' # bne x y       -> branch to y on x not equal
    beq = 'beq' # beq x y       -> branch to y on x equal
    ble = 'ble' # ble x y       -> branch to y on x less or equal
    blt = 'blt' # blt x y       -> branch on y on x less
    bge = 'bge' # bge x y       -> branch on y on x greater or equal
    bgt = 'bgt' # bgt x y       -> branch on y on x greater
    adda = 'adda'   # adda x,y  -> add two addresses x and y (used with arrays)
    load = 'load'   # load x,y  -> load from memory address y
    store = 'store' # store x,y -> store y to memory x

    const = 'const' # const x   -> create constant x
    read = 'read' # read        -> for built-in function InputNum()
    write = 'write' # write x   -> for built-in function OutputNum(x)
    writeNL = 'writeNL' # writeNL -> for built-in function OutputNewLine()

    # DUMMY: do not send this to processor
    undefined = 'undefined' # value = 0, it identifies operands which are uninitialized.