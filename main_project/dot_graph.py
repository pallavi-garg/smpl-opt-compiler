from .cfg import Control_Flow_Graph as cfg

class Dot_Graph:
# class that creates dot graph presentation graph of given cfg

    def __init__(self):
        self.__declarations = []
        self.__relations = []

    def get_representation(self, graph):
        for block in graph.get_blocks():
            self.__traverse_node(block, graph)
        representation = "digraph G {\n"
        
        for declaration in self.__declarations:
            representation += f"{declaration}\n"

        for relation in self.__relations:
            representation += f"{relation}\n"

        representation += '}'

        self.__declarations.clear()
        self.__relations.clear()

        return representation

    def __traverse_node(self, node, graph):
        self.__declarations.append(f"{node} [shape=record, label=\"<b>{node} | {self.__traverse_instructions(node)}\"];")
        fallthrough_label = ""
        if node.branch_block is not None:
            self.__relations.append(f"{node}:s -> {node.branch_block}:n [label=\"branch\"];")
            fallthrough_label = f"[label=\"fall-through\"]"
        
        if node.fall_through_block is not None:
            self.__relations.append(f"{node}:s -> {node.fall_through_block}:n {fallthrough_label};")
        
        if node.dominant_block is not None and node.dominant_block is not graph.get_root():
            self.__relations.append(f"{node.dominant_block}:b -> {node}:b [color=blue, style=dotted, label=\"dom\"]")

    def __traverse_instructions(self, node):
        instructions = "{"
        for instruction in node.instructions:
            instructions += f" {instruction} |"
        instructions = instructions.rstrip(instructions[-1])
        instructions += "}"
        return instructions
