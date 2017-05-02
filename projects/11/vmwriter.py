SEGMENTS = {
        "CONST": "constant",
        "ARG": "argument",
        "LOCAL": "local",
        "VAR": "local",
        "STATIC": "static",
        "THIS": "this",
        "THAT": "that",
        "POINTER": "pointer",
        "TEMP": "temp",
        }
ARITHMETIC = {
        "ADD": "add",
        "SUB": "sub",
        "NEG": "neg",
        "EQ": "eq",
        "GT": "gt",
        "LT": "lt",
        "AND": "and",
        "OR": "or",
        "NOT": "not",
        }

class VMWriter:
    def __init__(self, filename):
        self.output = open(filename, "w")
        self.lines = list()

    def writeFile(self):
        self.output.write("\n".join(self.lines))

    def writePush(self, segment, index):
        self.lines.append("push {} {}".format(SEGMENTS[segment], index))

    def writePop(self, segment, index):
        self.lines.append("pop {} {}".format(SEGMENTS[segment], index))

    def writeArithmetic(self, command):
        self.lines.append(ARITHMETIC[command])

    def writeLabel(self, label):
        self.lines.append("label {}".format(label))

    def writeGoto(self, label):
        self.lines.append("goto {}".format(label))

    def writeIf(self, label):
        self.lines.append("if-goto {}".format(label))

    def writeCall(self, name, nArgs):
        self.lines.append("call {} {}".format(name, nArgs))

    def writeFunction(self, name, nLocals):
        self.lines.append("function {} {}".format(name, nLocals))

    def writeReturn(self):
        self.lines.append("return")

    def close(self):
        self.writeFile()
        self.output.close()

