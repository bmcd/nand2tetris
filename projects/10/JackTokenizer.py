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
        self.lines = list()

    def writeFile(self):
        self.output.write("\n".join(self.lines))

    def writeOpen(self, tag):
        self.lines.append("<{}>".format(tag))

    def writeClose(self, tag):
        self.lines.append("</{}>".format(tag))

    def writeTerminal(self, tag, value):
        self.lines.append("<{}> {} </{}>".format(tag, value, tag))

    def advance(self):
        if(self.tokenizer.hasMoreTokens()):
            self.tokenizer.advance()

    def compileClass(self):
        self.advance()
        self.writeOpen("class")
        self.compileItem() # class
        self.compileItem() # name
        self.compileItem() # {

        while (self.tokenizer.keyWord in ["STATIC", "FIELD"]):
            self.compileClassVarDec()

        while (self.tokenizer.keyWord in ["CONSTRUCTOR", "FUNCTION", "METHOD"]):
            self.compileSubroutine()

        self.compileItem() # }
        self.writeClose("class")

    def compileClassVarDec(self):
        self.writeOpen("classVarDec")
        self.compileItem() # static/field
        self.compileItem() # type
        self.compileItem() # name
        self.compileItem() # ;
        self.writeClose("classVarDec")

    def compileSubroutine(self):
        self.writeOpen("subroutineDec")
        self.compileItem() # constructor/function/method
        self.compileItem() # return type
        self.compileItem() # name
        self.compileItem() # (
        self.compileParameterList()
        self.compileItem() # )
        self.writeOpen("subroutineBody")
        self.compileItem() # {
        while(self.tokenizer.keyWord == "VAR"):
            self.compileVarDec()

        self.compileStatements()

        self.compileItem() # }
        self.writeClose("subroutineBody")
        self.writeClose("subroutineDec")

    def compileParameterList(self):
        self.writeOpen("parameterList")
        while(self.tokenizer.symbol != ")"):
            self.compileItem() # type
            self.compileItem() # name
            if(self.tokenizer.symbol == ","):
                self.compileItem() # ,

        self.writeClose("parameterList")
        

    def compileVarDec(self):
        self.writeOpen("varDec")
        self.compileItem() # var
        self.compileItem() # type
        while(self.tokenizer.symbol != ";"):
            self.compileItem() # name
            if(self.tokenizer.symbol == ","):
                self.compileItem() # ,
        self.compileItem() # ;
        self.writeClose("varDec")

    def compileStatements(self):
        self.writeOpen("statements")
        while(self.tokenizer.symbol != "}"):
            if(self.tokenizer.keyWord == "DO"):
                self.compileDo()
            elif(self.tokenizer.keyWord == "IF"):
                self.compileIf()
            elif(self.tokenizer.keyWord == "LET"):
                self.compileLet()
            elif(self.tokenizer.keyWord == "RETURN"):
                self.compileReturn()
            elif(self.tokenizer.keyWord == "WHILE"):
                self.compileWhile()
            else:
                raise Exception()
        self.writeClose("statements")

    def compileDo(self):
        self.writeOpen("doStatement")
        self.compileItem() # do
        while(self.tokenizer.symbol != "("):
            self.compileItem() # Main . method
        self.compileItem() # (
        self.compileExpressionList()
        self.compileItem() # )
        self.compileItem() # ;
        self.writeClose("doStatement")

    def compileLet(self):
        self.writeOpen("letStatement")
        self.compileItem() # let
        while(self.tokenizer.symbol != "="):
            self.compileItem() # a 
            if(self.tokenizer.symbol == "["):
                self.compileItem() # [ 
                self.compileExpression() # 0
                self.compileItem() # ] 
        self.compileItem() # =
        self.compileExpression()
        self.compileItem() # ;
        self.writeClose("letStatement")

    def compileWhile(self):
        self.writeOpen("whileStatement")
        self.compileItem() # while
        self.compileItem() # (
        self.compileExpression()
        self.compileItem() # )
        self.compileItem() # {
        self.compileStatements()
        self.compileItem() # }
        self.writeClose("whileStatement")

    def compileReturn(self):
        self.writeOpen("returnStatement")
        self.compileItem() # return
        if(self.tokenizer.symbol != ";"):
            self.compileExpression()
        self.compileItem() # ;
        self.writeClose("returnStatement")

    def compileIf(self):
        self.writeOpen("ifStatement")
        self.compileItem() # if
        self.compileItem() # (
        self.compileExpression()
        self.compileItem() # )
        self.compileItem() # {
        self.compileStatements()
        self.compileItem() # }
        if(self.tokenizer.keyWord == "ELSE"):
            self.compileItem() # else
            self.compileItem() # {
            self.compileStatements()
            self.compileItem() # }
        self.writeClose("ifStatement")

    def compileExpression(self):
        self.writeOpen("expression")
        while(self.tokenizer.symbol != ")" and self.tokenizer.symbol != "]" and self.tokenizer.symbol != ";"):
            isIdent = self.tokenizer.tokenType == "IDENTIFIER"
            if(isIdent):
                self.writeOpen("term")
            self.compileItem() # todo real expressions
            if(isIdent):
                self.writeClose("term")
        self.writeClose("expression")

    def compileItem(self):
        if(self.tokenizer.tokenType == "KEYWORD"):
            self.writeTerminal("keyword", self.tokenizer.keyWord.lower())
        elif(self.tokenizer.tokenType == "IDENTIFIER"):
            self.writeTerminal("identifier", self.tokenizer.identifier)
        elif(self.tokenizer.tokenType == "SYMBOL"):
            self.writeTerminal("symbol", self.tokenizer.symbol)
        self.advance()

    def compileTerm(self):
        pass

    def compileExpressionList(self):
        self.writeOpen("expressionList")
        while(self.tokenizer.symbol != ")"):
            self.compileExpression()
            if(self.tokenizer.symbol == ","):
                self.compileItem() # ,
        self.writeClose("expressionList")


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
        compileEngine = CompileEngine(tokenizer, "{}/{}2.xml".format(dir, p.name.split(".")[0]))
        #tokenizer.writeTokenXml()
        compileEngine.compileClass()
        compileEngine.writeFile()
