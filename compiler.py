import sys
from main_project.parser import Parser
from main_project.file_reader import File_Reader
import argparse

def print_warnings(parser):
    if parser.warnings:
            for warning in parser.warnings:
                print(warning)

def compile():

    arg_parser = argparse.ArgumentParser(description="Compiles code of smpl language.")
    arg_parser.add_argument("file_path", help="Path of the file to compile.")
    args = arg_parser.parse_args()
    
    try:
        reader = File_Reader(args.file_path)
        p = Parser(reader.get_contents())
        p.parse()
        print_warnings(p)
    except Exception as ex:
        print_warnings(p)
        print(ex)
        return -1
    
    return 0

if __name__ == "__main__":
    sys.exit(compile())