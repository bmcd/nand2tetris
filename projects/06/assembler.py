import sys


class Assembler:
    def __init__(self, filename):
        self.filename = filename
        self.symbols = SymbolTable()
        self.parser = Parser(filename, self.symbols)
        self.code = Code()
        self.output = ""
        self.count = 0

    def assemble(self):
        while (self.parser.hasMoreCommands()):
            self.parser.advance()
            if (self.parser.commandType() == "A_COMMAND" or
                    self.parser.commandType() == "C_COMMAND"):
                self.count += 1
            elif (self.parser.commandType() == "L_COMMAND"):
                self.symbols.addEntry(self.parser.rawSymbol(), self.count)

        print(self.symbols.symbols)

        self.parser.reset()

        while (self.parser.hasMoreCommands()):
            self.parser.advance()
            if (self.parser.commandType() == "A_COMMAND"):
                self.count += 1
                self.output += "0"
                binary = "{0:015b}".format(self.parser.symbol())
                self.output += binary
                self.output += "\n"
            elif (self.parser.commandType() == "L_COMMAND"):
                pass
            else:
                self.count += 1
                self.output += "111"
                comp = self.parser.comp()
                dest = self.parser.dest()
                jump = self.parser.jump()
                self.output += self.code.comp(comp)
                self.output += self.code.dest(dest)
                self.output += self.code.jump(jump)
                self.output += "\n"
        out = open(self.filename[0:self.filename.find(".")] + ".hack", "w")
        out.write(self.output)


class Parser:
    def __init__(self, filename, symbols):
        file = open(filename, "r")
        self.lines = file.readlines()
        self.symbols = symbols
        self.reset()

    def reset(self):
        self.current_index = -1

    def hasMoreCommands(self):
        self.current_index += 1
        if (self.current_index >= len(self.lines)):
            return False

        line = self.lines[self.current_index].strip()
        if (line == "" or line.startswith("//")):
            return self.hasMoreCommands()

        return True

    def advance(self):
        l = self.lines[self.current_index].strip()
        l = self.stripComments(l)
        print(l)
        if (l.startswith("(")):
            self.command = "L_COMMAND"
            self.sym = l[1:l.find(")")]
        elif (l.startswith("@")):
            self.command = "A_COMMAND"
            self.sym = l[1:]
        else:
            self.command = "C_COMMAND"
            if (";" in l):
                self.destination = ""
                self.computation = l[0]
                self.jump_value = l[2:]
            else:
                parts = l.split("=")
                self.destination = parts[0]
                self.computation = parts[1]
                self.jump_value = None

    def commandType(self):
        return self.command

    def rawSymbol(self):
        return self.sym

    def symbol(self):
        if (self.sym.isdigit()):
            return int(self.sym)

        if (not self.symbols.contains(self.sym)):
            self.symbols.addEntry(self.sym, self.symbols.getNextAddress())

        return self.symbols.getAddress(self.sym)

    def dest(self):
        return self.destination

    def comp(self):
        return self.computation

    def jump(self):
        return self.jump_value

    def stripComments(self, l):
        comment_start = l.find("//")
        if (comment_start != -1):
            l = l[:comment_start]
        return l


class Code:
    def dest(self, input):
        output = ""
        output += "1" if "A" in input else "0"
        output += "1" if "D" in input else "0"
        output += "1" if "M" in input else "0"
        return output

    def comp(self, input):
        a = "1" if "M" in input else "0"
        c = input.replace("M", "A").strip()
        if (c == "0"):
            return a + "101010"
        if (c == "1"):
            return a + "111111"
        if (c == "-1"):
            return a + "111010"
        if (c == "D"):
            return a + "001100"
        if (c == "A"):
            return a + "110000"
        if (c == "!D"):
            return a + "001101"
        if (c == "!A"):
            return a + "110001"
        if (c == "-D"):
            return a + "001111"
        if (c == "-A"):
            return a + "110011"
        if (c == "D+1"):
            return a + "011111"
        if (c == "A+1"):
            return a + "110111"
        if (c == "D-1"):
            return a + "001110"
        if (c == "A-1"):
            return a + "110010"
        if (c == "D+A"):
            return a + "000010"
        if (c == "D-A"):
            return a + "010011"
        if (c == "A-D"):
            return a + "000111"
        if (c == "D&A"):
            return a + "000000"
        if (c == "D|A"):
            return a + "010101"
        print("error: " + c)

    def jump(self, input):
        if (input is None):
            return "000"
        input = input.strip()
        if (input == "JGT"):
            return "001"
        if (input == "JEQ"):
            return "010"
        if (input == "JGE"):
            return "011"
        if (input == "JLT"):
            return "100"
        if (input == "JNE"):
            return "101"
        if (input == "JLE"):
            return "110"
        if (input == "JMP"):
            return "111"


class SymbolTable:
    def __init__(self):
        self.symbols = dict()
        self.nextAddress = 16
        for x in range(0, 16):
            self.addEntry("R" + str(x), x)
        self.addEntry("SP", 0)
        self.addEntry("LCL", 1)
        self.addEntry("ARG", 2)
        self.addEntry("THIS", 3)
        self.addEntry("THAT", 4)
        self.addEntry("SCREEN", 16384)
        self.addEntry("KBD", 24576)

    def addEntry(self, symbol, address):
        self.symbols[symbol] = address

    def contains(self, symbol):
        return symbol in self.symbols

    def getAddress(self, symbol):
        return self.symbols[symbol]

    def getNextAddress(self):
        last = self.nextAddress
        self.nextAddress += 1
        return last


if (__name__ == "__main__"):
    assembler = Assembler(sys.argv[1])
    assembler.assemble()
