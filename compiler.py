# 詞彙語法描述
"""
OP = '+' | '-' | '*' | '/' | '<' | '>'
NUMBER = [0-9]+ ('.' [0-9]+)?
NONE = None
BOOL = 'True' | 'False'
STRING = '\'' .* '\'' | '\"' .* '\"'
NAME = [a-zA-Z_][a-zA-Z0-9_]*
"""

# 簡易運算式語法
"""
C = E (',' C)?
D = NAME (',' D)?
E = F (OP E)*
F = '(' E ')' | NUMBER | NONE | BOOL | STRING | 'input' '(' E ')' | NAME | NAME '(' C? ')'
"""

# 包含 while 的語法
"""
STMT = ASSIGN | WHILE | BLOCK | PRINT | FUNCTION | RETURN | CALL
ASSIGN = NAME '=' E ';'
WHILE = 'while' '(' E ')' STMT
BLOCK = '{' STMT* '}'
PRINT = 'print' '(' C ')' ';'
FUNCTION = 'function' NAME '(' D? ')' BLOCK
RETURN = 'return' E? ';'
CALL = NAME '(' C? ')' ';'
"""

# 初始化
import re, sys
from vm import StackVM

tempIdx = 0
labelIdx = 0
tokenIdx = 0

def nextTemp():
    global tempIdx
    idx = tempIdx
    tempIdx += 1
    return idx

def nextLabel():
    global labelIdx
    idx = labelIdx
    labelIdx += 1
    return idx

def next():
    global tokenIdx
    str = tokens[tokenIdx]
    tokenIdx += 1
    return str

def isNext(set):
    for str in set.split(" "):
        if str == tokens[tokenIdx]:
            return True
    else:
        return False

def skip(set):
    if isNext(set):
        return next()
    else:
        raise Exception(f"skip({set}) got {next()} fail!")

def isValue(str):
    try:
        int(str)
        return True
    except:
        try:
            float(str)
            return True
        except:
            if str == "None" or str == "True" or str == "False" or str[0] == "\'" or str[0] == "\"":
                return True
            else:
                return False

# EBNF 函式
OP = {
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
    "<": "LT",
    ">": "GT"
}

def C(flag):
    if not isNext(")"):
        i = E()
        f.write(f"LOAD, t{i}\n")

        if flag:
            f.write("PRINT\nPUSH, \" \"\nPRINT\n")

        if isNext(","):
            skip(",")
            C(flag)
        elif flag:
            f.write("PUSH, \"\\n\"\nPRINT\n")

def D():
    if not isNext(")"):
        i = next()

        if isNext(","):
            skip(",")
            D()

        f.write(f"STORE, {i}\n")

def F():
    if isNext("("):
        next()
        i = E()
        next()
    else:
        i = nextTemp()
        item = next()

        if isValue(item):
            f.write(f"PUSH, {item}\nSTORE, t{i}\n")
        elif item == "input":
            skip("(")
            f.write(f"LOAD, t{E()}\nINPUT\nSTORE, t{i}\n")
            skip(")")
        else:
            if isNext("("):
                skip("(")
                C(False)
                skip(")")
                f.write(f"CALL, {item}\nSTORE, t{i}\n")
            else:
                f.write(f"LOAD, {item}\nSTORE, t{i}\n")

    return i

def E():
    i1 = F()

    while isNext(" ".join(list(OP.keys()))):
        op = next()
        i2 = E()
        i = nextTemp()
        f.write(f"LOAD, t{i1}\nLOAD, t{i2}\n{OP[op]}\nSTORE, t{i}\n")
        i1 = i

    return i1

def ASSIGN(name):
    skip("=")
    e = E()
    skip(";")
    f.write(f"LOAD, t{e}\nSTORE, {name}\n")

def WHILE():
    whileBegin = nextLabel()
    whileEnd = nextLabel()
    f.write(f"(L{whileBegin})\n")
    skip("while")
    skip("(")
    e = E()
    skip(")")
    f.write(f"LOAD, t{e}\n")
    f.write(f"JZ, L{whileEnd}\n")
    STMT()
    f.write(f"JMP, L{whileBegin}\n")
    f.write(f"(L{whileEnd})\n")

def BLOCK():
    skip("{")
    STMTS()
    skip("}")

def PRINT():
    skip("print")
    skip("(")
    C(True)
    skip(")")
    skip(";")

def FUNCTION():
    skip("function")
    name = next()
    f.write(f"DEF, ({name})\nSTORE, ra\n")
    skip("(")
    D()
    skip(")")
    BLOCK()
    f.write("PUSH, None\nEND\n")

def RETURN():
    skip("return")

    if isNext(";"):
        f.write(f"PUSH, None\nRETURN\n")
    else:
        f.write(f"LOAD, t{E()}\nRETURN\n")

    skip(";")

def CALL(name):
    skip("(")
    C(False)
    skip(")")
    skip(";")
    f.write(f"CALL, {name}\nPOP\n")

def STMT():
    if isNext("while"):
        WHILE()
    elif isNext("{"):
        BLOCK()
    elif isNext("print"):
        PRINT()
    elif isNext("function"):
        FUNCTION()
    elif isNext("return"):
        RETURN()
    else:
        name = next()

        if isNext("("):
            CALL(name)
        else:
            ASSIGN(name)

def STMTS():
    while tokenIdx < len(tokens) and not isNext("}"):
        STMT()

# 主程式
if __name__ == "__main__":
    # 確認是否有提供參數
    if len(sys.argv) != 2:
        print("請提供一個參數")
        sys.exit()

    # 讀取來源檔
    f = open(sys.argv[1], "r", encoding = "utf-8")
    tokens = re.findall("\d+\.\d+|\'.+?\'|\".+?\"|\w+|[\+\-\*\/\<\>\=\,\(\)\{\}\;]", "".join(f.readlines()))
    f.close()

    # 寫入目的檔
    f = open(sys.argv[1].split(".")[0] + ".vm", "w+", encoding = "utf-8")
    STMTS()
    f.write("HALT\n")
    f.seek(0)

    # 執行虛擬機
    vm = StackVM()
    vm.load(f)
    vm.run()
