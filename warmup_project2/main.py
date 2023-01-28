import sys
import project2_parser as pa

def main():
    if len(sys.argv) < 2:
        print("Please provide input string to parse")
    else:
        args = sys.argv[1:]
        p = pa.Parser(''.join(args))
        try:
            results = p.computation()
            for result in results:
                print(result)
        except Exception as ex:
            print(ex.args[0])

if __name__ == "__main__":
    sys.exit(main())