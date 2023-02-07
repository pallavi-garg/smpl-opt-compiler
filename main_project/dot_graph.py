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
            self.__relations.append(f"{node} -> {node.branch_block} [label=\"branch\"];")
            fallthrough_label = f"[label=\"fall-through\"]"
        
        if node.fall_through_block is not None:
            if node.fall_through_block == node.get_dominator_block():
                self.__relations.append(f"{node} -> {node.fall_through_block} [label=\"loop\", color=red, fontcolor=red];")
            else:
                self.__relations.append(f"{node} -> {node.fall_through_block} {fallthrough_label};")
        
        if node.get_dominator_block() is not None:
            self.__relations.append(f"{node.get_dominator_block()}:b -> {node}:b [color=blue, fontcolor=blue, style=dotted, label=\"dom\"]")

    def __traverse_instructions(self, node):
        instructions = "{"
        if len(node.instructions) == 0:
            instructions += "\<empty\>"
        else:
            for instruction in node.instructions:
                instructions += f" {instruction} |"
            instructions = instructions.rstrip(instructions[-1])
        instructions += "}"
        return instructions
