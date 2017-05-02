class SymbolTable:
    def __init__(self):
        self.classscope = dict()
        self.classscope['STATIC'] = 0
        self.classscope['FIELD'] = 0
        self.startSubroutine()

    def startSubroutine(self):
        self.subscope = dict()
        self.subscope['ARG'] = 0
        self.subscope['VAR'] = 0

    def define(self, name, thetype, kind):
        table, index = self.getTableAndIndex(kind)
        table[name] = Symbol(name, thetype, kind, index)
        table[kind] += 1
        return table[name]

    def getTableAndIndex(self, kind):
        if(kind in ['STATIC', 'FIELD']):
            table = self.classscope
        else:
            table = self.subscope
        count = table[kind]
        return table, count

    def varCount(self, kind):
        _, count = self.getTableAndIndex(kind)
        return count

    def getSymbol(self, name):
        for table in [self.subscope, self.classscope]:
            if (name in table):
                return table[name]
        return None

    def kindOf(self, name):
        symbol = self.getSymbol(name)
        if(symbol is not None):
            return symbol.kind
        return None

    def typeOf(self, name):
        return self.getSymbol(name).thetype

    def indexOf(self, name):
        return self.getSymbol(name).index

class Symbol:
    def __init__(self, name, thetype, kind, index):
        self.name = name
        self.thetype = thetype
        self.kind = kind
        self.index = index

