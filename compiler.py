import sys
from main_project.parser import Parser
from main_project.file_reader import File_Reader, File_Writer
import argparse
from main_project.dot_graph import Dot_Graph as dot
from main_project.dead_code_emilinator import DE_Eliminator
from subprocess import Popen, PIPE

def copy_clipboard(msg):
    ''' Copy `msg` to the clipboard '''
    with Popen(['xclip','-selection', 'clipboard'], stdin=PIPE) as pipe:
        pipe.communicate(input=msg.encode('utf-8'))

def get_warnings(parser):
    warnings = None
    if len(parser.warnings) > 0:
        warnings = f"-------Warnings------"
        for warning in parser.warnings:
            warnings = f"{warnings}\n{warning}"
        warnings = f"{warnings}\n---------------------\n"
    return warnings

def compile():
    
    arg_parser = argparse.ArgumentParser(description="Compiles code of smpl language.")
    arg_parser.add_argument("file_path", help="Path of the file to compile.")
    args = arg_parser.parse_args()

    reader = File_Reader(args.file_path)
    
    #reader = File_Reader('/home/pallavi/workspace/Compiler/Compiler-Py/smpl-opt-compiler/testfiles/test.smpl')
    p = Parser(reader.get_contents())

    try:
        control_flow_graph = p.parse()
        dce = DE_Eliminator()
        dce.eliminate(control_flow_graph)

        warnings = get_warnings(p)
        dot_graph = dot()
        output = dot_graph.get_representation(control_flow_graph)
        if warnings is not None:
            print(warnings)
        print(output)
        writer = File_Writer()
        writer.write(args.file_path, warnings, output)

        #Only supported on linux
        copy_clipboard(output)
    
    except Exception as ex:
        warnings = get_warnings(p)
        if warnings is not None:
            print(warnings)
        print(ex)
        return -1
        
    return 0

if __name__ == "__main__":
    sys.exit(compile())