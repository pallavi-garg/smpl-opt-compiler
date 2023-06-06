from ctypes import c_int, c_short


def bsr(value, bits):
    minint = -2147483648
    if bits == 0:
        return value
    elif bits == 31:
        if value & minint:
            return 1
        else:
            return 0
    elif bits < 0 or bits > 31:
        raise ValueError('bad shift count')
    tmp = (value & 0x7FFFFFFE) // 2 ** bits
    if value & minint:
        return tmp | (0x40000000 // 2 ** (bits - 1))
    else:
        return tmp


class DLX(object):
    INPUT_ARRAY = []
    INPUT_ARRAY_COUNTER = 0

    #  processor state variables
    R = []
    PC = int()
    op = int()
    a = int()
    b = int()
    c = int()
    format = int()

    #  emulated memory
    MemSize = 10000

    #  bytes in memory (divisible by 4)
    M = [0] * (MemSize // 4)

    @staticmethod
    def load(program):
        for i, instruction in enumerate(program):
            DLX.M[i] = instruction
        DLX.M[i + 1] = -1

    @staticmethod
    def execute():
        origc = 0
        DLX.R = [0 for _ in range(32)]
        DLX.PC = 0
        DLX.R[30] = DLX.MemSize - 1

        try:
            end_yet = False
            while not end_yet:
                DLX.R[0] = 0
                DLX.disassem(DLX.M[DLX.PC])
                nextPC = DLX.PC + 1
                if DLX.format == 2:
                    origc = DLX.c
                    DLX.c = DLX.R[DLX.c]
                if DLX.op == DLX.ADD or DLX.op == DLX.ADDI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] + DLX.c
                elif DLX.op == DLX.SUB or DLX.op == DLX.SUBI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] - DLX.c
                elif DLX.op == DLX.CMP or DLX.op == DLX.CMPI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] - DLX.c
                    #  can not create overflow
                    if DLX.R[DLX.a] < 0:
                        DLX.R[DLX.a] = -1
                    elif DLX.R[DLX.a] > 0:
                        DLX.R[DLX.a] = 1
                    #  we don't have to do anything if R[a]==0
                elif DLX.op == DLX.MUL or DLX.op == DLX.MULI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] * DLX.c
                elif DLX.op == DLX.DIV or DLX.op == DLX.DIVI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] // DLX.c
                elif DLX.op == DLX.MOD or DLX.op == DLX.MODI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] % DLX.c
                elif DLX.op == DLX.OR or DLX.op == DLX.ORI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] | DLX.c
                elif DLX.op == DLX.AND or DLX.op == DLX.ANDI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] & DLX.c
                elif DLX.op == DLX.BIC or DLX.op == DLX.BICI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] & ~DLX.c
                elif DLX.op == DLX.XOR or DLX.op == DLX.XORI:
                    DLX.R[DLX.a] = DLX.R[DLX.b] ^ DLX.c
                elif DLX.op == DLX.LSH or DLX.op == DLX.LSHI:
                    if (DLX.c < -31) or (DLX.c > 31):
                        print(f"DLX.execute: Illegal value {str(DLX.c)} of operand c or register c!")
                        DLX.bug(1)
                    if DLX.c < 0:
                        DLX.R[DLX.a] = bsr(DLX.R[DLX.b], -DLX.c)
                    else:
                        DLX.R[DLX.a] = DLX.R[DLX.b] << DLX.c
                elif DLX.op == DLX.ASH or DLX.op == DLX.ASHI:
                    if (DLX.c < -31) or (DLX.c > 31):
                        print(f"DLX.execute: Illegal value {str(DLX.c)} of operand c or register c!")
                        DLX.bug(1)
                    if DLX.c < 0:
                        DLX.R[DLX.a] = DLX.R[DLX.b] >> -DLX.c
                    else:
                        DLX.R[DLX.a] = DLX.R[DLX.b] << DLX.c
                elif DLX.op == DLX.CHKI or DLX.op == DLX.CHK:
                    if DLX.R[DLX.a] < 0:
                        print(f"DLX.execute: {DLX.PC * 4}: R[{DLX.a}] == {DLX.R[DLX.a]} < 0")
                        DLX.bug(14)
                    elif DLX.R[DLX.a] >= DLX.c:
                        print(f"DLX.execute: {DLX.PC * 4}: R[{DLX.a}] == {DLX.R[DLX.a]} >= {DLX.c}")
                        DLX.bug(14)
                elif DLX.op == DLX.LDW or DLX.op == DLX.LDX:
                    #  remember: c == R[origc] because of F2 format
                    DLX.R[DLX.a] = DLX.M[(DLX.R[DLX.b] + DLX.c) // 4]
                elif DLX.op == DLX.STW or DLX.op == DLX.STX:
                    #  remember: c == R[origc] because of F2 format
                    DLX.M[(DLX.R[DLX.b] + DLX.c) // 4] = DLX.R[DLX.a]
                elif DLX.op == DLX.POP:
                    DLX.R[DLX.a] = DLX.M[DLX.R[DLX.b] // 4]
                    DLX.R[DLX.b] = DLX.R[DLX.b] + DLX.c
                elif DLX.op == DLX.PSH:
                    DLX.R[DLX.b] = DLX.R[DLX.b] + DLX.c
                    DLX.M[DLX.R[DLX.b] // 4] = DLX.R[DLX.a]
                elif DLX.op == DLX.BEQ:
                    if DLX.R[DLX.a] == 0:
                        nextPC = DLX.PC + DLX.c
                    if (nextPC < 0) or (nextPC > DLX.MemSize // 4):
                        print(f"{4 * nextPC} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(40)
                elif DLX.op == DLX.BNE:
                    if DLX.R[DLX.a] != 0:
                        nextPC = DLX.PC + DLX.c
                    if (nextPC < 0) or (nextPC > DLX.MemSize // 4):
                        print(f"{4 * nextPC} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(41)
                elif DLX.op == DLX.BLT:
                    if DLX.R[DLX.a] < 0:
                        nextPC = DLX.PC + DLX.c
                    if (nextPC < 0) or (nextPC > DLX.MemSize // 4):
                        print(f"{4 * nextPC} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(42)
                elif DLX.op == DLX.BGE:
                    if DLX.R[DLX.a] >= 0:
                        nextPC = DLX.PC + DLX.c
                    if (nextPC < 0) or (nextPC > DLX.MemSize // 4):
                        print(f"{4 * nextPC} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(43)
                elif DLX.op == DLX.BLE:
                    if DLX.R[DLX.a] <= 0:
                        nextPC = DLX.PC + DLX.c
                    if (nextPC < 0) or (nextPC > DLX.MemSize // 4):
                        print(f"{4 * nextPC} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(44)
                elif DLX.op == DLX.BGT:
                    if DLX.R[DLX.a] > 0:
                        nextPC = DLX.PC + DLX.c
                    if (nextPC < 0) or (nextPC > DLX.MemSize // 4):
                        print(f"{4 * nextPC} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(45)
                elif DLX.op == DLX.BSR:
                    DLX.R[31] = (DLX.PC + 1) * 4
                    nextPC = DLX.PC + DLX.c
                elif DLX.op == DLX.JSR:
                    DLX.R[31] = (DLX.PC + 1) * 4
                    nextPC = DLX.c // 4
                elif DLX.op == DLX.RET:
                    if origc == 0:
                        end_yet = True
                    if (DLX.c < 0) or (DLX.c > DLX.MemSize):
                        print(f"{DLX.c} is no address in memory (0..{DLX.MemSize}).")
                        DLX.bug(49)
                    nextPC = DLX.c // 4
                elif DLX.op == DLX.RDI:
                    print("?: ", end='')
                    #  for easier debug
                    if len(DLX.INPUT_ARRAY) == 0:
                        # String line = (new BufferedReader(new InputStreamReader(System.in))).readLine();
                        line = input()
                        DLX.R[DLX.a] = int(line)
                    else:
                        DLX.R[DLX.a] = DLX.INPUT_ARRAY[DLX.INPUT_ARRAY_COUNTER]
                        print(DLX.R[DLX.a], end='')
                elif DLX.op == DLX.WRD:
                    print(str(DLX.R[DLX.b]) + "  ", end='')
                elif DLX.op == DLX.WRH:
                    print("0x" + hex(DLX.R[DLX.b]) + "  ", end='')
                elif DLX.op == DLX.WRL:
                    print()
                elif DLX.op == DLX.ERR:
                    print("Program dropped off the end!")
                    DLX.bug(1)
                else:
                    print("DLX.execute: Unknown opcodes encountered!")
                    DLX.bug(1)
                DLX.PC = nextPC
        except IndexError as e:
            print(f"Not enough memory: failed at {DLX.PC * 4},   {DLX.disassemble(DLX.M[DLX.PC])}")

    #  Mnemonic-to-Opcode mapping
    mnemo = ["ADD", "SUB", "MUL", "DIV", "MOD", "CMP", "ERR", "ERR", "OR", "AND", "BIC", "XOR", "LSH", "ASH", "CHK",
             "ERR", "ADDI", "SUBI", "MULI", "DIVI", "MODI", "CMPI", "ERRI", "ERRI", "ORI", "ANDI", "BICI", "XORI",
             "LSHI", "ASHI", "CHKI", "ERR", "LDW", "LDX", "POP", "ERR", "STW", "STX", "PSH", "ERR", "BEQ", "BNE", "BLT",
             "BGE", "BLE", "BGT", "BSR", "ERR", "JSR", "RET", "RDI", "WRD", "WRH", "WRL", "ERR", "ERR", "ERR", "ERR",
             "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR",
             "ERR", "ERR", "ERR", "ERR", "ERR", "ERR", "ERR"]
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    MOD = 4
    CMP = 5
    OR = 8
    AND = 9
    BIC = 10
    XOR = 11
    LSH = 12
    ASH = 13
    CHK = 14
    ADDI = 16
    SUBI = 17
    MULI = 18
    DIVI = 19
    MODI = 20
    CMPI = 21
    ORI = 24
    ANDI = 25
    BICI = 26
    XORI = 27
    LSHI = 28
    ASHI = 29
    CHKI = 30
    LDW = 32
    LDX = 33
    POP = 34
    STW = 36
    STX = 37
    PSH = 38
    BEQ = 40
    BNE = 41
    BLT = 42
    BGE = 43
    BLE = 44
    BGT = 45
    BSR = 46
    JSR = 48
    RET = 49
    RDI = 50
    WRD = 51
    WRH = 52
    WRL = 53
    ERR = 63

    #  error opcodes which is insertered by loader
    #  after end of program code
    @staticmethod
    def disassem(instructionWord):
        DLX.op = bsr(instructionWord, 26)
        #  without sign extension
        if DLX.op == DLX.BSR or DLX.op == DLX.RDI or DLX.op == DLX.WRD or DLX.op == DLX.WRH or DLX.op == DLX.WRL \
                or DLX.op == DLX.CHKI or DLX.op == DLX.BEQ or DLX.op == DLX.BNE or DLX.op == DLX.BLT \
                or DLX.op == DLX.BGE or DLX.op == DLX.BLE or DLX.op == DLX.BGT or DLX.op == DLX.ADDI \
                or DLX.op == DLX.SUBI or DLX.op == DLX.MULI or DLX.op == DLX.DIVI or DLX.op == DLX.MODI \
                or DLX.op == DLX.CMPI or DLX.op == DLX.ORI or DLX.op == DLX.ANDI or DLX.op == DLX.BICI \
                or DLX.op == DLX.XORI or DLX.op == DLX.LSHI or DLX.op == DLX.ASHI or DLX.op == DLX.LDW \
                or DLX.op == DLX.POP or DLX.op == DLX.STW or DLX.op == DLX.PSH:
            DLX.format = 1
            DLX.a = (bsr(instructionWord, 21)) & 0x1F
            DLX.b = (bsr(instructionWord, 16)) & 0x1F
            DLX.c = c_short(instructionWord).value
            #  another dirty trick
        elif DLX.op == DLX.RET or DLX.op == DLX.CHK or DLX.op == DLX.ADD or DLX.op == DLX.SUB or DLX.op == DLX.MUL \
                or DLX.op == DLX.DIV or DLX.op == DLX.MOD or DLX.op == DLX.CMP or DLX.op == DLX.OR \
                or DLX.op == DLX.AND or DLX.op == DLX.BIC or DLX.op == DLX.XOR or DLX.op == DLX.LSH \
                or DLX.op == DLX.ASH or DLX.op == DLX.LDX or DLX.op == DLX.STX:
            DLX.format = 2
            DLX.a = (bsr(instructionWord, 21)) & 0x1F
            DLX.b = (bsr(instructionWord, 16)) & 0x1F
            DLX.c = instructionWord & 0x1F
        elif DLX.op == DLX.JSR:
            DLX.format = 3
            DLX.a = -1
            #  invalid, for error detection
            DLX.b = -1
            DLX.c = instructionWord & 0x3FFFFFF
        else:
            #  unknown instruction code
            print(f"Illegal instruction! ({DLX.PC})")

    @staticmethod
    def disassemble(instructionWord):
        DLX.disassem(instructionWord)
        line = DLX.mnemo[DLX.op]
        if DLX.op == DLX.WRL:
            return f"{line}\n"
        elif DLX.op == DLX.BSR or DLX.op == DLX.RET or DLX.op == DLX.JSR:
            return f"{line} {DLX.c}\n"
        elif DLX.op == DLX.RDI:
            return f"{line} {DLX.a}\n"
        elif DLX.op == DLX.WRD or DLX.op == DLX.WRH:
            return f"{line} {DLX.b}\n"
        elif DLX.op == DLX.CHKI or DLX.op == DLX.BEQ or DLX.op == DLX.BNE or DLX.op == DLX.BLT or DLX.op == DLX.BGE \
                or DLX.op == DLX.BLE or DLX.op == DLX.BGT or DLX.op == DLX.CHK:
            return f"{line} {DLX.a} {DLX.c}\n"
        elif DLX.op == DLX.ADDI or DLX.op == DLX.SUBI or DLX.op == DLX.MULI or DLX.op == DLX.DIVI or DLX.op == DLX.MODI \
                or DLX.op == DLX.CMPI or DLX.op == DLX.ORI or DLX.op == DLX.ANDI or DLX.op == DLX.BICI \
                or DLX.op == DLX.XORI or DLX.op == DLX.LSHI or DLX.op == DLX.ASHI or DLX.op == DLX.LDW \
                or DLX.op == DLX.POP or DLX.op == DLX.STW or DLX.op == DLX.PSH or DLX.op == DLX.ADD \
                or DLX.op == DLX.SUB or DLX.op == DLX.MUL or DLX.op == DLX.DIV or DLX.op == DLX.MOD \
                or DLX.op == DLX.CMP or DLX.op == DLX.OR or DLX.op == DLX.AND or DLX.op == DLX.BIC \
                or DLX.op == DLX.XOR or DLX.op == DLX.LSH or DLX.op == DLX.ASH or DLX.op == DLX.LDX \
                or DLX.op == DLX.STX:
            return f"{line} {DLX.a} {DLX.b} {DLX.c}\n"
        else:
            return line + "\n"

    @staticmethod
    def assemble(op, *args):
        if len(args) == 1:
            return DLX.assemble_0(op, *args)
        elif len(args) == 2:
            return DLX.assemble_1(op, *args)
        elif len(args) == 3:
            return DLX.assemble_2(op, *args)
        else:
            if op != DLX.WRL:
                print("DLX.assemble: No arguments given and the instruction is not WRL!")
                DLX.bug(1)
            return DLX.F1(op, 0, 0, 0)

    @staticmethod
    def assemble_0(op, arg1):
        if op == DLX.BSR:
            return DLX.F1(op, 0, 0, arg1)
        elif op == DLX.RDI:
            return DLX.F1(op, arg1, 0, 0)
        elif op == DLX.WRD or op == DLX.WRH:
            return DLX.F1(op, 0, arg1, 0)
        elif op == DLX.RET:
            return DLX.F2(op, 0, 0, arg1)
        elif op == DLX.JSR:
            return DLX.F3(op, arg1)
        else:
            print(f"DLX.assemble: wrong opcodes for one arg instruction {op}\t{arg1}")
            DLX.bug(1)
            return -1

    @staticmethod
    def assemble_1(op, arg1, arg2):
        if op == DLX.CHKI or op == DLX.BEQ or op == DLX.BNE or op == DLX.BLT or op == DLX.BGE or op == DLX.BLE \
                or op == DLX.BGT:
            return DLX.F1(op, arg1, 0, arg2)
        elif op == DLX.CHK:
            return DLX.F2(op, arg1, 0, arg2)
        else:
            print(f"DLX.assemble: Instruction is not valid {op}\t{arg1}\t{arg2}")
            DLX.bug(1)
            return -1

    @staticmethod
    def assemble_2(op, arg1, arg2, arg3):
        if op == DLX.ADDI or op == DLX.SUBI or op == DLX.MULI or op == DLX.DIVI or op == DLX.MODI or op == DLX.CMPI \
                or op == DLX.ORI or op == DLX.ANDI or op == DLX.BICI or op == DLX.XORI or op == DLX.LSHI \
                or op == DLX.ASHI or op == DLX.LDW or op == DLX.POP or op == DLX.STW or op == DLX.PSH:
            return DLX.F1(op, arg1, arg2, arg3)
        elif op == DLX.ADD or op == DLX.SUB or op == DLX.MUL or op == DLX.DIV or op == DLX.MOD or op == DLX.CMP \
                or op == DLX.OR or op == DLX.AND or op == DLX.BIC or op == DLX.XOR or op == DLX.LSH or op == DLX.ASH \
                or op == DLX.LDX or op == DLX.STX:
            return DLX.F2(op, arg1, arg2, arg3)
        else:
            print(f"DLX.assemble: Instruction is not valid {op}\t{arg1}\t{arg2}\t{arg3}")
            DLX.bug(1)
            return -1

    @staticmethod
    def F1(op, a, b, c):
        if c < 0:
            c = c_int(c ^ 0xFFFF0000).value
        if c_int(a & ~0x1F | b & ~0x1F | c & ~0xFFFF).value != 0:
            print("Illegal Operand(s) for F1 Format.")
            DLX.bug(1)
        return c_int(op << 26 | a << 21 | b << 16 | c).value

    @staticmethod
    def F2(op, a, b, c):
        if c_int(a & ~0x1F | b & ~0x1F | c & ~0x1F).value != 0:
            print("Illegal Operand(s) for F2 Format.")
            DLX.bug(1)
        return c_int(op << 26 | a << 21 | b << 16 | c).value

    @staticmethod
    def F3(op, c):
        if (c < 0) or (c > DLX.MemSize):
            print("Operand for F3 Format is referencing non-existent memory location.")
            DLX.bug(1)
        return c_int(op << 26 | c).value

    @staticmethod
    def bug(n):
        print(f"DLX.bug number: {n}")
        try:
            input()
        except Exception:
            pass

    @staticmethod
    def print_(opcode, arg1, arg2, arg3):
        line = DLX.mnemo[opcode]
        if opcode == DLX.WRL:
            return f"{line}\n"
        elif opcode == DLX.BSR or opcode == DLX.RET or opcode == DLX.JSR:
            return f"{line} {DLX.c}\n"
        elif opcode == DLX.RDI:
            return f"{line} {DLX.a}\n"
        elif opcode == DLX.WRD or opcode == DLX.WRH:
            return f"{line} {DLX.b}\n"
        elif opcode == DLX.CHKI or opcode == DLX.BEQ or opcode == DLX.BNE or opcode == DLX.BLT or opcode == DLX.BGE \
                or opcode == DLX.BLE or opcode == DLX.BGT or opcode == DLX.CHK:
            return f"{line} {DLX.a} {DLX.c}\n"
        elif opcode == DLX.ADDI or opcode == DLX.SUBI or opcode == DLX.MULI or opcode == DLX.DIVI \
                or opcode == DLX.MODI or opcode == DLX.CMPI or opcode == DLX.ORI or opcode == DLX.ANDI \
                or opcode == DLX.BICI or opcode == DLX.XORI or opcode == DLX.LSHI or opcode == DLX.ASHI \
                or opcode == DLX.LDW or opcode == DLX.POP or opcode == DLX.STW or opcode == DLX.PSH \
                or opcode == DLX.ADD or opcode == DLX.SUB or opcode == DLX.MUL or opcode == DLX.DIV \
                or opcode == DLX.MOD or opcode == DLX.CMP or opcode == DLX.OR or opcode == DLX.AND \
                or opcode == DLX.BIC or opcode == DLX.XOR or opcode == DLX.LSH or opcode == DLX.ASH \
                or opcode == DLX.LDX or opcode == DLX.STX:
            return f"{line} {arg1} {arg2} {arg3}\n"
        else:
            return f"{line}\n"
