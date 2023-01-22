import sys
from warmup_project2.parser import Parser

def main():
    if len(sys.argv) < 2:
        print("Please provide input string to parse")
    else:
        args = sys.argv[1:]
        p = Parser(''.join(args))
        try:
            p.computation()
        except Exception as ex:
            print(ex.args[0])

if __name__ == "__main__":
    sys.exit(main())