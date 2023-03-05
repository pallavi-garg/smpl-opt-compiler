from .cfg import Control_Flow_Graph as cfg
from .intermediate_representation import IR_One_Operand

class Dot_Graph:
# class that creates dot graph presentation graph of given cfg

    def __init__(self):
        self.__declarations = []
        self.__relations = []

    def get_representation(self, graph):
        for block in graph.get_blocks():
            self.__traverse_node(block)
        representation = "digraph G {\n"
        
        for declaration in self.__declarations:
            representation += f"{declaration}\n"

        for relation in self.__relations:
            representation += f"{relation}\n"

        representation += '}'

        self.__declarations.clear()
        self.__relations.clear()

        return representation

    def __traverse_node(self, node):
        self.__declarations.append(f"{node} [shape=record, label=\"<b>{node} | {self.__traverse_instructions(node)}\"];")
        fallthrough = f"[label=\" fall-through\", color=darkblue, fontcolor=darkblue]"
        loop = f"[label=\" loop\", color=brown, fontcolor=brown]"
        branch = f"[label=\" branch\", color=darkgreen, fontcolor=darkgreen]"

        if node.branch_block is not None:
            from_block = f"{node}"[2:]
            to_block = f"{node.branch_block}"[2:]
            if int(to_block) < int(from_block):
                self.__relations.append(f"{node}:s -> {node.branch_block}:n {loop};")
            else:
                self.__relations.append(f"{node}:s -> {node.branch_block} {branch};")
            
        if node.get_dominator_block() is not None:
            self.__relations.append(f"{node.get_dominator_block()}:b -> {node}:b [color=purple, style=dotted, label=\"dom\", fontcolor=purple]")
        
        if node.fall_through_block is not None:
            if len(node.get_instructions()) > 0:
                last_instruction = node.get_instructions()[-1]
                if isinstance(last_instruction, IR_One_Operand) and last_instruction.operand == node.fall_through_block:
                    fallthrough = branch
            self.__relations.append(f"{node}:s -> {node.fall_through_block} {fallthrough};")
        

    def __traverse_instructions(self, node):
        instructions = "{"
        if len(node.get_instructions()) == 0:
            instructions += "\<empty\>"
        else:
            for instruction in node.get_instructions():
                inst = f"{instruction}"
                if instruction.eliminated:
                    instructions += f" E- {inst} |"
                else:
                    instructions += f" {inst} |"
            instructions = instructions.rstrip(instructions[-1])
        instructions += "}"
        return instructions
