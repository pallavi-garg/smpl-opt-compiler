import numbers
from .cfg import Basic_Block

class IR:
# Intermediate Representation
    __next_ir_number = 0

    @staticmethod
    def get_next_ir_number():
        num = IR.__next_ir_number
        IR.__next_ir_number += 1
        return num

    def __init__(self, op_code, container):
        self.instruction_number = IR.get_next_ir_number()
        self.op_code = op_code
        self.prev_search_ds = None
        self.__container = container
        # collection of instructions where this(self) is used
        self.use_chain = [] 
        self.eliminated = False
        self.isdeleted = False

    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code}"
    
    def format_operand(self, operand):
        if self.op_code == IR_OP.param and isinstance(operand, numbers.Number):
            return f"-{operand}"
        elif(isinstance(operand, numbers.Number)) or operand == IR_Memory_Allocation.Base_Address:
            return f"#{operand}"
        elif(isinstance(operand, IR)):
            if operand.op_code == IR_OP.undefined:
                return f"(0?)"
            else:
                return f"({operand.instruction_number})"
        elif isinstance(operand, Basic_Block):
            ret = f"{operand}"
            for instruction in operand.get_instructions():
                if instruction.eliminated == False:
                    ret = f"{operand}{self.format_operand(instruction)}"
                    break
            return ret
        else:
            return f"{operand}"

    def __eq__(self, other) -> bool:
        return isinstance(other, IR) and self.instruction_number == other.instruction_number
    
    def get_container(self):
        return self.__container
    
    def __hash__(self) -> int:
        return self.instruction_number
    
class IR_One_Operand(IR):
# Intermediate Representation with 1 operand
    def __init__(self, op_code, operand, container):
        super().__init__(op_code, container)
        self.operand = operand
    
    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand)}"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, IR_One_Operand) and f"{self}" == f"{other}"

    def __hash__(self) -> int:
        return self.instruction_number

class IR_Two_Operand(IR):
# Intermediate Representation with 2 operands
    def __init__(self, op_code, operand1, operand2, container):
        super().__init__(op_code, container)
        self.operand1 = operand1
        self.operand2 = operand2
    
    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand1)}, {self.format_operand(self.operand2)}"

    def __eq__(self, other) -> bool:
        return isinstance(other, IR_Two_Operand) and f"{self}" == f"{other}"

    def __hash__(self) -> int:
        return self.instruction_number
    
class IR_Phi(IR_Two_Operand):
# Intermediate Representation with 2 operands
    def __init__(self, operand1, operand2, container, var = None):
        super().__init__(IR_OP.phi, operand1, operand2, container)
        self.var = var
    
    def __hash__(self) -> int:
        return self.instruction_number

    def __str__(self):
        s = f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand1)}, {self.format_operand(self.operand2)}"
        if self.var is not None:
            s = s + f' --- {self.var}'
        return s

class IR_Memory_Allocation(IR):
    __current_base_address = 0
    Base_Address = 'BASE'
    Integer_Size = 4 #bytes

    @staticmethod
    def get_base_address(size):
        address = IR_Memory_Allocation.__current_base_address
        IR_Memory_Allocation.__current_base_address += size
        return address

    def __init__(self, dimensions, array_name, container):
        super().__init__(IR_OP.const, container)
        size = 1
        self.array_name = array_name
        for d in dimensions:
            size *= d
        self.mem_size = size * IR_Memory_Allocation.Integer_Size
        self.dimensions = dimensions
        self.indexers = [1]
        for d in reversed(dimensions[1:]):
            self.indexers.insert(0, self.indexers[0] * d)
        self.base_address = IR_Memory_Allocation.get_base_address(self.mem_size)

    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code} #{self.array_name}_#{self.base_address}_#{self.mem_size}"

class IR_Kill(IR_One_Operand):

    def __init__(self, operand, container):
        super().__init__(IR_OP.kill, operand, container)
        self.loads = []
        self.eliminated = True

    def made_load(self, load):
        self.loads.append(load)

    def __hash__(self) -> int:
        return self.instruction_number
    
class IR_Load(IR_One_Operand):
    def __init__(self, operand, prev_load, array, container):
        super().__init__(IR_OP.load, operand, container)
        self.prev_load = prev_load
        self.array = array

    def __str__(self):
        return f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand)} ---{self.array.array_name}"
    
    def __hash__(self) -> int:
        return self.instruction_number
    
class IR_Store(IR_Two_Operand):

    def __init__(self, operand1, operand2, container, var = None, id = None):
        super().__init__(IR_OP.store, operand1, operand2, container)
        self.var = var
        self.id = id
    
    def __hash__(self) -> int:
        return self.instruction_number
    
    def __str__(self):
       return f"({self.instruction_number}) : {self.op_code} {self.format_operand(self.operand1)}, {self.format_operand(self.operand2)} --- {self.id}"
    
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
    kill = 'kill' # kill x -> forget load history of array_id
    malloc = 'malloc'
    ret = 'return'
    param = 'param'
    call = 'call'