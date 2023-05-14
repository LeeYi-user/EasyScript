# 初始化
import sys

# 虛擬機
class StackVM:
    def __init__(self):
        self.code = []
        self.stack = []
        self.variable = [{}]

    def load(self, f):
        for i in f:
            i = i.split(",")

            for j in i:
                j = j.strip()

                if j == "":
                    continue

                if j.isnumeric():
                    j = int(j)

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
            elif op == "GT":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a > b)

            # 跳躍指令
            elif op[0] == "(" and op[-1] == ")":
                pass
            elif op == "JMP":
                pc = self.code.index(f"({self.code[pc + 1]})") - 1
            elif op == "JZ":
                pc += 1
                if not self.stack.pop():
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
            elif op == "RETURN":
                pc = self.variable[br]["pc"]
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
    f = open(sys.argv[1], "r")

    # 執行虛擬機
    vm = StackVM()
    vm.load(f)
    vm.run()
