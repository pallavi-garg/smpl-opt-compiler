from .cfg import Control_Flow_Graph as cfg
from .intermediate_representation import IR_One_Operand, IR_OP

class Dot_Graph:
# class that creates dot graph presentation graph of given cfg

    def __init__(self):
        self.__declarations = []
        self.__relations = []
        self.__callings = {}

    def get_representation(self, graphs):
        representation = "digraph G {\ngraph [nodesep=0.5 ranksep=0.75]"
        for name, graph in graphs.items():
            representation += "\nsubgraph cluster_"
            representation += name
            representation += "\n{label="
            representation += f"{name}\n"
            representation += self.__get_representation(graph)
            representation += '\n}'
        
        for caller, callee in self.__callings.items():
            block = graphs[callee].get_blocks()[0]
            representation += f"{caller} -> {block}:n [label=call style=dotted]"
        
        representation += '\n}'

        self.__callings.clear()
        return representation

    def __get_representation(self, graph):  
        representation = ""
        for block in graph.get_blocks():
            self.__traverse_node(block)
        
        for declaration in self.__declarations:
            representation += f"{declaration}\n"

        for relation in self.__relations:
            representation += f"{relation}\n"

        self.__declarations.clear()
        self.__relations.clear()

        return representation

    def __traverse_node(self, node):
        self.__declarations.append(f"{node} [shape=record, label=\"<b>{node} | {self.__traverse_instructions(node)}\"];")
        fallthrough = f"[label=\" follow\", color=darkblue, fontcolor=darkblue]"
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
            self.__relations.append(f"{node.get_dominator_block()}:b -> {node}:b [color=purple, style=dotted, fontcolor=purple]")
        
        if node.fall_through_block is not None:
            if len(node.get_instructions()) > 0:
                last_instruction = node.get_instructions()[-1]
                if isinstance(last_instruction, IR_One_Operand) and last_instruction.operand == node.fall_through_block:
                    fallthrough = branch
                elif last_instruction.op_code == IR_OP.bra:
                    fallthrough = branch
            self.__relations.append(f"{node}:s -> {node.fall_through_block} {fallthrough};")
        

    def __traverse_instructions(self, node):
        instructions = "{"
        if len(node.get_instructions()) == 0:
            instructions += "\<empty\>"
        else:
            for instruction in node.get_instructions():
                inst = f"{instruction}"
                calling = instruction.get_calling_info()
                if calling != None:
                    inst = f"<{instruction.instruction_number}> {inst}"
                    self.__callings[f"\n{instruction.get_container()}:{instruction.instruction_number}:_"] = calling
                if instruction.eliminated:
                    instructions += f" * {inst} |"
                else:
                    instructions += f" {inst} |"
            instructions = instructions.rstrip(instructions[-1])
        instructions += "}"
        return instructions
