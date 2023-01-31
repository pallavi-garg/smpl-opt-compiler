class Control_Flow_Graph:
# Represents abstract syntax tree generated with nodes represented by Basic_Block
    
    def __init__(self):
    # constructor for control flow graph
        self.__root = Basic_Block()
        self.blocks = []
        self.blocks.append(self.__root)

    def get_new_block(self):
    # create and returns a new block
        new_block = Basic_Block()
        self.blocks.append(new_block)
        return new_block

    def get_root(self):
    # returns root block
        return self.__root

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
        self.dominant_block = dominant_block
        self.branch_block = None
        self.fall_through_block = None
        self.instructions = []
        self.use_chain = {}
        self.symbold_table = {}
    
    def __str__(self):
        return f"{self.__name}"