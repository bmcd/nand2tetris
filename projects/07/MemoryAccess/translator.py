import sys
from pathlib import Path


class CodeWriter:
    def __init__(self, filename):
        self.output = open(filename, "w")
        self.label_count = 0

    def setFileName(self, filename):
        self.current_file = filename

    def writeArithmetic(self, command):
        print("Writing arthmetic: " + command)
        lines = list()
        if (command == "add"):
            self.twoArgs(lines)
            lines.append("M=D+M")
            self.advanceStack(lines)
        elif (command == "sub"):
            self.twoArgs(lines)
            lines.append("M=M-D")
            self.advanceStack(lines)
        elif (command == "and"):
            self.twoArgs(lines)
            lines.append("M=M&D")
            self.advanceStack(lines)
        elif (command == "or"):
            self.twoArgs(lines)
            lines.append("M=M|D")
            self.advanceStack(lines)
        elif (command == "not"):
            self.oneArg(lines)
            lines.append("M=!M")
            self.advanceStack(lines)
        elif (command == "neg"):
            self.oneArg(lines)
            lines.append("M=-M")
            self.advanceStack(lines)
        elif (command == "eq"):
            self.twoArgs(lines)
            self.writeComp(lines, "JEQ")
            self.advanceStack(lines)
        elif (command == "lt"):
            self.twoArgs(lines)
            self.writeComp(lines, "JLT")
            self.advanceStack(lines)
        elif (command == "gt"):
            self.twoArgs(lines)
            self.writeComp(lines, "JGT")
            self.advanceStack(lines)

        self.output.write("\n".join(lines) + "\n")

    def advanceStack(self, lines):
        lines.append("@SP")
        lines.append("M=M+1")

    def writeComp(self, lines, jump):
        truelabel = "TRUELABEL" + str(self.label_count)
        finishlabel = "FINISHLABEL" + str(self.label_count)
        self.label_count += 1
        lines.append("@SP")
        lines.append("A=M")
        lines.append("D=M-D")
        lines.append("@" + truelabel)
        lines.append("D;" + jump)
        lines.append("@0")
        lines.append("D=A")
        lines.append("@" + finishlabel)
        lines.append("0;JMP")
        lines.append("(" + truelabel + ")")
        lines.append("A=-1")
        lines.append("D=A")
        lines.append("(" + finishlabel + ")")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")

    def oneArg(self, lines):
        lines.append("@SP")
        lines.append("M=M-1")
        lines.append("A=M")

    def twoArgs(self, lines):
        lines.append("@SP")
        lines.append("M=M-1")
        lines.append("A=M")
        lines.append("D=M")
        lines.append("@SP")
        lines.append("M=M-1")
        lines.append("A=M")

    def writePushPop(self, command, segment, index):
        print("Writing push/pop: " + command + " " + segment + " " + index)
        lines = list()
        if (command == "C_PUSH"):
            if (segment == "constant"):
                lines.append("@{}".format(index))
                lines.append("D=A")
                lines.append("@SP")
                lines.append("A=M")
                lines.append("M=D")
                self.advanceStack(lines)
            elif (segment == "local"):
                self.pushFrom(lines, "LCL", index)
                self.advanceStack(lines)
            elif (segment == "argument"):
                self.pushFrom(lines, "ARG", index)
                self.advanceStack(lines)
            elif (segment == "this"):
                self.pushFrom(lines, "THIS", index)
                self.advanceStack(lines)
            elif (segment == "that"):
                self.pushFrom(lines, "THAT", index)
                self.advanceStack(lines)
            elif (segment == "pointer"):
                self.pushFrom(lines, "3", index, True)
                self.advanceStack(lines)
            elif (segment == "temp"):
                self.pushFrom(lines, "5", index, True)
                self.advanceStack(lines)
            elif (segment == "static"):
                self.pushFrom(lines, "16", index, True)
                self.advanceStack(lines)

        elif (command == "C_POP"):
            if (segment == "local"):
                self.popTo(lines, "LCL", index)
            elif (segment == "argument"):
                self.popTo(lines, "ARG", index)
            elif (segment == "this"):
                self.popTo(lines, "THIS", index)
            elif (segment == "that"):
                self.popTo(lines, "THAT", index)
            elif (segment == "pointer"):
                self.popTo(lines, "3", index, True)
            elif (segment == "temp"):
                self.popTo(lines, "5", index, True)
            elif (segment == "static"):
                self.popTo(lines, "16", index, True)

        self.output.write("\n".join(lines) + "\n")

    def pushFrom(self, lines, pointer, index, isstatic=False):
        lines.append("@{}".format(pointer))
        if(isstatic):
            lines.append("D=A")
        else:
            lines.append("D=M")
        lines.append("@{}".format(index))
        lines.append("A=D+A")
        lines.append("D=M")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")

    def popTo(self, lines, pointer, index, isstatic=False):
        lines.append("@{}".format(pointer))
        if(isstatic):
            lines.append("D=A")
        else:
            lines.append("D=M")
        lines.append("@{}".format(index))
        lines.append("A=D+A")
        lines.append("D=A")
        lines.append("@R13")
        lines.append("M=D")
        self.oneArg(lines)
        lines.append("D=M")
        lines.append("@R13")
        lines.append("A=M")
        lines.append("M=D")

    def close(self):
        self.output.close()


class Parser:
    def __init__(self, file):
        self.file = file.open("r")
        self.lines = self.file.readlines()
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
        parts = l.split(" ")
        cmd = parts[0]
        if (cmd == "push"):
            self.command = "C_PUSH"
            self.arg1 = parts[1]
            self.arg2 = parts[2]
        elif (cmd == "pop"):
            self.command = "C_POP"
            self.arg1 = parts[1]
            self.arg2 = parts[2]
        # self.command = "C_LABEL"
        # self.command = "C_GOTO"
        # self.command = "C_IF"
        # self.command = "C_FUNCTION"
        # self.command = "C_CALL"
        else:
            self.command = "C_ARITHMETIC"
            self.arg1 = cmd

    def stripComments(self, l):
        comment_start = l.find("//")
        if (comment_start != -1):
            l = l[:comment_start]
        return l

    def close(self):
        self.file.close()


if (__name__ == "__main__"):
    files = list()
    input_file = Path(sys.argv[1])
    if (input_file.is_dir()):
        for child in input_file.iterdir():
            if (child.name.endswith(".vm")):
                files.append(child)
        codewriter = CodeWriter(
            "{}/{}.asm".format(input_file.name, input_file.name))
    elif (input_file.is_file()):
        files.append(input_file)
        codewriter = CodeWriter("{}.asm"
                                .format(input_file.name.replace(".vm", "")))

    for p in files:
        print("Handling " + p.name)
        parser = Parser(p)
        codewriter.setFileName(p.name)
        while (parser.hasMoreCommands()):
            parser.advance()
            cmd = parser.command
            if (cmd == "C_PUSH" or cmd == "C_POP"):
                codewriter.writePushPop(cmd, parser.arg1, parser.arg2)
            elif (cmd == "C_ARITHMETIC"):
                codewriter.writeArithmetic(parser.arg1)
        parser.close()
    codewriter.close()
