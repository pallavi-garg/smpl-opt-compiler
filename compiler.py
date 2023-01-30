import sys
from main_project.parser import Parser
from main_project.file_reader import File_Reader
import argparse

def compile():

    arg_parser = argparse.ArgumentParser(description="Compiles code of smpl language.")
    arg_parser.add_argument("file_path", help="Path of the file to compile.")
    args = arg_parser.parse_args()
    
    try:
        reader = File_Reader(args.file_path)
        p = Parser(reader.get_contents())
        results, warnings = p.computation()
        for warning in warnings:
            print(warning)
        for result in results:
            print(result)
    except Exception as ex:
        print(ex)
        return -1
    
    return 0

if __name__ == "__main__":
    sys.exit(compile())