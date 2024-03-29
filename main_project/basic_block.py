class Basic_Block:
# Class to represent basic block.
# All instructions in a basic block are executed together as a whole.
    __next_block_num = 0

    @staticmethod
    def get_next_ir_number():
        num = Basic_Block.__next_block_num
        Basic_Block.__next_block_num += 1
        return num

    def __init__(self, dominant_block = None):
        self.__number = Basic_Block.get_next_ir_number()
        self.__name = f'BB{self.__number}'
        self.first_instruction_number = -1
        self.fall_through_block = None
        self.branch_block = None
        self.join_block = None
        self.__instructions = []
        self.symbol_table = {}
        self.set_dominator_block(dominant_block)
        self.killed_arrays = set()
        self.temp_kills = set()

    def __eq__(self, other):
        return isinstance(other, Basic_Block) and self.__name == other.__name

    def set_dominator_block(self, dominant_block):
        self.__dominant_block = dominant_block
        if dominant_block is not None:
            self.symbol_table = self.__dominant_block.symbol_table.copy()

    def get_dominator_block(self):
        return self.__dominant_block 
    
    def __str__(self):
        return f"{self.__name}"

    def add_instruction(self, instruction, index = None):
        if self.first_instruction_number == -1:
            self.first_instruction_number = instruction.instruction_number
        if index is None:
            self.__instructions.append(instruction)
        else:
            self.__instructions.insert(index, instruction)

    def get_instructions(self):
        return self.__instructions

    def remove_instruction(self, instruction):
        if instruction in self.__instructions:
            self.__instructions.remove(instruction)
        instruction.isdeleted = True

    def __hash__(self) -> int:
        return self.__number