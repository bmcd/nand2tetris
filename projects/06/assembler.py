import sys


class Assembler:
    def __init__(self, filename):
        self.filename = filename
        self.parser = Parser(filename)
        self.code = Code()
        self.symbols = SymbolTable()
        self.output = ""

    def assemble(self):
        while (self.parser.hasMoreCommands()):
            self.parser.advance()
            if (self.parser.commandType() == "A_COMMAND"):
                self.output += "0"
                binary = "{0:015b}".format(int(self.parser.symbol()))
                self.output += binary
                self.output += "\n"
            elif (self.parser.commandType() == "L_COMMAND"):
                pass
            else:
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
    def __init__(self, filename):
        file = open(filename, "r")
        self.lines = file.readlines()
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

    def symbol(self):
        return self.sym

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
        c = input.replace("M", "A")
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

    def jump(self, input):
        if (input is None):
            return "000"
        elif (input == "JGT"):
            return "001"
        elif (input == "JEQ"):
            return "010"
        elif (input == "JGE"):
            return "011"
        elif (input == "JLT"):
            return "100"
        elif (input == "JNE"):
            return "101"
        elif (input == "JLE"):
            return "110"
        elif (input == "JMP"):
            return "111"


class SymbolTable:
    def __init__(self):
        self.symbols = dict()

    def addEntry(self, symbol, address):
        self.symbols[symbol] = address

    def contains(self, symbol):
        return symbol in self.symbols

    def getAddress(self, symbol):
        return self.symbols[symbol]


if (__name__ == "__main__"):
    assembler = Assembler(sys.argv[1])
    assembler.assemble()
