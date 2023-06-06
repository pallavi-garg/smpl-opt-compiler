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
        warnings = f"\n-------Warnings-------\n"
        for warning in parser.warnings:
            warnings = f"{warnings}\n{warning}"
        warnings = f"{warnings}\n\n---------------------\n"
    return warnings

def compile():
    arg_parser = argparse.ArgumentParser(description="Compiles code of smpl language.")
    arg_parser.add_argument("file_path", help="Path of the file to compile.")
    args = arg_parser.parse_args()
    file_path = args.file_path    
    '''
    file_path = '/home/pallavi/workspace/Compiler/compiler/smpl-opt-compiler/testfiles/test.smpl'
    '''
    
    reader = File_Reader(file_path)
    
    p = Parser(reader.get_contents())
    run_dce = True

    try:
        control_flow_graphs = p.parse()
        warnings = get_warnings(p)

        write_output(control_flow_graphs, warnings, None, file_path, 'SSA')
    except Exception as ex:
        warnings = get_warnings(p)
        if warnings is not None:
            print(warnings)
        print(f'\nException occurred during SSA: {ex}')
        return -1
    
    if run_dce:
        try:
            no_show = False
            dce = DE_Eliminator()
            for _, control_flow_graph in control_flow_graphs.items():
                dce.eliminate(control_flow_graph, no_show)
            notes = ''
            if no_show:
                notes = '\n\n-----Eliminated following instructions-----\n'

            for note in dce.notes:
                if len(dce.notes[note]) > 0:
                    notes = notes + f'{note}:\n'
                    for r in dce.notes[note]:
                        notes = notes + f'{r}\n'

            write_output(control_flow_graphs, warnings, notes, file_path, 'After DCE', 'w', 'dce')

        except Exception as ex:
            print(f'\n\n\nException occurred during DCE: {ex}')
            return -1
    
    
        
    return 0

def write_output(control_flow_graphs, warnings, notes, file_path, title, mode = 'w', suffix = ''):
    dot_graph = dot()
    output = dot_graph.get_representation(control_flow_graphs)
    if warnings is not None:
        print(warnings)
    print(output)
    if notes is not None:
        print(notes)
    writer = File_Writer()
    writer.write(file_path, title, warnings, notes, output, mode, suffix)

    #Only supported on linux
    copy_clipboard(output)

if __name__ == "__main__":
    sys.exit(compile())