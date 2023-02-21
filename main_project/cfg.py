class Control_Flow_Graph:
# Represents abstract syntax tree generated with nodes represented by Basic_Block
    
    def __init__(self):
    # constructor for control flow graph
        self.__root = Basic_Block()
        self.__blocks = []
        self.__blocks.append(self.__root)

    def get_new_block(self):
    # create and returns a new block
        new_block = Basic_Block()
        self.__blocks.append(new_block)
        return new_block

    def get_root(self):
    # returns root block
        return self.__root

    def get_blocks(self):
    # returns root block
        return self.__blocks
    
    def __delete_empty_blocks(self):
        to_delete = []
        for block in self.__blocks:
            if block.branch_block is not None:
                instructions_in_branch_block = block.branch_block.get_instructions()
                if len(instructions_in_branch_block) == 0:
                    branch_instruction = block.get_instructions()[-1]
                    branch_instruction.operand2 = block.branch_block.fall_through_block
                    if branch_instruction.operand2 is None:
                        branch_instruction.operand2 = block.branch_block.branch_block
                    if branch_instruction.operand2 is None:
                        branch_instruction.operand2 = block.branch_block.join_block
                    to_delete.append(block.branch_block)
                    block.branch_block = branch_instruction.operand2
        
        for block in to_delete:
            self.__blocks.remove(block)
    
    def clean_up(self):
        self.__delete_empty_blocks()

    def print(self):
        for block in self.__blocks:
            print(f"name -> {block} : fall -> {block.fall_through_block}, branch -> {block.branch_block}, join -> {block.join_block}")
        self.clean_up()

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
        self.__name = f'BB{Basic_Block.get_next_ir_number()}'
        self.first_instruction_number = -1
        self.fall_through_block = None
        self.branch_block = None
        self.join_block = None
        self.__instructions = []
        self.symbol_table = {}
        self.set_dominator_block(dominant_block)

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
        self.__instructions.remove(instruction)
