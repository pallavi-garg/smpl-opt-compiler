"""
Parser for grammar defined in ../grammars/arithmetic_grammar.txt

"""

class Arithmetic_Parser:

    # constructor initialization
    def __init__(self, input_string):
        self.input_string = input_string.strip()
        self.position = 0
        self.len = len(self.input_string)
    
    # entry point for this parser
    def computation(self):
        results = []
        val = self.__expression()
        if self.position < self.len and self.input_string[self.position] == '.':
            results.append(val)
        else:
            results.append("Syntax Error - missing dot at end of expression")
        
        while self.position < self.len and self.input_string[self.position] == '.':
            self.__next()
            if self.position < self.len:
                val = self.__expression()
                if self.position < self.len and self.input_string[self.position] == '.':
                    results.append(val)
                else:
                    results.append("Syntax Error - missing dot at end of expression")
                    break
        return results

    # advance the position to __next character
    def __next(self):
        self.position += 1

    # advances to __next position is current position is space
    def __skip_space(self):
        while self.position < self.len and self.input_string[self.position].isspace():
            self.__next()

    # calculates expression
    def __expression(self):
        val = self.__term();
        while self.position < self.len and (self.input_string[self.position] == '+' or self.input_string[self.position] == '-'):
            if self.input_string[self.position] == '+':
                self.__next();
                val += self.__term();
            elif self.input_string[self.position] == '-':
                self.__next();
                val -= self.__term();
        return val

    # calculates term
    def __term(self):
        val = self.__factor()
        while self.position < self.len and (self.input_string[self.position] == '*' or self.input_string[self.position] == '/'):
            if self.input_string[self.position] == '*':
                self.__next()
                val *= self.__factor();
            elif self.input_string[self.position] == '/':
                self.__next()
                val = int (val/self.__factor())
        return val

    # calculates factor
    def __factor(self):
        val = 0
        self.__skip_space()
        if self.input_string[self.position] == '(':
            self.__next()
            val = self.__expression()
            if self.input_string[self.position] == ')':
                self.__next()
            else:
                print("Invalid Syntax at index %d.", self.position)
        elif self.input_string[self.position].isnumeric():
            val = ord(self.input_string[self.position]) - 48
            self.__next()
            while self.position < self.len and self.input_string[self.position].isnumeric():
                val = val * 10 + ord(self.input_string[self.position]) - 48;
                self.__next()
        self.__skip_space()
        return val;


    
    

