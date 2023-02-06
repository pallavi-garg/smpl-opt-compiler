import sys
from main_project.parser import Parser
from main_project.file_reader import File_Reader
import argparse
from main_project.dot_graph import Dot_Graph as dot

def print_warnings(parser):
    warnings = parser.warnings
    if len(warnings) > 0:
        print("\n-------Warnings------")
        for warning in warnings:
            print(warning)
        print("---------------------\n")

def compile():

    arg_parser = argparse.ArgumentParser(description="Compiles code of smpl language.")
    arg_parser.add_argument("file_path", help="Path of the file to compile.")
    args = arg_parser.parse_args()

    reader = File_Reader(args.file_path)
    p = Parser(reader.get_contents())

    try:
        control_flow_graph = p.parse()
        print_warnings(p)
        dot_graph = dot()
        print(dot_graph.get_representation(control_flow_graph))
    
    except Exception as ex:
        print_warnings(p)
        print(ex)
        return -1
        
    return 0

if __name__ == "__main__":
    sys.exit(compile())