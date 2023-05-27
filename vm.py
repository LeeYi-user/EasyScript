# 初始化
import re, sys

# 變數
class Value:
    def __init__(self, data, flag = None):
        if flag is not None:
            try:
                data = int(data)
            except:
                try:
                    data = float(data)
                except:
                    if data == "None":
                        data = None
                    elif data == "True":
                        data = True
                    elif data == "False":
                        data = False
                    elif flag == "PUSH":
                        data = data.strip(data[0])

        self.data = data

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data)
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data)
        return out

    def __pow__(self, other):
        assert isinstance(other, (int, float)), "only supporting int/float powers for now"
        out = Value(self.data**other)
        return out

    def __lt__(self, other):
        if isinstance(other, Value):
            out = Value(self.data < other.data)
        else:
            out = (self.data < other)

        return out

    def __gt__(self, other):
        if isinstance(other, Value):
            out = Value(self.data > other.data)
        else:
            out = (self.data > other)

        return out

    def __eq__(self, other):
        if isinstance(other, Value):
            out = Value(self.data == other.data)
        else:
            out = (self.data == other)

        return out

    def __neg__(self):
        return self * -1

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return self * other**-1

    def __rtruediv__(self, other):
        return other * self**-1

    def __repr__(self):
        return str(self.data)

# 虛擬機
class StackVM:
    def __init__(self):
        self.code = []
        self.stack = []
        self.variable = [{}]

    def load(self, f):
        for i in f:
            lexeme = ["\(.+?\)", "\'.+?\'", "\".+?\"", "\w+"]
            i = re.findall("|".join(lexeme), i)

            for j in i:
                if len(self.code) > 0 and self.code[-1] == "PUSH":
                    j = Value(j, "PUSH")

                self.code.append(j)

        f.close()

    def run(self):
        pc = 0
        br = 0

        while True:
            op = self.code[pc]

            # 存取變數
            if op == "PUSH":
                pc += 1
                self.stack.append(self.code[pc])
            elif op == "POP":
                self.stack.pop()
            elif op == "STORE":
                pc += 1
                name = self.code[pc]
                value = self.stack.pop()
                self.variable[br][name] = value
            elif op == "LOAD":
                pc += 1
                name = self.code[pc]
                value = self.variable[br][name]
                self.stack.append(value)
            elif op == "INPUT":
                data = input(self.stack.pop().data)
                self.stack.append(Value(data, "INPUT"))
            elif op == "PRINT":
                print(str(self.stack.pop().data).replace(r"\n", "\n"), end = "")

            # 簡易運算
            elif op == "ADD":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif op == "SUB":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == "MUL":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == "DIV":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)
            elif op == "LT":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a < b)
            elif op == "GT":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a > b)
            elif op == "EQ":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a == b)

            # 跳躍指令
            elif op[0] == "(" and op[-1] == ")":
                pass
            elif op == "JMP":
                pc = self.code.index(f"({self.code[pc + 1]})") - 1
            elif op == "JZ":
                pc += 1
                if not self.stack.pop().data:
                    pc = self.code.index(f"({self.code[pc]})") - 1

            # 函式指令
            elif op == "DEF":
                while self.code[pc] != "END":
                    pc += 1
            elif op == "CALL":
                pc += 1
                br += 1
                self.stack.append(pc)
                self.variable.append({})
                pc = self.code.index(f"({self.code[pc]})") - 1
            elif op == "RETURN" or op == "END":
                pc = self.variable[br]["ra"]
                self.variable.pop()
                br -= 1

            # 中斷執行
            elif op == "HALT":
                break
            else:
                raise Exception(f"Invalid opcode: {op}")

            pc += 1

# 主程式
if __name__ == "__main__":
    # 確認是否有提供參數
    if len(sys.argv) != 2:
        print("請提供一個參數")
        sys.exit()

    # 讀取來源檔
    f = open(sys.argv[1], "r", encoding = "utf-8")

    # 執行虛擬機
    vm = StackVM()
    vm.load(f)
    vm.run()
