import sys
from parsers import parser

def main():
    if len(sys.argv) < 2:
        print("Please provide input string to parse")
    else:
        p = parser.Parser(sys.argv[1])
        results = p.computation()
        for result in results:
            print(result)

if __name__ == "__main__":
    sys.exit(main())