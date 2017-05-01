import sys
from pathlib import Path


class CodeWriter:
    def __init__(self, filename):
        self.output = open(filename, "w")
        self.label_count = 0
        self.writeInit()
        self.function_name_stack = ["null"]

    def setFileName(self, filename):
        self.current_file = filename

    def getCurrentFilePrefix(self):
        return self.current_file.split(".")[0]

    def writeInit(self):
        print("Writing init TODO")
        lines = list()
        lines.append("@256")
        lines.append("D=A")
        lines.append("@SP")
        lines.append("M=D")
        self.writeToOutput(lines)
        self.writeCall("Sys.init", "0")

    def writeLabel(self, label, shouldPrefix=False):
        print("Writing label: " + label)
        lines = list()
        if(shouldPrefix):
            label = "{}${}".format(self.function_name_stack[-1], label)
        lines.append("(" + label + ")")
        self.writeToOutput(lines)

    def writeGoto(self, label, shouldPrefix=False):
        print("Writing goto: " + label)
        lines = list()
        if(shouldPrefix):
            label = "{}${}".format(self.function_name_stack[-1], label)
        lines.append("@" + label)
        lines.append("0;JMP")
        self.writeToOutput(lines)

    def writeIf(self, label, shouldPrefix=False):
        print("Writing if: " + label)
        lines = list()
        if(shouldPrefix):
            label = "{}${}".format(self.function_name_stack[-1], label)
        self.oneArg(lines)
        lines.append("D=M")
        lines.append("@" + label)
        lines.append("D;JNE")
        self.writeToOutput(lines)

    def writeCall(self, functionName, numArgs):
        print("Writing call: " + functionName + " " + numArgs)
        lines = list()
        return_label = self.uniqueLabel("RETURN")
        lines.append("@{}".format(return_label))
        lines.append("D=A")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")
        self.advanceStack(lines)
        self.pushFrom(lines, "LCL", 0, True)
        self.advanceStack(lines)
        self.pushFrom(lines, "ARG", 0, True)
        self.advanceStack(lines)
        self.pushFrom(lines, "THIS", 0, True)
        self.advanceStack(lines)
        self.pushFrom(lines, "THAT", 0, True)
        self.advanceStack(lines)
        lines.append("@SP")
        lines.append("D=M")
        lines.append("@{}".format(numArgs))
        lines.append("D=D-A")
        lines.append("@{}".format(5))
        lines.append("D=D-A")
        lines.append("@ARG")
        lines.append("M=D")
        lines.append("@SP")
        lines.append("D=M")
        lines.append("@LCL")
        lines.append("M=D")
        self.writeToOutput(lines)
        self.writeGoto(functionName)
        self.writeLabel(return_label)

    def writeReturn(self):
        print("Writing return")
        lines = list()
        lines.append("@LCL")
        lines.append("D=M")
        lines.append("@FRAME")
        lines.append("M=D")
        lines.append("@5")
        lines.append("A=D-A")
        lines.append("D=M")
        lines.append("@RET")
        lines.append("M=D")
        self.popTo(lines, "ARG", 0)
        lines.append("@ARG")
        lines.append("D=M+1")
        lines.append("@SP")
        lines.append("M=D")

        lines.append("@FRAME")
        lines.append("D=M")
        lines.append("@1")
        lines.append("A=D-A")
        lines.append("D=M")
        lines.append("@THAT")
        lines.append("M=D")

        lines.append("@FRAME")
        lines.append("D=M")
        lines.append("@2")
        lines.append("A=D-A")
        lines.append("D=M")
        lines.append("@THIS")
        lines.append("M=D")

        lines.append("@FRAME")
        lines.append("D=M")
        lines.append("@3")
        lines.append("A=D-A")
        lines.append("D=M")
        lines.append("@ARG")
        lines.append("M=D")

        lines.append("@FRAME")
        lines.append("D=M")
        lines.append("@4")
        lines.append("A=D-A")
        lines.append("D=M")
        lines.append("@LCL")
        lines.append("M=D")

        lines.append("@RET")
        lines.append("A=M")
        lines.append("0;JMP")

        self.writeToOutput(lines)

    def writeFunction(self, functionName, numLocals):
        print("Writing function: " + functionName + " " + numLocals)
        self.writeLabel(functionName)
        self.function_name_stack.append(functionName)
        for i in range(int(numLocals)):
            self.writePushPop("C_PUSH", "constant", "0")

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

        self.writeToOutput(lines)

    def writeToOutput(self, lines):
        out = "\n".join(lines) + "\n"
        # print(out)
        self.output.write(out)

    def advanceStack(self, lines):
        lines.append("@SP")
        lines.append("M=M+1")

    def uniqueLabel(self, label):
        suffix = self.label_count
        self.label_count += 1
        return label + str(suffix)

    def writeComp(self, lines, jump):
        truelabel = self.uniqueLabel("TRUELABEL")
        finishlabel = self.uniqueLabel("FINISHLABEL")
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
                self.pushFrom(lines, "static", index, True)
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
                self.popTo(lines, "static", index, True)

        self.writeToOutput(lines)

    def pushFrom(self, lines, pointer, index, isAddress=False):
        if(pointer == "static"):
            pointer = "{}.{}".format(self.getCurrentFilePrefix(), index)
            index = 0

        lines.append("@{}".format(pointer))
        if(isAddress):
            lines.append("D=A")
        else:
            lines.append("D=M")
        lines.append("@{}".format(index))
        lines.append("A=D+A")
        lines.append("D=M")
        lines.append("@SP")
        lines.append("A=M")
        lines.append("M=D")

    def popTo(self, lines, pointer, index, isAddress=False):
        if(pointer == "static"):
            pointer = "{}.{}".format(self.getCurrentFilePrefix(), index)
            index = 0

        lines.append("@{}".format(pointer))
        if(isAddress):
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
        elif (cmd == "label"):
            self.command = "C_LABEL"
            self.arg1 = parts[1]
        elif (cmd == "goto"):
            self.command = "C_GOTO"
            self.arg1 = parts[1]
        elif (cmd == "if-goto"):
            self.command = "C_IF"
            self.arg1 = parts[1]
        elif (cmd == "function"):
            self.command = "C_FUNCTION"
            self.arg1 = parts[1]
            self.arg2 = parts[2]
        elif (cmd == "call"):
            self.command = "C_CALL"
            self.arg1 = parts[1]
            self.arg2 = parts[2]
        elif (cmd == "return"):
            self.command = "C_RETURN"
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
            elif (cmd == "C_LABEL"):
                codewriter.writeLabel(parser.arg1, True)
            elif (cmd == "C_GOTO"):
                codewriter.writeGoto(parser.arg1, True)
            elif (cmd == "C_IF"):
                codewriter.writeIf(parser.arg1, True)
            elif (cmd == "C_CALL"):
                codewriter.writeCall(parser.arg1, parser.arg2)
            elif (cmd == "C_FUNCTION"):
                codewriter.writeFunction(parser.arg1, parser.arg2)
            elif (cmd == "C_RETURN"):
                codewriter.writeReturn()
        parser.close()
    codewriter.close()
