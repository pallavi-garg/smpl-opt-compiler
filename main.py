import sys
from warmup_project2.parser import Parser

def main():
    if len(sys.argv) < 2:
        print("Please provide input string to parse")
    else:
        args = sys.argv[1:]
        p = Parser(''.join(args))
        p.computation()

if __name__ == "__main__":
    sys.exit(main())