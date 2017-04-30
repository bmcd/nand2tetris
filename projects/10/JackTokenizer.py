import sys
import re
from pathlib import Path

IDENTIFIER = '^(\w+)'
SYMBOL = '^(\W)'
INTEGER = '^(\d+)'
STRING = '^"(.*)"'
KEYWORDS = [ 'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return' ]
class JackTokenizer:

    def __init__(self, file):
        self.file = file.open("r")
        name = file.name.split(".")[0]
        self.token_out_filename = "{}/{}T2.xml".format(file.parent.name, name)
        self.tokens = list()
        self.input = "".join(self.file.readlines())
        self.file.close()

    def writeTokenXml(self):
        out = open(self.token_out_filename, "w")
        out.write("<tokens>\n")
        while (self.hasMoreTokens()):
            self.advance()

        for group in self.tokens:
            out.write("<{}> {} </{}>\n".format(group[0], group[1], group[0]))

        out.write("</tokens>")
        out.close()

    def hasMoreTokens(self):
        # TODO remove comments
        self.input = self.input.lstrip()
        if(len(self.input) == 0):
            return False
        if(self.input.startswith("/*")):
            end_comment = self.input.find("*/") + 2
            self.input = self.input[end_comment:]
            return self.hasMoreTokens()
        if(self.input.startswith("//")):
            end_comment = self.input.find("\n") + 1 # newline is 1?
            self.input = self.input[end_comment:]
            return self.hasMoreTokens()

        return True

    def advance(self):
        i = self.input
        self.tokenType = None
        self.keyWord = None
        self.symbol = None
        self.identifier = None
        self.intVal = None
        self.stringVal = None
        intmatch = re.match(INTEGER, i)
        if(intmatch):
            self.tokenType = "INT_CONST"
            match, capture, self.input = self.getParts(intmatch)
            self.intVal = int(capture)
            self.tokens.append(('integerConstant', capture))
            return
        stringmatch = re.match(STRING, i)
        if(stringmatch):
            self.tokenType = "STRING_CONST"
            match, capture, self.input = self.getParts(stringmatch)
            self.stringVal = capture
            self.tokens.append(('stringConstant', capture))
            return
        symbolmatch = re.match(SYMBOL, i)
        if(symbolmatch):
            self.tokenType = "SYMBOL"
            match, capture, self.input = self.getParts(symbolmatch)
            self.symbol = capture.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            self.tokens.append(('symbol', self.symbol))
            return
        identifiermatch = re.match(IDENTIFIER, i)
        if(identifiermatch):
            match, capture, self.input = self.getParts(identifiermatch)
            if(capture in KEYWORDS):
                self.tokenType = "KEYWORD"
                self.keyWord = capture.upper()
                self.tokens.append(('keyword', capture))
            else:
                self.tokenType = "IDENTIFIER"
                self.identifier = capture
                self.tokens.append(('identifier', capture))

    def getParts(self, match):
        whole = match.group(0)
        return whole, match.group(1), match.string[len(whole):]

class CompileEngine:
    def __init__(self, tokenizer, filename):
        self.tokenizer = tokenizer
        self.output = open(filename, "w")

    def compileClass():
        pass

    def compileClassVarDec():
        pass

    def compileSubroutine():
        pass

    def compileParameterList():
        pass

    def compileVarDec():
        pass

    def compileStatements():
        pass

    def compileDo():
        pass

    def compileLet():
        pass

    def compileWhile():
        pass

    def compileReturn():
        pass

    def compileIf():
        pass

    def compileExpression():
        pass

    def compileTerm():
        pass

    def compileExpressionList():
        pass


# JackAnalyzer
if (__name__ == "__main__"):
    files = list()
    input_file = Path(sys.argv[1])
    dir = "."
    if (input_file.is_dir()):
        dir = input_file.name
        for child in input_file.iterdir():
            if (child.name.endswith(".jack")):
                files.append(child)
    elif (input_file.is_file()):
        files.append(input_file)

    for p in files:
        print("Handling " + p.name)
        tokenizer = JackTokenizer(p)
        # compileEngine = CompileEngine(tokenizer, "{}/{}2.xml".format(dir, p.name))
        tokenizer.writeTokenXml()
        # compileEngine.compileClass()
