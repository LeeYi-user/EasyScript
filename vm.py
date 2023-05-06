class StackVM:
    def __init__(self):
        self.code = []
        self.stack = []
        self.variable = {}

    def load(self, f):
        for i in f:
            i = i.split(",")

            for j in i:
                j = j.strip()

                if j.isnumeric():
                    j = int(j)

                self.code.append(j)

        f.close()

    def run(self):
        i = 0

        while True:
            op = self.code[i]

            # 存取變數
            if op == "PUSH":
                i += 1
                self.stack.append(self.code[i])
            elif op == "STORE":
                i += 1
                name = self.code[i]
                value = self.stack.pop()
                self.variable[name] = value
            elif op == "LOAD":
                i += 1
                name = self.code[i]
                value = self.variable[name]
                self.stack.append(value)
            elif op == "PRINT":
                print(self.stack.pop())

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

            # 跳躍指令
            elif op[0] == "(" and op[-1] == ")":
                pass
            elif op == "JMP":
                i = self.code.index(f"({self.code[i + 1]})") - 1
            elif op == "JZ":
                i += 1
                if not self.stack.pop():
                    i = self.code.index(f"({self.code[i]})") - 1

            # 中斷執行
            elif op == "HALT":
                break
            else:
                raise Exception(f"Invalid opcode: {op}")

            i += 1
