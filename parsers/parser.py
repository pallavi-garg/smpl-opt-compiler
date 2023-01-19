"""
Parser for grammar defined in ../grammar.txt

"""

class Parser:

    # constructor initialization
    def __init__(self, input_tring):
        self.input_tring = input_tring.strip()
        self.position = 0
        self.len = len(self.input_tring)
    
    # entry point for this parser
    def computation(self):
        results = []
        val = self.__expression()
        if self.position < self.len and self.input_tring[self.position] == '.':
            results.append(val)
        
        while self.position < self.len and self.input_tring[self.position] == '.':
            self.__next()
            if self.position < self.len:
                val = self.__expression()
                if self.position < self.len and self.input_tring[self.position] == '.':
                    results.append(val)
                else:
                    break
        return results

    # advance the position to __next character
    def __next(self):
        self.position += 1

    # advances to __next position is current position is space
    def __skip_space(self):
        while self.position < self.len and self.input_tring[self.position].isspace():
            self.__next()

    # calculates expression
    def __expression(self):
        val = self.__term();
        while self.position < self.len and (self.input_tring[self.position] == '+' or self.input_tring[self.position] == '-'):
            if self.input_tring[self.position] == '+':
                self.__next();
                val += self.__term();
            elif self.input_tring[self.position] == '-':
                self.__next();
                val -= self.__term();
        return val

    # calculates term
    def __term(self):
        val = self.__factor()
        while self.position < self.len and (self.input_tring[self.position] == '*' or self.input_tring[self.position] == '/'):
            if self.input_tring[self.position] == '*':
                self.__next()
                val *= self.__factor();
            elif self.input_tring[self.position] == '/':
                self.__next()
                val = int (val/self.__factor())
        return val

    def __factor(self):
        val = 0
        self.__skip_space()
        if self.input_tring[self.position] == '(':
            self.__next()
            val = self.__expression()
            if self.input_tring[self.position] == ')':
                self.__next()
            else:
                print("Invalid Syntax at index %d.", self.position)
        elif self.input_tring[self.position].isnumeric():
            val = ord(self.input_tring[self.position]) - 48
            self.__next()
            while self.position < self.len and self.input_tring[self.position].isnumeric():
                val = val * 10 + ord(self.input_tring[self.position]) - 48;
                self.__next()
        self.__skip_space()
        return val;


    
    

