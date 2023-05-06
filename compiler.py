# 詞彙語法描述
"""
OP = '+' | '-' | '*' | '/' | '<'
VALUE = [0-9]+
NAME = [a-zA-Z_][a-zA-Z0-9_]*
"""

# 簡易運算式語法
"""
E = F (OP E)*
F = '(' E ')' | VALUE | NAME
"""

# 包含 while 的語法
"""
STMT = ASSIGN | WHILE | BLOCK | PRINT
ASSIGN = NAME '=' E ';'
WHILE = 'while' '(' E ')' STMT
BLOCK = '{' STMT* '}'
PRINT = 'print' E ';'
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

# EBNF 函式
OP = {
    "+": "ADD",
    "-": "SUB",
    "*": "MUL",
    "/": "DIV",
    "<": "LT"
}

def F():
    if isNext("("):
        next()
        i = E()
        next()
    else:
        i = nextTemp()
        item = next()

        if item.isnumeric():
            f.write(f"PUSH, {item}\nSTORE, t{i}\n")
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

def ASSIGN():
    name = next()
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
    e = E()
    skip(";")
    f.write(f"LOAD, t{e}\nPRINT\n")

def STMT():
    if isNext("while"):
        WHILE()
    elif isNext("{"):
        BLOCK()
    elif isNext("print"):
        PRINT()
    else:
        ASSIGN()

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
    f = open(sys.argv[1], "r")
    tokens = re.findall("\w+|[\+\-\*\/\<\=\(\)\{\}\;]", "".join(f.readlines()))
    f.close()

    # 寫入目的檔
    f = open(sys.argv[1].split(".")[0] + ".vm", "w+")
    STMTS()
    f.write("HALT\n")
    f.seek(0)

    # 執行虛擬機
    vm = StackVM()
    vm.load(f)
    vm.run()
