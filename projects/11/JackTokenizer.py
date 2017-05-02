import sys
import re
from pathlib import Path
from SymbolTable import SymbolTable
from vmwriter import VMWriter

IDENTIFIER = '^(\w+)'
SYMBOL = '^(\W)'
INTEGER = '^(\d+)'
STRING = '^"(.*)"'
KEYWORDS = [
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var',
    'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let',
    'do', 'if', 'else', 'while', 'return'
]
OPS = {
    '+': "ADD",
    '-': "SUB",
    '*': "Math.multiply",
    '/': "Math.divide",
    '|': "OR",
    '&': "AND",
    '~': "DUNNO",
    '<': "LT",
    '>': "GT",
    '=': "EQ"
}
UNARY_OPS = {'-': "NEG", '~': "NOT"}


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
        if (len(self.input) == 0):
            return False
        if (self.input.startswith("/*")):
            end_comment = self.input.find("*/") + 2
            self.input = self.input[end_comment:]
            return self.hasMoreTokens()
        if (self.input.startswith("//")):
            end_comment = self.input.find("\n") + 1  # newline is 1?
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
        if (intmatch):
            self.tokenType = "INT_CONST"
            match, capture, self.input = self.getParts(intmatch)
            self.intVal = int(capture)
            self.tokens.append(('integerConstant', capture))
            return
        stringmatch = re.match(STRING, i)
        if (stringmatch):
            self.tokenType = "STRING_CONST"
            match, capture, self.input = self.getParts(stringmatch)
            self.stringVal = capture
            self.tokens.append(('stringConstant', capture))
            return
        symbolmatch = re.match(SYMBOL, i)
        if (symbolmatch):
            self.tokenType = "SYMBOL"
            match, capture, self.input = self.getParts(symbolmatch)
            self.symbol = capture
            self.tokens.append(('symbol', self.symbol.replace("&", "&amp;")
                                .replace("<", "&lt;").replace(">", "&gt;")))
            return
        identifiermatch = re.match(IDENTIFIER, i)
        if (identifiermatch):
            match, capture, self.input = self.getParts(identifiermatch)
            if (capture in KEYWORDS):
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
    def __init__(self, symbolTable, tokenizer, filename):
        self.symbolTable = symbolTable
        self.tokenizer = tokenizer
        self.writer = VMWriter(filename)
        self.lines = list()
        self.label_count = 0

    def writeFile(self):
        self.writer.close()

    def writeOpen(self, tag):
        self.lines.append("<{}>".format(tag))

    def writeClose(self, tag):
        self.lines.append("</{}>".format(tag))

    def writeTerminal(self, tag, value):
        self.lines.append("<{}> {} </{}>".format(tag, value, tag))

    def advance(self):
        if (self.tokenizer.hasMoreTokens()):
            self.tokenizer.advance()

    def uniqueLabel(self, label):
        self.label_count += 1
        return label + str(self.label_count)

    def compileClass(self):
        self.advance()
        self.writeOpen("class")
        self.compileItem()  # class
        self.classname = self.tokenizer.identifier
        self.compileItem()  # name
        self.compileItem()  # {

        while (self.tokenizer.keyWord in ["STATIC", "FIELD"]):
            self.compileClassVarDec()

        while (self.tokenizer.keyWord in ["CONSTRUCTOR", "FUNCTION", "METHOD"]
               ):
            self.compileSubroutine()

        self.compileItem()  # }
        self.writeClose("class")

    def compileClassVarDec(self):
        self.writeOpen("classVarDec")
        self.compileVarDecList()
        self.writeClose("classVarDec")

    def compileVarDecList(self):
        kind = self.tokenizer.keyWord
        self.compileItem()  # static/field/var
        thetype = self.tokenizer.identifier if self.tokenizer.identifier else self.tokenizer.keyWord
        self.compileItem()  # type
        count = 0
        while (self.tokenizer.symbol != ";"):
            count += 1
            self.compileNewIdentifier(thetype, kind)  # name
            if (self.tokenizer.symbol == ","):
                self.compileItem()  # ,
        self.compileItem()  # ;
        return count

    def compileSubroutine(self):
        self.symbolTable.startSubroutine()
        self.writeOpen("subroutineDec")
        funtype = self.tokenizer.keyWord
        self.compileItem()  # constructor/function/method
        self.compileItem()  # return type
        label = "{}.{}".format(self.classname, self.tokenizer.identifier)
        self.compileItem()  # name
        self.compileItem()  # (
        self.compileParameterList()
        nArgs = self.symbolTable.varCount("ARG")
        self.compileItem()  # )
        self.writeOpen("subroutineBody")
        self.compileItem()  # {
        while (self.tokenizer.keyWord == "VAR"):
            self.compileVarDec()

        nLocals = self.symbolTable.varCount("VAR")
        self.writer.writeFunction(label, nLocals)
        if (funtype == "METHOD"):
            nArgs += 1
            self.writer.writePush("ARG", 0)
            self.writer.writePop("POINTER", 0)
        elif (funtype == "CONSTRUCTOR"):
            self.writer.writePush("CONST", self.symbolTable.varCount("FIELD"))
            self.writer.writeCall("Memory.alloc", 1)
            self.writer.writePop("POINTER", 0)
        self.compileStatements()
        self.compileItem()  # }
        self.writeClose("subroutineBody")
        self.writeClose("subroutineDec")

    def compileParameterList(self):
        self.writeOpen("parameterList")
        kind = "ARG"
        while (self.tokenizer.symbol != ")"):
            thetype = self.tokenizer.identifier if self.tokenizer.identifier else self.tokenizer.keyWord
            self.compileItem()  # type
            self.compileNewIdentifier(thetype, kind)  # name
            if (self.tokenizer.symbol == ","):
                self.compileItem()  # ,

        self.writeClose("parameterList")

    def compileVarDec(self):
        self.writeOpen("varDec")
        count = self.compileVarDecList()
        self.writeClose("varDec")
        return count

    def compileStatements(self):
        self.writeOpen("statements")
        while (self.tokenizer.symbol != "}"):
            if (self.tokenizer.keyWord == "DO"):
                self.compileDo()
            elif (self.tokenizer.keyWord == "IF"):
                self.compileIf()
            elif (self.tokenizer.keyWord == "LET"):
                self.compileLet()
            elif (self.tokenizer.keyWord == "RETURN"):
                self.compileReturn()
            elif (self.tokenizer.keyWord == "WHILE"):
                self.compileWhile()
            else:
                raise Exception()
        self.writeClose("statements")

    def compileDo(self):
        self.writeOpen("doStatement")
        self.compileItem()  # do
        label = ""
        argCount = 0
        while (self.tokenizer.symbol != "("):
            label += self.compileItem()[0]  # Main . method
        parts = label.split(".")
        objsym = self.symbolTable.getSymbol(parts[0])
        if (objsym is not None):
            # is a method, push obj as first param
            self.writer.writePush(objsym.kind, objsym.index)
            label = label.replace(objsym.name, objsym.thetype)
            argCount += 1
        elif (len(parts) == 1):
            label = self.classname + "." + label
            self.writer.writePush("POINTER", 0)
            argCount += 1

        self.compileItem()  # (
        argCount += self.compileExpressionList()
        self.compileItem()  # )
        self.compileItem()  # ;
        self.writer.writeCall(label, argCount)
        self.writer.writePop("TEMP", 0)
        self.writeClose("doStatement")

    def compileLet(self):
        self.writeOpen("letStatement")
        self.compileItem()  # let
        is_array = False
        if (self.tokenizer.symbol != "="):
            value, sym = self.compileItem()  # a
            if (self.tokenizer.symbol == "["):
                is_array = True
                self.writer.writePush(sym.kind, sym.index)
                self.compileItem()  # [
                self.compileExpression()  # 0
                self.writer.writeArithmetic("ADD")
                self.writer.writePop("POINTER", 1)
                self.compileItem()  # ]
        self.compileItem()  # =
        self.compileExpression()
        self.compileItem()  # ;
        if (is_array):
            self.writer.writePop("THAT", 0)
        else:
            self.writer.writePop(sym.kind, sym.index)
        self.writeClose("letStatement")

    def compileWhile(self):
        self.writeOpen("whileStatement")
        start = self.uniqueLabel("LOOPSTART")
        end = self.uniqueLabel("LOOPEND")
        self.writer.writeLabel(start)
        self.compileItem()  # while
        self.compileItem()  # (
        self.compileExpression()
        self.writer.writeArithmetic("NOT")
        self.writer.writeIf(end)
        self.compileItem()  # )
        self.compileItem()  # {
        self.compileStatements()
        self.compileItem()  # }
        self.writer.writeGoto(start)
        self.writer.writeLabel(end)
        self.writeClose("whileStatement")

    def compileReturn(self):
        self.writeOpen("returnStatement")
        self.compileItem()  # return
        if (self.tokenizer.symbol != ";"):
            self.compileExpression()
        self.compileItem()  # ;
        self.writer.writeReturn()
        self.writeClose("returnStatement")

    def compileIf(self):
        self.writeOpen("ifStatement")
        self.compileItem()  # if
        self.compileItem()  # (
        self.compileExpression()
        iftrue = self.uniqueLabel("IFTRUE")
        iffalse = self.uniqueLabel("IFFALSE")
        ifend = self.uniqueLabel("IFEND")
        self.writer.writeIf(iftrue)
        self.writer.writeGoto(iffalse)
        self.writer.writeLabel(iftrue)
        self.compileItem()  # )
        self.compileItem()  # {
        self.compileStatements()
        self.compileItem()  # }
        self.writer.writeGoto(ifend)
        self.writer.writeLabel(iffalse)
        if (self.tokenizer.keyWord == "ELSE"):
            self.compileItem()  # else
            self.compileItem()  # {
            self.compileStatements()
            self.compileItem()  # }
        self.writer.writeLabel(ifend)
        self.writeClose("ifStatement")

    def compileExpression(self):
        self.writeOpen("expression")
        self.compileTerm()
        while (self.tokenizer.symbol in OPS.keys()):
            op, _ = self.compileItem()  # & | + etc
            self.compileTerm()
            if (op in ["*", "/"]):
                self.writer.writeCall(OPS[op], 2)
            else:
                self.writer.writeArithmetic(OPS[op])
        self.writeClose("expression")

    def compileNewIdentifier(self, thetype, kind):
        sym = self.symbolTable.define(self.tokenizer.identifier, thetype, kind)
        self.writeTerminal("identifier", "{} DEFINE {} {} {}".format(
            sym.kind, sym.thetype, sym.name, sym.index))
        self.advance()

    def compileItem(self):
        sym = None
        ret = None
        if (self.tokenizer.tokenType == "KEYWORD"):
            ret = self.tokenizer.keyWord
            self.writeTerminal("keyword", self.tokenizer.keyWord.lower())
        elif (self.tokenizer.tokenType == "IDENTIFIER"):
            name = self.tokenizer.identifier
            sym = self.symbolTable.getSymbol(name)
            if (sym):
                ret = name
                self.writeTerminal("identifier", "{} EXISTING {} {} {}".format(
                    sym.kind, sym.thetype, sym.name, sym.index))
            else:
                ret = name
                # class or subroutine
                self.writeTerminal("identifier", "CLASS/SUBROUTINE " + name)
        elif (self.tokenizer.tokenType == "SYMBOL"):
            ret = self.tokenizer.symbol
            self.writeTerminal("symbol",
                               self.tokenizer.symbol.replace("&", "&amp;")
                               .replace("<", "&lt;").replace(">", "&gt;"))
        elif (self.tokenizer.tokenType == "INT_CONST"):
            ret = self.tokenizer.intVal
            self.writeTerminal("integerConstant", self.tokenizer.intVal)
        elif (self.tokenizer.tokenType == "STRING_CONST"):
            ret = self.tokenizer.stringVal
            self.writeTerminal("stringConstant", self.tokenizer.stringVal)
        self.advance()
        return ret, sym

    def compileTerm(self):
        self.writeOpen("term")
        if (self.tokenizer.symbol == "("):
            self.compileItem()  # (
            self.compileExpression()
            self.compileItem()  # )
        elif (self.tokenizer.symbol in UNARY_OPS.keys()):
            unary_op, _ = self.compileItem()  # - ~
            self.compileTerm()
            self.writer.writeArithmetic(UNARY_OPS[unary_op])
        else:
            tokenType = self.tokenizer.tokenType
            value, sym = self.compileItem()  # any value
            if (self.tokenizer.symbol == "."):
                value += self.compileItem()[0]  # .
                value += self.compileItem()[0]  # subroutineName
            if (self.tokenizer.symbol == "["):
                self.writer.writePush(sym.kind, sym.index)
                self.compileItem()  # [
                self.compileExpression()
                self.writer.writeArithmetic("ADD")
                self.writer.writePop("POINTER", 1)
                self.writer.writePush("THAT", 0)
                self.compileItem()  # ]
            elif (self.tokenizer.symbol == "("):
                parts = value.split(".")
                sym = self.symbolTable.getSymbol(parts[0])
                nArgs = 0
                if (sym is not None):
                    # is a method, push obj as first param
                    self.writer.writePush(sym.kind, sym.index)
                    value = value.replace(sym.name, sym.thetype)
                    nArgs += 1
                elif (len(parts) == 1):
                    value = self.classname + "." + value
                    self.writer.writePush("POINTER", 0)
                    nArgs += 1

                self.compileItem()  # (
                nArgs += self.compileExpressionList()
                self.writer.writeCall(value, nArgs)
                self.compileItem()  # )
            elif (tokenType == "INT_CONST"):
                self.writer.writePush("CONST", value)
            elif (tokenType == "STRING_CONST"):
                self.writer.writePush("CONST", len(value))
                self.writer.writeCall("String.new", 1)
                self.writer.writePop("TEMP", 1)
                for i in range(len(value)):
                    self.writer.writePush("TEMP", 1)
                    self.writer.writePush("CONST", ord(value[i]))
                    self.writer.writeCall("String.appendChar", 2)
                    self.writer.writePop("TEMP", 0)
                self.writer.writePush("TEMP", 1)

            elif (tokenType == "KEYWORD"):
                if (value == "TRUE"):
                    self.writer.writePush("CONST", 1)
                    self.writer.writeArithmetic("NEG")
                elif (value == "THIS"):
                    self.writer.writePush("POINTER", 0)
                elif (value in ["FALSE", "NULL"]):
                    self.writer.writePush("CONST", 0)
                else:
                    print(value)
                    raise Exception()
            else:
                self.writer.writePush(sym.kind, sym.index)

        self.writeClose("term")

    def compileExpressionList(self):
        self.writeOpen("expressionList")
        count = 0
        while (self.tokenizer.symbol != ")"):
            count += 1
            self.compileExpression()
            if (self.tokenizer.symbol == ","):
                self.compileItem()  # ,
        self.writeClose("expressionList")
        return count


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
        symbolTable = SymbolTable()
        compileEngine = CompileEngine(symbolTable, tokenizer,
                                      "{}/{}.vm".format(dir,
                                                        p.name.split(".")[0]))
        # tokenizer.writeTokenXml()
        compileEngine.compileClass()
        compileEngine.writeFile()
