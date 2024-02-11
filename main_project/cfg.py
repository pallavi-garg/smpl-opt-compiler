from .basic_block import Basic_Block

class Control_Flow_Graph:
# Represents abstract syntax tree generated with nodes represented by Basic_Block
    
    def __init__(self):
    # constructor for control flow graph
        self.__root = Basic_Block()
        self.__blocks = []
        self.__blocks.append(self.__root)
        self.ordered_blocks = []

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
        self.sort_blocks()
        for block in self.__blocks:
            print(f"name -> {block} : {block.processing_order} : fall -> {block.fall_through_block}, branch -> {block.branch_block}, join -> {block.join_block}")
        self.clean_up()

